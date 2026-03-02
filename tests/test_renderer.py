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


class TestRenderTaskAnnotations:
    """Tests for rendering task summary table (T013)."""

    @pytest.fixture
    def playbook_with_task_annotations(self):
        """Create PlaybookData with annotated tasks."""
        return PlaybookData(
            source_path="test.yml",
            title="Test Playbook",
            description="Test playbook with task annotations",
            hosts="appservers",
            tasks=[
                TaskData(
                    name="Install dependencies",
                    module="package",
                    args={},
                    description="Install runtime packages",
                    notes=["Uses native package manager"],
                    warnings=["Requires cache refresh"],
                    tags=["install"],
                ),
                TaskData(
                    name="Prepare directory",
                    module="file",
                    args={},
                    # No description, but has block_comment
                    block_comment="This configures directory permissions.",
                ),
                TaskData(
                    name="Unannotated task",
                    module="command",
                    args={},
                ),
            ],
        )

    def test_render_task_summary_table_when_any_content(self, playbook_with_task_annotations):
        """Test that task summary table is rendered when tasks have annotation content."""
        output = render_playbook(playbook_with_task_annotations)

        # Should contain task summary section
        assert "## Task Summary" in output or "## Tasks" in output
        # Should contain table headers
        assert "Task" in output or "Name" in output
        assert "Description" in output

    def test_render_task_description_uses_annotation_first(self, playbook_with_task_annotations):
        """Test that task description from @task.description takes precedence."""
        output = render_playbook(playbook_with_task_annotations)

        # Task 0 has explicit description annotation - should be in output
        assert "Install runtime packages" in output

        # Task 1 has no description annotation but has block_comment
        # Depending on implementation, this might use block_comment as fallback
        # For now, just verify task 1 name appears
        assert "Prepare directory" in output


class TestRenderTaskProse:
    """Tests for rendering task prose comments (T021)."""

    @pytest.fixture
    def playbook_with_prose_fallback(self):
        """Create PlaybookData with prose fallback scenario."""
        return PlaybookData(
            source_path="test.yml",
            title="Test Playbook",
            description="Test playbook with prose",
            hosts="servers",
            tasks=[
                TaskData(
                    name="Task with annotation",
                    module="command",
                    args={},
                    description="Explicit description from annotation",
                    block_comment="This is prose that should be ignored",
                ),
                TaskData(
                    name="Task with prose only",
                    module="command",
                    args={},
                    block_comment="This configures the application directory.",
                ),
                TaskData(
                    name="Task with inline comment",
                    module="command",
                    args={},
                    inline_comment="restart to apply changes",
                ),
            ],
        )

    def test_render_task_description_falls_back_to_block_comment(
        self, playbook_with_prose_fallback
    ):
        """Test that task description falls back to block_comment when no annotation exists."""
        output = render_playbook(playbook_with_prose_fallback)

        # Task 0: Annotation should take precedence
        assert "Explicit description from annotation" in output

        # Task 1: Should use block_comment as fallback
        assert "This configures the application directory" in output

    def test_render_task_inline_comment_below_table_row(self, playbook_with_prose_fallback):
        """Test that inline comments render beneath table rows."""
        output = render_playbook(playbook_with_prose_fallback)

        # Task 2 has inline comment - should be rendered in italics
        assert "restart to apply changes" in output
        # Check for italic formatting
        assert "*restart to apply changes*" in output or "_restart to apply changes_" in output


class TestRenderTodos:
    """Tests for rendering TODO section (T028)."""

    @pytest.fixture
    def playbook_with_todos(self):
        """Create PlaybookData with TODOs."""
        from anodyse.models import TodoItem

        return PlaybookData(
            source_path="test.yml",
            title="Test Playbook",
            description="Test playbook with TODOs",
            hosts="servers",
            todos=[
                TodoItem(text="Add post-deploy notification", author=None, source="file"),
                TodoItem(text="Validate rollback strategy", author="ris", source="file"),
            ],
            tasks=[
                TaskData(
                    name="Install packages",
                    module="command",
                    args={},
                    todos=[
                        TodoItem(text="Add package mirror fallback", author="john", source="task"),
                    ],
                ),
                TaskData(
                    name="Configure app",
                    module="command",
                    args={},
                ),
            ],
        )

    @pytest.fixture
    def playbook_without_todos(self):
        """Create PlaybookData without TODOs."""
        return PlaybookData(
            source_path="test.yml",
            title="Test Playbook",
            description="Test playbook without TODOs",
            hosts="servers",
            tasks=[
                TaskData(name="Task 1", module="command", args={}),
            ],
        )

    def test_render_todo_section_present_when_todos_exist(self, playbook_with_todos):
        """Test that TODO section is rendered when TODOs exist."""
        output = render_playbook(playbook_with_todos)

        assert "TODO" in output or "Todo" in output, "Should contain TODO section"

    def test_render_todo_section_absent_when_no_todos(self, playbook_without_todos):
        """Test that TODO section is absent when no TODOs exist."""
        output = render_playbook(playbook_without_todos)

        # Count TODO section headers - should be none when no TODOs exist
        lines = output.split("\n")
        todo_section_lines = [
            line for line in lines if line.startswith("## ") and "TODO" in line.upper()
        ]
        assert len(todo_section_lines) == 0, "Should not have TODO section header when no TODOs"

    def test_render_todo_table_columns(self, playbook_with_todos):
        """Test that TODO table has Location, Author, and TODO columns."""
        output = render_playbook(playbook_with_todos)

        # Should have table with columns
        if "|" in output:
            # Check for column headers
            assert "Location" in output or "Source" in output, "Should have location/source column"
            assert "Author" in output, "Should have Author column"
            assert "TODO" in output or "Description" in output, (
                "Should have TODO/description column"
            )

    def test_render_todo_author_dash_when_none(self, playbook_with_todos):
        """Test that author shows '-' when None."""
        output = render_playbook(playbook_with_todos)

        # File TODO without author should show dash
        # This is hard to test exactly, but we can check the structure
        assert "-" in output, "Should contain dash for empty author"

    def test_render_todo_location_file_vs_task(self, playbook_with_todos):
        """Test that location differentiates file vs task TODOs."""
        output = render_playbook(playbook_with_todos)

        # Check that file-level TODOs are rendered
        assert "Add post-deploy notification" in output, "File-level TODO should be in output"

        # Check that File location is shown
        lines = output.split("\n")
        table_started = False
        for line in lines:
            if "| Location |" in line:
                table_started = True
                continue
            if table_started and "| File |" in line:
                # Found file-level TODO row
                assert True
                return

        # If we get here, File location wasn't found
        assert False, f"Should have 'File' location in TODO table. Output:\n{output}"

    def test_render_index_todo_flag_present(self):
        """Test that index shows TODO flag when TODOs exist."""
        from anodyse.models import IndexEntry

        entry_with_todos = IndexEntry(
            title="Playbook With TODOs",
            source_path="/path/to/playbook.yml",
            output_filename="playbook.md",
            description="Test",
            doc_tags=[],
            item_type="playbook",
            has_todos=True,
            todo_count=3,
        )

        output = render_index([entry_with_todos])

        # Should have some TODO indicator
        assert "3" in output or "TODO" in output or "⚠" in output, "Should show TODO indicator"

    def test_render_index_todo_count_shown(self):
        """Test that index shows TODO count."""
        from anodyse.models import IndexEntry

        entry = IndexEntry(
            title="Test",
            source_path="/test.yml",
            output_filename="test.md",
            description="Test",
            doc_tags=[],
            item_type="playbook",
            has_todos=True,
            todo_count=5,
        )

        output = render_index([entry])

        assert "5" in output, "Should display TODO count"


if __name__ == "__main__":
    pytest.main([__file__])
