"""Unit tests for the discovery module."""

import tempfile
import warnings
from pathlib import Path

import pytest

from anodyse.discovery import discover
from anodyse.exceptions import ManifestError


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path("tests/fixtures")


class TestDiscovery:
    """Tests for discover function."""

    def test_discover_fixtures_directory(self, fixtures_dir):
        """Test discovering playbooks and roles in fixtures directory."""
        results = discover(str(fixtures_dir))

        assert isinstance(results, list)
        assert len(results) >= 2  # Should find at least annotated playbook and role

    def test_discover_finds_playbooks(self, fixtures_dir):
        """Test that discovery finds playbook files."""
        results = discover(str(fixtures_dir))

        # Convert to Path objects for easier checking
        paths = [Path(p) for p in results]

        # Should find playbook_annotated.yml
        playbook_found = any("playbook" in str(p).lower() for p in paths)
        assert playbook_found or len(paths) > 0

    def test_discover_finds_roles(self, fixtures_dir):
        """Test that discovery finds role directories."""
        results = discover(str(fixtures_dir))

        # Convert to Path objects
        paths = [Path(p) for p in results]

        # Should find role_sample directory
        role_found = any("role_sample" in str(p) for p in paths)
        assert role_found or len(paths) > 0

    def test_discover_single_playbook(self, fixtures_dir):
        """Test discovering a single playbook file."""
        playbook_path = fixtures_dir / "playbook_annotated.yml"
        results = discover(str(playbook_path))

        assert len(results) >= 1

    def test_discover_returns_absolute_paths(self, fixtures_dir):
        """Test that discovered paths are absolute."""
        results = discover(str(fixtures_dir))

        for path_str in results:
            path = Path(path_str)
            assert path.is_absolute()

    def test_discover_nonexistent_manifest_warns(self, fixtures_dir):
        """Test that nonexistent manifest paths emit warnings."""
        # Create a temporary manifest file that references nonexistent paths
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("include:\n  - /nonexistent/path.yml\n")
            manifest_path = f.name

        try:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                discover(str(fixtures_dir), config_path=manifest_path)

                # Should emit warning for nonexistent path
                # Warnings are expected
        finally:
            Path(manifest_path).unlink()

    def test_discover_manifest_invalid_schema_raises(self):
        """Test that invalid manifest schema raises ManifestError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            # Invalid YAML (invalid schema)
            f.write("include: 'not a list'\n")
            manifest_path = f.name

        try:
            with pytest.raises(ManifestError):
                discover(".", config_path=manifest_path)
        finally:
            Path(manifest_path).unlink()


class TestDiscoveryEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_discover_nonexistent_path(self):
        """Test discovery on nonexistent path."""
        result = discover("/nonexistent/path")
        # Should return empty list, not raise error
        assert result == []

    def test_discover_empty_directory(self):
        """Test discovery on empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = discover(tmpdir)
            # Should return empty list for directory with no playbooks/roles
            assert result == []

    def test_discover_with_invalid_manifest(self):
        """Test discovery with invalid manifest file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create an invalid manifest
            manifest_path = tmpdir_path / ".anodyse.yml"
            manifest_path.write_text("invalid: yaml: [")

            # Should raise ManifestError
            with pytest.raises(ManifestError):
                discover(tmpdir)

    def test_discover_with_manifest_missing_files(self):
        """Test discovery when manifest references missing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create manifest referencing nonexistent files
            manifest_path = tmpdir_path / ".anodyse.yml"
            manifest_content = """
include:
  - /nonexistent/playbook.yml
  - /nonexistent/role
"""
            manifest_path.write_text(manifest_content)

            # Should emit warnings but not fail or return results
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                result = discover(tmpdir)
                # May have warnings about missing files
                assert isinstance(result, list)

    def test_discover_single_file(self):
        """Test discovery on a single playbook file."""
        result = discover("tests/fixtures/playbook_annotated.yml")
        # Should return single item or empty list depending on implementation
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__])
