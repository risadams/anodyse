"""Tests for the CLI module."""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from anodyse.cli import main


@pytest.fixture
def cli_runner():
    """Create a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path("tests/fixtures")


class TestCLI:
    """Tests for the CLI entry point."""

    def test_cli_help(self, cli_runner):
        """Test CLI help output."""
        result = cli_runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Anodyse" in result.output

    def test_cli_single_playbook(self, cli_runner, fixtures_dir):
        """Test CLI with single playbook."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = cli_runner.invoke(
                main,
                [
                    str(fixtures_dir / "playbook_annotated.yml"),
                    "--output",
                    tmpdir,
                ],
            )

            # Should succeed or exit with code 2 (warnings)
            assert result.exit_code in [0, 2]

            # Output directory should have files
            output_files = list(Path(tmpdir).glob("*.md"))
            assert len(output_files) > 0

    def test_cli_directory_discovery(self, cli_runner, fixtures_dir):
        """Test CLI with directory discovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = cli_runner.invoke(
                main,
                [
                    str(fixtures_dir),
                    "--output",
                    tmpdir,
                ],
            )

            # Should succeed or exit with code 2 (warnings)
            assert result.exit_code in [0, 2]

            # Should have generated files
            output_files = list(Path(tmpdir).glob("*.md"))
            assert len(output_files) >= 2  # At least index + 1 item

    def test_cli_with_graph(self, cli_runner, fixtures_dir):
        """Test CLI with Mermaid graph enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = cli_runner.invoke(
                main,
                [
                    str(fixtures_dir / "playbook_annotated.yml"),
                    "--output",
                    tmpdir,
                    "--graph",
                ],
            )

            assert result.exit_code in [0, 2]

            # Generated file should contain mermaid
            md_files = list(Path(tmpdir).glob("*.md"))
            md_content = "\n".join(f.read_text() for f in md_files)
            assert "mermaid" in md_content.lower() or "graph" in md_content.lower()

    def test_cli_with_verbose(self, cli_runner, fixtures_dir):
        """Test CLI with verbose output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = cli_runner.invoke(
                main,
                [
                    str(fixtures_dir / "playbook_annotated.yml"),
                    "--output",
                    tmpdir,
                    "--verbose",
                ],
            )

            assert result.exit_code in [0, 2]
            # Verbose should print additional info
            assert "✓" in result.output or "Processing" in result.output

    def test_cli_nonexistent_path(self, cli_runner):
        """Test CLI with nonexistent path."""
        result = cli_runner.invoke(main, ["/nonexistent/path.yml"])

        # Should fail
        assert result.exit_code != 0

    def test_cli_no_backup_flag(self, cli_runner, fixtures_dir):
        """Test CLI with no-backup flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            # First run
            cli_runner.invoke(
                main,
                [
                    str(fixtures_dir / "playbook_annotated.yml"),
                    "--output",
                    str(output_dir),
                ],
            )

            # Second run with no-backup
            result2 = cli_runner.invoke(
                main,
                [
                    str(fixtures_dir / "playbook_annotated.yml"),
                    "--output",
                    str(output_dir),
                    "--no-backup",
                ],
            )

            assert result2.exit_code in [0, 2]

            # Note: no-backup only affects the second run, not the first
            # So we may or may not have backups depending on implementation

    def test_cli_warnings_exit_code(self, cli_runner, fixtures_dir):
        """Test CLI exit code with warnings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = cli_runner.invoke(
                main,
                [
                    str(fixtures_dir / "playbook_unannotated.yml"),
                    "--output",
                    tmpdir,
                ],
            )

            # Should exit with code 2 due to missing annotations
            assert result.exit_code == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
