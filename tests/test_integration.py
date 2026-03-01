"""Integration tests for the full Anodyse pipeline."""

import tempfile
from pathlib import Path

import pytest

from anodyse.discovery import discover
from anodyse.extractor import extract
from anodyse.models import IndexEntry
from anodyse.output import write_output
from anodyse.parser import detect_type, parse_playbook, parse_role
from anodyse.renderer import render_index, render_playbook


@pytest.fixture
def playbook_annotated_path():
    """Path to annotated playbook fixture."""
    return Path("tests/fixtures/playbook_annotated.yml")


@pytest.fixture
def role_sample_path():
    """Path to role sample fixture."""
    return Path("tests/fixtures/role_sample")


@pytest.fixture
def output_dir():
    """Create a temporary output directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestFullPipeline:
    """Integration tests for the full pipeline."""

    def test_pipeline_annotated_playbook(self, playbook_annotated_path, output_dir):
        """Test full pipeline with annotated playbook."""
        # Step 1: Discover
        results = discover(str(playbook_annotated_path.parent))
        assert len(results) > 0

        # Step 2: Detect type
        item_type = detect_type(str(playbook_annotated_path))
        assert item_type == "playbook"

        # Step 3: Parse
        data = parse_playbook(str(playbook_annotated_path))
        assert data is not None
        assert data.hosts == "webservers"

        # Step 4: Extract annotations
        source = playbook_annotated_path.read_text()
        data = extract(data, source)
        assert data.title is not None
        assert data.description is not None

        # Step 5: Render
        rendered = render_playbook(data)
        assert isinstance(rendered, str)
        assert len(rendered) > 0
        assert data.title in rendered

        # Step 6: Write output
        output_path = output_dir / "deploy.md"
        write_output(rendered, str(output_path))

        # Verify file was created
        assert output_path.exists()
        assert output_path.read_text() == rendered

    def test_pipeline_role(self, role_sample_path, output_dir):
        """Test full pipeline with role."""
        # Step 1: Detect type
        item_type = detect_type(str(role_sample_path))
        assert item_type == "role"

        # Step 2: Parse
        data = parse_role(str(role_sample_path))
        assert data is not None
        assert len(data.tasks) > 0

        # Step 3: Extract annotations
        source = (role_sample_path / "tasks" / "main.yml").read_text()
        data = extract(data, source)
        assert data.title is not None

        # Step 4: Render
        from anodyse.renderer import render_role

        rendered = render_role(data)
        assert isinstance(rendered, str)
        assert len(rendered) > 0

        # Step 5: Write output
        output_path = output_dir / "webserver.md"
        write_output(rendered, str(output_path))
        assert output_path.exists()

    def test_pipeline_with_index(self, playbook_annotated_path, role_sample_path, output_dir):
        """Test full pipeline including index generation."""
        entries = []

        # Process playbook
        playbook_data = parse_playbook(str(playbook_annotated_path))
        source = playbook_annotated_path.read_text()
        playbook_data = extract(playbook_data, source)

        entry1 = IndexEntry(
            title=playbook_data.title or "Untitled",
            source_path=playbook_annotated_path,
            output_filename="deploy.md",
            description=playbook_data.description,
            doc_tags=playbook_data.doc_tags,
            item_type="playbook",
        )
        entries.append(entry1)

        # Process role
        role_data = parse_role(str(role_sample_path))
        source = (role_sample_path / "tasks" / "main.yml").read_text()
        role_data = extract(role_data, source)

        entry2 = IndexEntry(
            title=role_data.title or "Untitled",
            source_path=role_sample_path,
            output_filename="webserver.md",
            description=role_data.description,
            doc_tags=role_data.doc_tags,
            item_type="role",
        )
        entries.append(entry2)

        # Render index
        index_content = render_index(entries)
        assert isinstance(index_content, str)
        assert len(entries) >= 2

        # Write index
        index_path = output_dir / "index.md"
        write_output(index_content, str(index_path))
        assert index_path.exists()

        # Verify index contains entry titles
        index_text = index_path.read_text()
        assert entry1.title in index_text or entry2.title in index_text

    def test_pipeline_mermaid_diagram(self, playbook_annotated_path):
        """Test pipeline with Mermaid diagram enabled."""
        # Parse and extract
        data = parse_playbook(str(playbook_annotated_path))
        source = playbook_annotated_path.read_text()
        data = extract(data, source)

        # Render with graph=True
        rendered = render_playbook(data, graph=True)

        # Should contain mermaid block
        assert "mermaid" in rendered.lower() or "graph" in rendered.lower()

    def test_pipeline_backup_files(self, playbook_annotated_path, output_dir):
        """Test that backup files are created on overwrite."""
        output_path = output_dir / "test.md"

        # First write
        write_output("First version", str(output_path))
        assert output_path.exists()

        # Second write (should create backup)
        write_output("Second version", str(output_path), no_backup=False)

        # Check that backup was created
        backup_path = output_path.with_suffix(".md.bak")
        assert backup_path.exists()
        assert backup_path.read_text() == "First version"

    def test_pipeline_no_backup_flag(self, output_dir):
        """Test that no_backup flag skips backup creation."""
        output_path = output_dir / "test.md"

        # First write
        write_output("First version", str(output_path))

        # Second write with no_backup=True
        write_output("Second version", str(output_path), no_backup=True)

        # Backup should NOT exist
        backup_path = output_path.with_suffix(".md.bak")
        assert not backup_path.exists()
        assert output_path.read_text() == "Second version"

    def test_pipeline_filename_slugification(self, output_dir):
        """Test that filenames are properly slugified."""
        output_path = output_dir / "My Fancy Playbook (v1.0).md"

        write_output("Content", str(output_path))

        # Should be slugified
        files = list(output_dir.glob("*.md"))
        assert len(files) == 1

        # Filename should be slugified (lowercase, no special chars)
        filename = files[0].name
        assert filename.islower()
        assert "(" not in filename
        assert ")" not in filename
        assert " " not in filename


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
