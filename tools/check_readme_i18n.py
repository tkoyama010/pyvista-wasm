#!/usr/bin/env python3
"""Check README i18n drift: structural parity + stale-translation detection.

Python stdlib only — no third-party runtime dependencies.

Two checks are performed against every ``README.<lang>.md`` at the repo root:

1. **Structural parity** — heading levels (H1-H6) are extracted from
   ``README.md`` and each localized README.  The lists must match in count
   and per-position level.  This catches missing, extra, or restructured
   sections while allowing heading *text* to differ (it is translated).

2. **Stale translation** — the git commit timestamp of each localized README
   is compared against ``README.md``.  If the translation's last commit
   predates the English README's latest change, it is flagged as stale.
   An allowlist file exempts specific files (e.g. cosmetic badge-only changes).

Usage::

    python tools/check_readme_i18n.py [--allowlist FILE] [--no-stale-check]

Exit codes: 0 = pass, 1 = drift detected, 2 = configuration error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


def extract_heading_levels(filepath: Path) -> list[int]:
    """Extract heading levels (1-6) from a Markdown file in document order.

    ATX headings only (``#`` prefix).  Lines inside fenced code blocks
    are skipped so that ``#`` comments in code samples are not mistaken
    for headings.

    Parameters
    ----------
    filepath
        Path to the Markdown file.

    Returns
    -------
    list[int]
        Heading levels in document order.

    """
    levels: list[int] = []
    in_code_block = False
    for line in filepath.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        match = HEADING_RE.match(line)
        if match:
            levels.append(len(match.group(1)))
    return levels


def check_structural_parity(
    en_levels: list[int],
    lang_levels: list[int],
    lang_file: Path,
) -> list[str]:
    """Compare heading structure between the English README and a localized one.

    Parameters
    ----------
    en_levels
        Heading levels from ``README.md``.
    lang_levels
        Heading levels from the localized README.
    lang_file
        Path to the localized README (used for error messages).

    Returns
    -------
    list[str]
        Error messages for each structural mismatch.

    """
    errors: list[str] = []
    if len(en_levels) != len(lang_levels):
        errors.append(
            f"{lang_file.name}: heading count mismatch — "
            f"README.md has {len(en_levels)} headings, "
            f"{lang_file.name} has {len(lang_levels)}",
        )
        return errors
    for i, (en_level, lang_level) in enumerate(
        zip(en_levels, lang_levels, strict=False),
    ):
        if en_level != lang_level:
            errors.append(
                f"{lang_file.name}: heading {i + 1} level mismatch — "
                f"README.md has H{en_level}, {lang_file.name} has H{lang_level}",
            )
    return errors


def get_last_commit_epoch(filepath: Path, repo_root: Path) -> int | None:
    """Get the last commit timestamp (Unix epoch) for a file via git log.

    Parameters
    ----------
    filepath
        Path to the file.
    repo_root
        Repository root for the git command working directory.

    Returns
    -------
    int | None
        Unix epoch timestamp, or ``None`` if git is unavailable or the file
        has no commit history.

    """
    try:
        result = subprocess.run(  # noqa: S603
            [
                "git",
                "log",
                "-1",
                "--format=%ct",
                "--",
                str(filepath.relative_to(repo_root)),
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_root,
        )
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def check_stale_translation(
    en_epoch: int | None,
    lang_epoch: int | None,
    lang_file: Path,
    allowlist: set[str],
) -> list[str]:
    """Flag a localized README whose last commit predates README.md's latest change.

    Parameters
    ----------
    en_epoch
        Last commit epoch of ``README.md``.
    lang_epoch
        Last commit epoch of the localized README.
    lang_file
        Path to the localized README.
    allowlist
        Set of filenames exempt from the stale check.

    Returns
    -------
    list[str]
        Error message if the translation is stale and not allowlisted.

    """
    if en_epoch is None or lang_epoch is None:
        return []
    if lang_epoch < en_epoch and lang_file.name not in allowlist:
        return [
            (
                f"{lang_file.name}: stale translation — "
                f"last commit ({lang_epoch}) predates README.md ({en_epoch}). "
                f"Update {lang_file.name} or add it to the allowlist."
            ),
        ]
    return []


def find_localized_readmes(root: Path) -> list[Path]:
    """Find all ``README.<lang>.md`` files at the repo root (excluding ``README.md``).

    Parameters
    ----------
    root
        Repository root directory.

    Returns
    -------
    list[Path]
        Sorted list of localized README paths.

    """
    return sorted(p for p in root.glob("README.*.md") if p.name != "README.md")


def load_allowlist(path: Path | None) -> set[str]:
    """Load stale-check allowlist entries from a file.

    Parameters
    ----------
    path
        Path to the allowlist file, or ``None``.

    Returns
    -------
    set[str]
        Set of filenames exempt from the stale check.

    """
    if path is None or not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def detect_repo_root(explicit: Path | None) -> Path | None:
    """Determine the repository root, using git if no explicit path is given.

    Parameters
    ----------
    explicit
        Explicitly provided repository root, or ``None`` to auto-detect.

    Returns
    -------
    Path | None
        Resolved repository root, or ``None`` if detection failed.

    """
    if explicit is not None:
        return explicit.resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None
    return Path(result.stdout.strip()).resolve()


def main(argv: list[str] | None = None) -> int:
    """Run the README i18n drift checker.

    Parameters
    ----------
    argv
        Command-line arguments (defaults to ``sys.argv[1:]``).

    Returns
    -------
    int
        Exit code: 0 = pass, 1 = drift, 2 = config error.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=None,
        help="File listing README.<lang>.md names exempt from stale checks (one per line).",
    )
    parser.add_argument(
        "--no-stale-check",
        action="store_true",
        help="Skip the stale-translation (git commit date) check.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (auto-detected via git if omitted).",
    )
    args = parser.parse_args(argv)

    repo_root = detect_repo_root(args.repo_root)
    if repo_root is None:
        print("Error: not a git repository and --repo-root not given.", file=sys.stderr)
        return 2

    en_readme = repo_root / "README.md"
    if not en_readme.exists():
        print(f"Error: {en_readme} not found.", file=sys.stderr)
        return 2

    lang_readmes = find_localized_readmes(repo_root)
    if not lang_readmes:
        print("No localized README.*.md files found — nothing to check.")
        return 0

    allowlist = load_allowlist(args.allowlist)
    en_levels = extract_heading_levels(en_readme)
    all_errors: list[str] = []

    en_epoch: int | None = None
    if not args.no_stale_check:
        en_epoch = get_last_commit_epoch(en_readme, repo_root)

    for lang_file in lang_readmes:
        lang_levels = extract_heading_levels(lang_file)
        all_errors.extend(check_structural_parity(en_levels, lang_levels, lang_file))
        if not args.no_stale_check:
            lang_epoch = get_last_commit_epoch(lang_file, repo_root)
            all_errors.extend(
                check_stale_translation(en_epoch, lang_epoch, lang_file, allowlist),
            )

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        print(f"\n{len(all_errors)} drift issue(s) found.", file=sys.stderr)
        return 1

    print(f"All {len(lang_readmes)} localized README(s) pass structural parity and stale checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
