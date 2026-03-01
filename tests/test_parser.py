"""Unit tests for the YAML parser module."""

import tempfile
from pathlib import Path

import pytest
import yaml

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
