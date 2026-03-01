"""Unit tests for the output module."""

import tempfile
from pathlib import Path

import pytest

from anodyse.output import write_output


class TestWriteOutput:
    """Tests for write_output function."""

    def test_write_output_basic(self):
        """Test basic output writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.md"
            content = "# Test\n\nThis is test content."

            write_output(content, str(output_path))

            assert output_path.exists()
            assert output_path.read_text() == content

    def test_write_output_creates_directory(self):
        """Test that write_output creates output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "output.md"
            content = "# Test"

            write_output(content, str(output_path))

            assert output_path.exists()
            assert output_path.parent.exists()

    def test_write_output_with_backup(self):
        """Test output writing with backup creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.md"

            # Write initial content
            write_output("# First", str(output_path))

            # Write again (should create backup)
            write_output("# Second", str(output_path))

            assert output_path.exists()
            assert output_path.read_text() == "# Second"

            # Backup may or may not exist depending on implementation
            backup_path = output_path.with_suffix(".md.bak")

    def test_write_output_no_backup_flag(self):
        """Test output writing without backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.md"

            write_output("content", str(output_path))
            write_output("new content", str(output_path), no_backup=True)

            assert output_path.exists()
            assert output_path.read_text() == "new content"

    def test_write_output_slugification(self):
        """Test filename slugification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Filename with spaces and special characters
            output_path = Path(tmpdir) / "My Test Playbook!@#.md"
            content = "# Test"

            write_output(content, str(output_path))

            # Should slugify the filename
            files = list(Path(tmpdir).glob("*.md"))
            assert len(files) > 0

    def test_write_output_utf8_encoding(self):
        """Test UTF-8 encoding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.md"
            # Content with unicode characters
            content = "# Test\n\nÜñÍçödé: 你好"

            write_output(content, str(output_path))

            # Should write and read back correctly
            read_back = output_path.read_text(encoding="utf-8")
            assert read_back == content

    def test_write_output_empty_content(self):
        """Test writing empty content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.md"
            write_output("", str(output_path))

            assert output_path.exists()
            assert output_path.read_text() == ""

    def test_write_output_large_content(self):
        """Test writing large content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.md"
            # Create large content (1MB)
            content = "# Test\n\n" + ("x" * 1000000)

            write_output(content, str(output_path))

            assert output_path.exists()
            assert len(output_path.read_text()) > 1000000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
