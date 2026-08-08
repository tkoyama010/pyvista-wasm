#!/usr/bin/env python3
"""Recursively compare key structure of ja.yml and en.yml.

ja.yml is the authoritative locale for slide structure.  This script
exits non-zero if the key sets of the two locale files differ, naming
the offending keys so the maintainer knows exactly what to add or remove.

See ``docs/decisions/0006-decide-how-to-sync-slide-locale-files.md``
(ADR-0006) for the decision this hook enforces.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

LOCALES_DIR = Path(__file__).resolve().parent
JA_FILE = LOCALES_DIR / "ja.yml"
EN_FILE = LOCALES_DIR / "en.yml"


def collect_keys(node: object, prefix: str = "") -> set[str]:
    """Recursively collect every dotted key path from a YAML mapping."""
    keys: set[str] = set()
    if not isinstance(node, dict):
        return keys
    for key, value in node.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        keys.add(path)
        keys |= collect_keys(value, path)
    return keys


def main() -> int:
    """Run the key-parity check and return the exit code."""
    ja_keys = collect_keys(yaml.safe_load(JA_FILE.read_text(encoding="utf-8")))
    en_keys = collect_keys(yaml.safe_load(EN_FILE.read_text(encoding="utf-8")))

    only_ja = ja_keys - en_keys
    only_en = en_keys - ja_keys

    if not only_ja and not only_en:
        return 0

    if only_ja:
        print("Keys in ja.yml but missing from en.yml:")
        for key in sorted(only_ja):
            print(f"  {key}")
    if only_en:
        print("Keys in en.yml but missing from ja.yml:")
        for key in sorted(only_en):
            print(f"  {key}")
    print(
        "\nja.yml is the authoritative locale for slide structure. "
        "Update en.yml (or ja.yml) so both files share the same key set.",
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
