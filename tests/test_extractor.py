"""Unit tests for the annotation extractor module."""

import warnings

import pytest

from anodyse.exceptions import AnnotationWarning
from anodyse.extractor import extract
from anodyse.models import PlaybookData
from anodyse.parser import parse_playbook, parse_role


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


class TestExtractPlaybook:
    """Tests for extract function with playbook data."""

    def test_extract_full_annotations(self, playbook_annotated_path):
        """Test extraction of fully annotated playbook."""
        data = parse_playbook(playbook_annotated_path)
        source = open(playbook_annotated_path).read()

        result = extract(data, source)

        assert result.title is not None
        assert result.description is not None
        assert len(result.params) > 0
        assert len(result.warnings) > 0
        assert len(result.examples) > 0
        assert len(result.doc_tags) > 0

    def test_extract_partial_annotations(self, playbook_unannotated_path):
        """Test extraction with missing annotations emits warnings."""
        data = parse_playbook(playbook_unannotated_path)
        source = open(playbook_unannotated_path).read()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = extract(data, source)

            # Should emit at least 2 warnings (missing title and description)
            ann_warnings = [x for x in w if issubclass(x.category, AnnotationWarning)]
            assert len(ann_warnings) >= 2

        assert result.title is None
        assert result.description is None

    def test_extract_no_annotations(self, playbook_unannotated_path):
        """Test extraction with no annotations."""
        data = parse_playbook(playbook_unannotated_path)
        source = "---\n- hosts: all\n  tasks:\n    - name: test\n      debug: msg='test'"

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = extract(data, source)

        assert result.title is None
        assert result.description is None
        assert len(result.params) == 0
        assert len(result.warnings) == 0

    def test_extract_param_repeatable(self):
        """Test @param annotation is repeatable."""
        data = PlaybookData(
            source_path="test.yml",
            title=None,
            description=None,
            hosts="all",
        )

        source = """# @param env: Environment name
# @param version: App version
# @param timeout: Timeout in seconds
---
- hosts: all
"""

        result = extract(data, source)

        assert len(result.params) == 3
        assert result.params[0]["name"] == "env"
        assert result.params[1]["name"] == "version"
        assert result.params[2]["name"] == "timeout"

    def test_extract_tag_repeatable(self):
        """Test @tag annotation is repeatable."""
        data = PlaybookData(
            source_path="test.yml",
            title=None,
            description=None,
            hosts="all",
        )

        source = """# @tag deploy
# @tag production
# @tag critical
---
- hosts: all
"""

        result = extract(data, source)

        assert len(result.doc_tags) == 3
        assert "deploy" in result.doc_tags
        assert "production" in result.doc_tags
        assert "critical" in result.doc_tags


class TestExtractTaskAnnotations:
    """Tests for task-level annotation extraction (T012)."""

    @pytest.fixture
    def playbook_task_annotated_path(self):
        """Path to task-annotated playbook fixture."""
        return "tests/fixtures/playbook_task_annotated.yml"

    def test_extract_task_annotation_class_a(self, playbook_task_annotated_path):
        """Test extraction of Class A task annotations (@task.description|note|warning|tag)."""
        data = parse_playbook(playbook_task_annotated_path)
        source = open(playbook_task_annotated_path).read()

        result = extract(data, source)

        # Task 0 has @task annotations
        task0 = result.tasks[0]
        assert task0.description is not None, (
            "Task 0 should have description from @task.description"
        )
        assert len(task0.notes) > 0, "Task 0 should have notes from @task.note"
        assert len(task0.warnings) > 0, "Task 0 should have warnings from @task.warning"
        # Tags might be in task.tags or doc_tags depending on implementation
        # For now, just check that at least one is populated
        assert len(task0.tags) > 0, "Task 0 should have tags from @task.tag"

    def test_extract_task_no_cross_contamination_between_tasks(self, playbook_task_annotated_path):
        """Test that task annotations don't bleed across task boundaries."""
        data = parse_playbook(playbook_task_annotated_path)
        source = open(playbook_task_annotated_path).read()

        result = extract(data, source)

        # Task 0 has annotations
        task0 = result.tasks[0]
        assert task0.description is not None

        # Task 3 is unannotated - should not inherit task 0's annotations
        task3 = result.tasks[3]
        # Task 3 might have fallback description from task name, but should not have
        # the same description, notes, or warnings as task 0
        assert task3.description != task0.description, (
            "Task 3 should not inherit task 0's description"
        )
        assert len(task3.notes) == 0, "Task 3 should not inherit task 0's notes"
        assert len(task3.warnings) == 0, "Task 3 should not inherit task 0's warnings"


class TestExtractTaskProse:
    """Tests for task prose comment extraction (T020)."""

    @pytest.fixture
    def playbook_task_annotated_path(self):
        """Path to task-annotated playbook fixture."""
        return "tests/fixtures/playbook_task_annotated.yml"

    def test_extract_task_prose_block(self, playbook_task_annotated_path):
        """Test extraction of block prose comments into task.block_comment."""
        data = parse_playbook(playbook_task_annotated_path)
        source = open(playbook_task_annotated_path).read()

        result = extract(data, source)

        # Task 1 has prose block comment
        task1 = result.tasks[1]
        assert task1.block_comment is not None, "Task 1 should have block_comment from prose"
        assert len(task1.block_comment) > 0

        # Task 0 has annotations and shouldn't have block_comment in it
        task0 = result.tasks[0]
        if task0.block_comment:
            # Should not contain annotation syntax
            assert "@task." not in task0.block_comment, (
                "block_comment should not contain annotation syntax"
            )

    def test_extract_task_inline_comment(self, playbook_task_annotated_path):
        """Test extraction of inline prose comments into task.inline_comment."""
        data = parse_playbook(playbook_task_annotated_path)
        source = open(playbook_task_annotated_path).read()

        result = extract(data, source)

        # Task 0 has inline comment
        task0 = result.tasks[0]
        assert task0.inline_comment is not None, "Task 0 should have inline_comment"
        assert len(task0.inline_comment) > 0

        # Task 2 has inline comment
        task2 = result.tasks[2]
        assert task2.inline_comment is not None, "Task 2 should have inline_comment"
        assert len(task2.inline_comment) > 0

        # Task 3 has no inline comment
        task3 = result.tasks[3]
        assert task3.inline_comment is None or len(task3.inline_comment) == 0, (
            "Task 3 should not have inline_comment"
        )


class TestExtractTodos:
    """Tests for TODO/FIXME extraction (T027)."""

    @pytest.fixture
    def playbook_task_annotated_path(self):
        """Path to task-annotated playbook fixture."""
        return "tests/fixtures/playbook_task_annotated.yml"

    def test_extract_task_todo_in_block(self, playbook_task_annotated_path):
        """Test extraction of TODO/FIXME from task block comments."""
        data = parse_playbook(playbook_task_annotated_path)
        source = open(playbook_task_annotated_path).read()

        result = extract(data, source)

        # Task 0 has TODO in block comments
        task0 = result.tasks[0]
        assert len(task0.todos) > 0, "Task 0 should have TODOs from block comments"

        # Check that TODO has source="task"
        for todo in task0.todos:
            assert todo.source == "task", "Block TODOs should have source='task'"

    def test_extract_task_inline_todo_is_prose_not_structured(self, playbook_task_annotated_path):
        """Test that inline TODOs are prose, not structured TodoItems."""
        data = parse_playbook(playbook_task_annotated_path)
        source = open(playbook_task_annotated_path).read()

        result = extract(data, source)

        # Task 2 has inline comment (which might contain TODO text)
        # But inline comments should never create structured TodoItems
        task2 = result.tasks[2]

        # If task 2 has inline_comment, it should be preserved as prose
        if task2.inline_comment:
            # Even if it contains "TODO", it should not be in task2.todos
            assert len(task2.todos) == 0, "Inline TODOs should not create structured TodoItems"

    def test_extract_file_level_todo_source_is_file(self, playbook_task_annotated_path):
        """Test that file-level TODOs have source='file'."""
        data = parse_playbook(playbook_task_annotated_path)
        source = open(playbook_task_annotated_path).read()

        result = extract(data, source)

        # File has TODO/FIXME comments at the top
        if len(result.todos) > 0:
            for todo in result.todos:
                assert todo.source == "file", "File-level TODOs should have source='file'"

    def test_extract_no_todos_empty_list(self):
        """Test that tasks without TODOs have empty todos list."""
        # Create minimal playbook data
        from pathlib import Path

        from anodyse.models import PlaybookData, TaskData

        task = TaskData(name="Test", module="command", args={})
        data = PlaybookData(
            source_path=Path("test.yml"),
            title=None,
            description=None,
            hosts="localhost",
            tasks=[task],
        )

        result = extract(data, "# No TODOs here\n- hosts: localhost")

        assert len(result.tasks[0].todos) == 0, "Task without TODOs should have empty todos list"
        assert len(result.todos) == 0, "Playbook without TODOs should have empty todos list"


class TestExtractRole:
    """Tests for extract function with role data."""

    def test_extract_role_annotated(self, role_sample_path):
        """Test extraction from annotated role."""
        data = parse_role(role_sample_path)
        source = open(f"{role_sample_path}/tasks/main.yml").read()

        result = extract(data, source)

        assert result.title is not None
        assert result.description is not None
        assert len(result.warnings) > 0


if __name__ == "__main__":
    pytest.main([__file__])
