"""Unit tests for the Markdown renderer module."""

import pytest

from anodyse.models import IndexEntry, PlaybookData, RoleData, TaskData
from anodyse.renderer import render_index, render_playbook, render_role


@pytest.fixture
def sample_playbook_data():
    """Create sample PlaybookData for testing."""
    return PlaybookData(
        source_path="test.yml",
        title="Test Playbook",
        description="A test playbook for deployment",
        hosts="webservers",
        tasks=[
            TaskData(name="Install packages", module="package", args={}),
            TaskData(name="Start service", module="systemd", args={}),
        ],
        params=[{"name": "env", "description": "Environment name"}],
        warnings=["Backup before running"],
        examples=["anodyse test.yml"],
        doc_tags=["deploy"],
    )


@pytest.fixture
def sample_role_data():
    """Create sample RoleData for testing."""
    return RoleData(
        source_path="roles/webserver",
        title="Webserver Role",
        description="Configures web server",
        tasks=[
            TaskData(name="Install nginx", module="package", args={}),
        ],
        params=[{"name": "nginx_version", "description": "Nginx version"}],
        warnings=["Requires firewall rule"],
        examples=["role: webserver"],
        doc_tags=["webserver"],
        meta={"galaxy_info": {"author": "test"}},
    )


@pytest.fixture
def sample_entries():
    """Create sample IndexEntry instances."""
    return [
        IndexEntry(
            title="Deploy App",
            source_path="/path/to/deploy.yml",
            output_filename="deploy-app.md",
            description="Deployment playbook",
            doc_tags=["deploy"],
            item_type="playbook",
        ),
        IndexEntry(
            title="Webserver Role",
            source_path="/path/to/roles/webserver",
            output_filename="webserver.md",
            description="Configures web server",
            doc_tags=["webserver"],
            item_type="role",
        ),
    ]


class TestRenderPlaybook:
    """Tests for render_playbook function."""

    def test_render_playbook_basic(self, sample_playbook_data):
        """Test basic playbook rendering."""
        output = render_playbook(sample_playbook_data)

        assert isinstance(output, str)
        assert "Test Playbook" in output
        assert "A test playbook for deployment" in output
        assert "webservers" in output

    def test_render_playbook_contains_sections(self, sample_playbook_data):
        """Test that required sections are present."""
        output = render_playbook(sample_playbook_data)

        # Check for required sections
        assert "Overview" in output or "Parameters" in output
        assert "Tasks" in output or "task" in output.lower()

    def test_render_playbook_parameters(self, sample_playbook_data):
        """Test that parameters are rendered."""
        output = render_playbook(sample_playbook_data)

        assert "env" in output or "Parameter" in output

    def test_render_playbook_warnings(self, sample_playbook_data):
        """Test that warnings are rendered."""
        output = render_playbook(sample_playbook_data)

        assert "Backup before running" in output or "Warning" in output.lower()

    def test_render_playbook_mermaid_on(self, sample_playbook_data):
        """Test Mermaid diagram is included when graph=True."""
        output = render_playbook(sample_playbook_data, graph=True)

        assert "mermaid" in output.lower() or "graph" in output.lower()

    def test_render_playbook_mermaid_off(self, sample_playbook_data):
        """Test Mermaid diagram is excluded when graph=False."""
        output = render_playbook(sample_playbook_data, graph=False)

        # Mermaid block should not be present
        assert "```mermaid" not in output

    def test_render_playbook_undocumented(self):
        """Test rendering with missing description."""
        data = PlaybookData(
            source_path="test.yml",
            title="Test",
            description=None,  # Undocumented
            hosts="all",
        )

        output = render_playbook(data)

        assert "undocumented" in output.lower() or "⚠️" in output


class TestRenderRole:
    """Tests for render_role function."""

    def test_render_role_basic(self, sample_role_data):
        """Test basic role rendering."""
        output = render_role(sample_role_data)

        assert isinstance(output, str)
        assert "Webserver Role" in output
        assert "Configures web server" in output

    def test_render_role_parameters(self, sample_role_data):
        """Test that role parameters are rendered."""
        output = render_role(sample_role_data)

        assert "nginx_version" in output or "Parameter" in output

    def test_render_role_mermaid_on(self, sample_role_data):
        """Test Mermaid diagram included when graph=True."""
        output = render_role(sample_role_data, graph=True)

        assert "mermaid" in output.lower() or "graph" in output.lower()


class TestRenderIndex:
    """Tests for render_index function."""

    def test_render_index_basic(self, sample_entries):
        """Test basic index rendering."""
        output = render_index(sample_entries)

        assert isinstance(output, str)
        assert "index" in output.lower() or "Table" in output or "|" in output

    def test_render_index_entries(self, sample_entries):
        """Test that all entries are in the index."""
        output = render_index(sample_entries)

        assert "Deploy App" in output
        assert "Webserver Role" in output

    def test_render_index_table_format(self, sample_entries):
        """Test that index uses table format."""
        output = render_index(sample_entries)

        # Should contain table markers
        assert "|" in output

    def test_render_index_empty(self):
        """Test rendering empty index."""
        output = render_index([])

        assert isinstance(output, str)


if __name__ == "__main__":
    pytest.main([__file__])
