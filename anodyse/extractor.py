"""Annotation extractor for Ansible playbooks and roles."""

import re
import warnings

from .exceptions import AnnotationWarning
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
    # Reset repeatable fields to avoid accumulation on repeated calls
    data.params = []
    data.warnings = []
    data.examples = []
    data.doc_tags = []

    # Extract all annotation lines
    annotations = _parse_annotations(source_text)

    # Process @title (single value)
    if "title" in annotations:
        data.title = annotations["title"][0]
    else:
        data.title = None
        warnings.warn(
            "Missing @title annotation (document remains undocumented)",
            AnnotationWarning,
            stacklevel=2,
        )

    # Process @description (single value)
    if "description" in annotations:
        data.description = annotations["description"][0]
    else:
        data.description = None
        warnings.warn(
            "Missing @description annotation (document remains undocumented)",
            AnnotationWarning,
            stacklevel=2,
        )

    # Process @param (repeatable)
    if "param" in annotations:
        for param_str in annotations["param"]:
            # Format: <name>: <description>
            if ":" in param_str:
                name, description = param_str.split(":", 1)
                data.params.append(
                    {
                        "name": name.strip(),
                        "description": description.strip(),
                    }
                )

    # Process @warning (repeatable)
    if "warning" in annotations:
        data.warnings = annotations["warning"]

    # Process @example (repeatable)
    if "example" in annotations:
        data.examples = annotations["example"]

    # Process @tag (repeatable)
    if "tag" in annotations:
        data.doc_tags = annotations["tag"]

    return data


def _parse_annotations(source_text: str) -> dict[str, list[str]]:
    """Parse @-annotations from YAML comment text.

    Looks for patterns: # @<tag> <value>

    Args:
        source_text: Raw YAML text

    Returns:
        Dictionary mapping tag names to lists of values
    """
    annotations: dict[str, list[str]] = {}

    # Process each line to extract annotations
    lines = source_text.split("\n")
    for line in lines:
        # Look for comment lines with @-tags
        match = re.search(r"#\s*@(\w+)\s+(.+?)$", line)
        if match:
            tag = match.group(1)
            value = match.group(2).strip()

            if tag not in annotations:
                annotations[tag] = []

            annotations[tag].append(value)

    return annotations
