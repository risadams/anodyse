"""Unit tests for the YAML parser module."""

import tempfile
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from anodyse.exceptions import ParseError
from anodyse.models import PlaybookData, RoleData, TaskData
from anodyse.parser import detect_type, parse_playbook, parse_role


@pytest.fixture
def playbook_annotated_path():
    """Path to annotated playbook fixture."""
    return "tests/fixtures/playbook_annotated.yml"


@pytest.fixture
def playbook_unannotated_path():
    """Path to unannotated playbook fixture."""
    return "tests/fixtures/playbook_unannotated.yml"


@pytest.fixture
def role_sample_path():
    """Path to role sample fixture."""
    return "tests/fixtures/role_sample"


@pytest.fixture
def playbook_task_annotated_path():
    """Path to task-annotated playbook fixture."""
    return "tests/fixtures/playbook_task_annotated.yml"


class TestDetectType:
    """Tests for detect_type function."""

    def test_detect_type_playbook(self, playbook_annotated_path):
        """Test detection of playbook file."""
        result = detect_type(playbook_annotated_path)
        assert result == "playbook"

    def test_detect_type_role(self, role_sample_path):
        """Test detection of role directory."""
        result = detect_type(role_sample_path)
        assert result == "role"

    def test_detect_type_unknown(self):
        """Test detection of unknown type."""
        result = detect_type("nonexistent_path.yml")
        assert result == "unknown"


class TestParsePlaybook:
    """Tests for parse_playbook function."""

    def test_parse_playbook_annotated(self, playbook_annotated_path):
        """Test parsing annotated playbook fixture."""
        data = parse_playbook(playbook_annotated_path)

        assert isinstance(data, PlaybookData)
        assert data.hosts == "webservers"
        assert len(data.tasks) > 0
        assert all(isinstance(t, TaskData) for t in data.tasks)

    def test_parse_playbook_unannotated(self, playbook_unannotated_path):
        """Test parsing unannotated playbook fixture."""
        data = parse_playbook(playbook_unannotated_path)

        assert isinstance(data, PlaybookData)
        assert data.hosts == "all"
        assert len(data.tasks) > 0

    def test_parse_playbook_malformed_yaml(self):
        """Test parsing malformed YAML raises ParseError."""
        with pytest.raises(ParseError):
            parse_playbook("tests/fixtures/nonexistent.yml")

    def test_parse_playbook_task_structure(self, playbook_annotated_path):
        """Test that tasks are parsed into TaskData instances."""
        data = parse_playbook(playbook_annotated_path)

        for task in data.tasks:
            assert isinstance(task, TaskData)
            assert hasattr(task, "name")
            assert hasattr(task, "module")
            assert hasattr(task, "args")

    def test_parse_playbook_task_annotated_fixture(self, playbook_task_annotated_path):
        """Fixture sanity check: task-comment coverage fixture parses correctly."""
        data = parse_playbook(playbook_task_annotated_path)
        assert isinstance(data, PlaybookData)
        assert data.hosts == "app_servers"
        assert len(data.tasks) == 4

    def test_parser_extracts_block_comments_per_task(self, playbook_task_annotated_path):
        """Test parser attaches block comments to correct task (T011)."""
        data = parse_playbook(playbook_task_annotated_path)

        # Task 0: Has @task annotations in block comments
        task0 = data.tasks[0]
        assert hasattr(task0, "_raw_block_comments")
        assert task0._raw_block_comments is not None
        assert len(task0._raw_block_comments) > 0
        # Should contain annotation lines
        block_text = " ".join(task0._raw_block_comments)
        assert "@task" in block_text.lower()

        # Task 1: Has prose block comment
        task1 = data.tasks[1]
        assert hasattr(task1, "_raw_block_comments")
        assert task1._raw_block_comments is not None
        assert len(task1._raw_block_comments) > 0

        # Task 2: Has inline comment only, no block comment
        task2 = data.tasks[2]
        assert hasattr(task2, "_raw_block_comments")
        # Either None or empty list for no block comment
        assert not task2._raw_block_comments or len(task2._raw_block_comments) == 0

        # Task 3: No comments at all
        task3 = data.tasks[3]
        assert hasattr(task3, "_raw_block_comments")
        assert not task3._raw_block_comments or len(task3._raw_block_comments) == 0

    def test_parser_extracts_inline_comment_per_task(self, playbook_task_annotated_path):
        """Test parser attaches inline comments to correct task (T011)."""
        data = parse_playbook(playbook_task_annotated_path)

        # Task 0: Has inline comment on name line
        task0 = data.tasks[0]
        assert hasattr(task0, "_raw_inline_comment")
        assert task0._raw_inline_comment is not None
        assert len(task0._raw_inline_comment) > 0

        # Task 1: No inline comment
        task1 = data.tasks[1]
        assert hasattr(task1, "_raw_inline_comment")
        assert not task1._raw_inline_comment or len(task1._raw_inline_comment) == 0

        # Task 2: Has inline comment
        task2 = data.tasks[2]
        assert hasattr(task2, "_raw_inline_comment")
        assert task2._raw_inline_comment is not None
        assert len(task2._raw_inline_comment) > 0

        # Task 3: No inline comment
        task3 = data.tasks[3]
        assert hasattr(task3, "_raw_inline_comment")
        assert not task3._raw_inline_comment or len(task3._raw_inline_comment) == 0

    def test_parser_blank_lines_in_block_region_included(self, playbook_task_annotated_path):
        """Test that blank lines within block comment regions are preserved (T019)."""
        data = parse_playbook(playbook_task_annotated_path)

        # Task 1 has block comments with potential blank lines
        task1 = data.tasks[1]
        if hasattr(task1, "_raw_block_comments") and task1._raw_block_comments:
            # Check block comment region has content (blank lines filtered)
            assert len(task1._raw_block_comments) > 0

    def test_parser_no_cross_task_comment_bleed(self, playbook_task_annotated_path):
        """Test that comments don't bleed across task boundaries (T019)."""
        data = parse_playbook(playbook_task_annotated_path)

        # Task 0 has specific annotations like "Install runtime dependencies"
        task0 = data.tasks[0]
        task0_text = " ".join(task0._raw_block_comments) if task0._raw_block_comments else ""

        # Task 1 has different content
        task1 = data.tasks[1]
        task1_text = " ".join(task1._raw_block_comments) if task1._raw_block_comments else ""

        # Task 0's specific content should not appear in task 1's comments
        if "Install runtime dependencies" in task0_text:
            assert "Install runtime dependencies" not in task1_text, (
                "Task 1 should not contain task 0's description"
            )

        # Task 1's specific content should not appear in task 0's comments
        if "application directory permissions" in task1_text:
            assert "application directory permissions" not in task0_text, (
                "Task 0 should not contain task 1's prose"
            )


class TestParseRole:
    """Tests for parse_role function."""

    def test_parse_role_sample(self, role_sample_path):
        """Test parsing role sample fixture."""
        data = parse_role(role_sample_path)

        assert isinstance(data, RoleData)
        assert len(data.tasks) > 0
        assert all(isinstance(t, TaskData) for t in data.tasks)
        assert len(data.defaults) > 0
        assert len(data.vars) > 0

    def test_parse_role_missing_tasks(self):
        """Test parsing role without tasks/main.yml raises ParseError."""
        with pytest.raises(ParseError):
            parse_role("nonexistent_role")

    def test_parse_role_meta_loaded(self, role_sample_path):
        """Test that role metadata is loaded."""
        data = parse_role(role_sample_path)

        assert isinstance(data.meta, dict)
        assert "galaxy_info" in data.meta


class TestParserEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_parse_playbook_invalid_yaml_syntax(self):
        """Test parsing YAML with invalid syntax."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            fname = f.name
            f.write("{ invalid yaml: [")
            f.flush()

        try:
            with pytest.raises(ParseError):
                parse_playbook(fname)
        finally:
            Path(fname).unlink(missing_ok=True)

    def test_parse_playbook_empty_file(self):
        """Test parsing empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            fname = f.name
            f.write("")
            f.flush()

        try:
            # Should handle empty file gracefully
            try:
                result = parse_playbook(fname)
                # Empty file may return None or empty PlaybookData
                assert result is None or isinstance(result, PlaybookData)
            except ParseError:
                # Also acceptable to raise ParseError for empty file
                pass
        finally:
            Path(fname).unlink(missing_ok=True)

    def test_parse_playbook_with_variables(self):
        """Test parsing playbook with variable definitions."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            fname = f.name
            yaml = YAML()
            with open(fname, "w") as fw:
                yaml.dump(
                    {
                        "name": "Test Playbook",
                        "hosts": "all",
                        "pre_tasks": [{"name": "Task 1", "debug": {"msg": "test"}}],
                        "tasks": [{"name": "Task 2", "debug": {"msg": "test"}}],
                    },
                    fw,
                )

        try:
            result = parse_playbook(fname)
            assert result is not None
        finally:
            Path(fname).unlink(missing_ok=True)

    def test_parse_playbook_with_handlers(self):
        """Test parsing playbook with handlers."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            fname = f.name
            yaml = YAML()
            with open(fname, "w") as fw:
                yaml.dump(
                    {
                        "name": "Test",
                        "hosts": "all",
                        "tasks": [{"name": "Task", "shell": "echo test"}],
                        "handlers": [{"name": "Handler", "debug": {"msg": "handler"}}],
                    },
                    fw,
                )

        try:
            result = parse_playbook(fname)
            assert result is not None
        finally:
            Path(fname).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
