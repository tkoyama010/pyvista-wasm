"""Tests for the README i18n drift-detection script."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "tools" / "check_readme_i18n.py"


def _load_module():
    """Load the check_readme_i18n module from the tools directory."""
    spec = importlib.util.spec_from_file_location("check_readme_i18n", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_readme_i18n"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    """Provide the check_readme_i18n module for testing."""
    return _load_module()


class TestExtractHeadingLevels:
    """Tests for extract_heading_levels."""

    def test_basic_headings(self, mod, tmp_path):
        """Heading levels are extracted in document order."""
        f = tmp_path / "test.md"
        f.write_text("# Title\n\n## Section\n\n### Sub\n", encoding="utf-8")
        assert mod.extract_heading_levels(f) == [1, 2, 3]

    def test_ignores_code_blocks(self, mod, tmp_path):
        """Lines inside fenced code blocks are not parsed as headings."""
        f = tmp_path / "test.md"
        f.write_text(
            "# Title\n\n```bash\n# this is a comment\n```\n\n## Section\n",
            encoding="utf-8",
        )
        assert mod.extract_heading_levels(f) == [1, 2]

    def test_empty_file(self, mod, tmp_path):
        """An empty file yields no headings."""
        f = tmp_path / "empty.md"
        f.write_text("", encoding="utf-8")
        assert mod.extract_heading_levels(f) == []


class TestCheckStructuralParity:
    """Tests for check_structural_parity."""

    def test_matching_structure(self, mod):
        """No errors when heading levels match exactly."""
        errors = mod.check_structural_parity([1, 2, 2], [1, 2, 2], Path("README.ja.md"))
        assert errors == []

    def test_count_mismatch(self, mod):
        """A heading count difference is reported."""
        errors = mod.check_structural_parity([1, 2, 2], [1, 2], Path("README.ja.md"))
        assert len(errors) == 1
        assert "heading count mismatch" in errors[0]

    def test_level_mismatch(self, mod):
        """A heading level difference is reported with position."""
        errors = mod.check_structural_parity([1, 2, 2], [1, 3, 2], Path("README.ja.md"))
        assert len(errors) == 1
        assert "heading 2 level mismatch" in errors[0]


class TestCheckStaleTranslation:
    """Tests for check_stale_translation."""

    def test_stale(self, mod):
        """A translation older than the English README is flagged."""
        errors = mod.check_stale_translation(100, 50, Path("README.ja.md"), set())
        assert len(errors) == 1
        assert "stale" in errors[0]

    def test_not_stale(self, mod):
        """A translation newer than the English README is not flagged."""
        errors = mod.check_stale_translation(50, 100, Path("README.ja.md"), set())
        assert errors == []

    def test_allowlisted(self, mod):
        """An allowlisted file is not flagged even when stale."""
        errors = mod.check_stale_translation(100, 50, Path("README.ja.md"), {"README.ja.md"})
        assert errors == []

    def test_none_epochs(self, mod):
        """None epochs produce no errors."""
        assert mod.check_stale_translation(None, 50, Path("README.ja.md"), set()) == []
        assert mod.check_stale_translation(100, None, Path("README.ja.md"), set()) == []


class TestFindLocalizedReadmes:
    """Tests for find_localized_readmes."""

    def test_finds_localized_only(self, mod, tmp_path):
        """Only README.<lang>.md files are returned, not README.md."""
        (tmp_path / "README.md").write_text("# Test", encoding="utf-8")
        (tmp_path / "README.ja.md").write_text("# Test", encoding="utf-8")
        (tmp_path / "README.zh_CN.md").write_text("# Test", encoding="utf-8")
        (tmp_path / "CONTRIBUTING.md").write_text("# Test", encoding="utf-8")
        result = mod.find_localized_readmes(tmp_path)
        names = [p.name for p in result]
        assert names == ["README.ja.md", "README.zh_CN.md"]


class TestLoadAllowlist:
    """Tests for load_allowlist."""

    def test_loads_entries(self, mod, tmp_path):
        """Non-comment, non-empty lines are loaded as allowlist entries."""
        f = tmp_path / "allowlist"
        f.write_text("README.ja.md\n# comment\nREADME.es.md\n\n", encoding="utf-8")
        assert mod.load_allowlist(f) == {"README.ja.md", "README.es.md"}

    def test_none_path(self, mod):
        """A None path returns an empty set."""
        assert mod.load_allowlist(None) == set()

    def test_nonexistent_path(self, mod, tmp_path):
        """A nonexistent path returns an empty set."""
        assert mod.load_allowlist(tmp_path / "nonexistent") == set()


class TestMainIntegration:
    """Integration tests for the main function."""

    def test_pass_on_matching_structure(self, mod, tmp_path):
        """Exit code 0 when localized README matches English structure."""
        (tmp_path / "README.md").write_text(
            "# Title\n\n## Section\n\n## Another\n",
            encoding="utf-8",
        )
        (tmp_path / "README.ja.md").write_text(
            "# Title\n\n## Section\n\n## Another\n",
            encoding="utf-8",
        )
        rc = mod.main(["--repo-root", str(tmp_path), "--no-stale-check"])
        assert rc == 0

    def test_fail_on_structural_drift(self, mod, tmp_path):
        """Exit code 1 when localized README has different heading count."""
        (tmp_path / "README.md").write_text(
            "# Title\n\n## Section\n\n## Another\n",
            encoding="utf-8",
        )
        (tmp_path / "README.ja.md").write_text(
            "# Title\n\n## Section\n",
            encoding="utf-8",
        )
        rc = mod.main(["--repo-root", str(tmp_path), "--no-stale-check"])
        assert rc == 1

    def test_no_localized_readmes(self, mod, tmp_path):
        """Exit code 0 when no localized READMEs exist."""
        (tmp_path / "README.md").write_text("# Title\n", encoding="utf-8")
        rc = mod.main(["--repo-root", str(tmp_path), "--no-stale-check"])
        assert rc == 0
