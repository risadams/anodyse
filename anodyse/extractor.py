"""Annotation extractor for Ansible playbooks and roles."""

from .models import PlaybookData, RoleData


def extract(
    data: PlaybookData | RoleData,
    source_text: str,
) -> PlaybookData | RoleData:
    """Extract @ annotations from source_text and populate dataclass fields.

    Supported tags:
      @title        single value → data.title
      @description  single value → data.description
      @param        repeatable, format "<name>: <description>" → data.params
      @warning      repeatable → data.warnings
      @example      repeatable → data.examples
      @tag          repeatable → data.doc_tags

    If @title or @description is absent, set the field to None.
    Do NOT infer or generate missing values.
    Emit AnnotationWarning when @title or @description is absent.

    Args:
        data: PlaybookData or RoleData instance with unpopulated annotation fields
        source_text: Raw YAML text containing comments with @-annotations

    Returns:
        Updated dataclass instance with annotations populated

    Emits:
        AnnotationWarning when mandatory annotations are missing
    """
    raise NotImplementedError("extract() not yet implemented")
