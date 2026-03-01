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
