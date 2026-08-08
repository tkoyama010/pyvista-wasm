"""Check JA/EN slide locale files share the same key structure.

Standalone script for pre-commit.ci — depends only on PyYAML, not on the
pyvista_wasm package itself.  Mirrors the ``check-locale-parity`` CLI
subcommand; see ADR-0006 for the decision this enforces.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def _collect_keys(node: object, prefix: str = "") -> set[str]:
    """Recursively collect every dotted key path from a YAML mapping."""
    keys: set[str] = set()
    if not isinstance(node, dict):
        return keys
    for key, value in node.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        keys.add(path)
        keys |= _collect_keys(value, path)
    return keys


def main() -> None:
    """Parse locale file paths and fail if their key structures differ."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ja", type=Path, default=Path("slides/locales/ja.yml"))
    parser.add_argument("--en", type=Path, default=Path("slides/locales/en.yml"))
    args = parser.parse_args()

    ja_keys = _collect_keys(yaml.safe_load(args.ja.read_text(encoding="utf-8")))
    en_keys = _collect_keys(yaml.safe_load(args.en.read_text(encoding="utf-8")))

    only_ja = ja_keys - en_keys
    only_en = en_keys - ja_keys

    if not only_ja and not only_en:
        return

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
    sys.exit(1)


if __name__ == "__main__":
    main()
