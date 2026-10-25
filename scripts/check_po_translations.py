"""Check that ja translation catalogs do not regress below their baseline.

Implements a ratchet: each ``.po`` catalog must keep a translation ratio
(translated msgids / total msgids) at or above the ratio recorded in the
baseline file. Raise a catalog's translation and regenerate the baseline
(``--update``) to lower the bar permanently; a regression fails the check.

Usage::

    python scripts/check_po_translations.py --baseline docs/locale/ja/translation-baseline.json
    python scripts/check_po_translations.py --baseline ... --update  # refresh baseline

"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LocaleDir = "docs/locale/ja/LC_MESSAGES"


def parse_po(path: Path) -> tuple[int, int]:
    """Return (translated, total) msgid counts for a .po file.

    Entries are ``msgid`` blocks each followed by a ``msgstr`` block; both
    may span multiple quoted continuation lines. Obsolete (``#~``) entries
    and the header entry are ignored. Fuzzy entries count as untranslated.
    """
    translated = 0
    total = 0

    entries = _entries(path.read_text(encoding="utf-8"))
    for index, entry in enumerate(entries):
        if index == 0 and entry["msgid"] == '""':
            continue  # catalog header
        total += 1
        if entry["msgstr"]:
            translated += 1
    return translated, total


def _entries(text: str) -> list[dict[str, object]]:
    """Split po text into entries with a ``msgstr`` flag.

    An entry's flags (``#, fuzzy`` / ``#~``) always precede its ``msgid``
    line, so they are snapshotted when the ``msgid`` is seen and the
    accumulation resets for the next entry.
    """
    entries: list[dict[str, object]] = []
    flags = {"fuzzy": False, "obsolete": False}
    pending: dict[str, object] | None = None
    section = ""
    msgstr_empty = True

    def close() -> None:
        nonlocal pending, msgstr_empty, section
        if pending is not None:
            pending["msgstr"] = not msgstr_empty and not (pending["fuzzy"] or pending["obsolete"])
            entries.append(pending)
        pending = None
        msgstr_empty = True
        section = ""

    for raw in (*text.splitlines(), 'msgid ""'):
        line = raw.strip()
        if line.startswith("#,") and "fuzzy" in line:
            flags["fuzzy"] = True
        elif line.startswith("#~"):
            flags["obsolete"] = True
        elif line.startswith("msgid "):
            close()
            pending = {
                "fuzzy": flags["fuzzy"],
                "obsolete": flags["obsolete"],
                "msgid": line[len("msgid ") :].strip(),
            }
            flags = {"fuzzy": False, "obsolete": False}
            section = "msgid"
        elif line.startswith("msgstr "):
            section = "msgstr"
            content = line[len("msgstr ") :].strip()
            msgstr_empty = content in ('""', "")
        elif line.startswith('"'):
            msgstr_empty = msgstr_empty and not (section == "msgstr" and line != '""')

    return entries


def ratios(locale_dir: Path) -> dict[str, float]:
    """Compute the translation ratio for every .po under ``locale_dir``."""
    result: dict[str, float] = {}
    for po in sorted(locale_dir.rglob("*.po")):
        translated, total = parse_po(po)
        if total == 0:
            continue
        result[str(po.relative_to(locale_dir))] = translated / total
    return result


def main() -> int:
    """Run the check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path(LocaleDir).parent / "translation-baseline.json",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="rewrite the baseline with current ratios instead of checking",
    )
    args = parser.parse_args()

    locale_dir = Path(LocaleDir)
    current = ratios(locale_dir)

    if args.update:
        args.baseline.write_text(
            json.dumps(
                dict(sorted(current.items())),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        print(f"Baseline updated: {len(current)} catalogs")
        return 0

    if not args.baseline.exists():
        print(f"::error::Baseline file not found: {args.baseline}")
        return 1

    baseline: dict[str, float] = json.loads(args.baseline.read_text())
    regressions = 0
    for name, ratio in sorted(current.items()):
        if name not in baseline:
            # New catalog: must be fully translated.
            if ratio < 1.0:
                print(
                    f"::error::New catalog {name} is {ratio:.0%} translated; "
                    "translate it fully or run the check with --update deliberately",
                )
                regressions += 1
            continue
        floor = baseline[name]
        if ratio < floor - 1e-9:
            print(
                f"::error::{name} is {ratio:.0%} translated, below the "
                f"baseline {floor:.0%} — translate the new strings and commit "
                "the catalog",
            )
            regressions += 1

    # Baselines for removed catalogs are stale; flag them so the baseline
    # shrinks back.
    for name in baseline:
        if name not in current:
            print(f"::warning::Baseline entry {name} no longer exists — rerun --update")
    if regressions:
        print(
            f"Translation regression in {regressions} catalog(s). "
            "Run `python scripts/check_po_translations.py --update` only when "
            "lowering the bar deliberately.",
        )
        return 1
    print(f"Translation ratchet OK: {len(current)} catalogs at or above baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
