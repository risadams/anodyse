"""Annotation extractor for Ansible playbooks and roles."""

import re
import warnings

from .exceptions import AnnotationWarning
from .models import PlaybookData, RoleData, TaskData
from .utils import classify_comment, parse_todo


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

    # Extract file-level TODOs (T031)
    data.todos = _extract_file_level_todos(source_text)

    # Process task-level annotations (T016)
    for task in data.tasks:
        extract_task_annotations(task)
    
    if isinstance(data, PlaybookData):
        for task in data.pre_tasks:
            extract_task_annotations(task)
        for task in data.post_tasks:
            extract_task_annotations(task)
        for task in data.handlers:
            extract_task_annotations(task)

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


def _extract_file_level_todos(source_text: str) -> list:
    """Extract TODO/FIXME comments from file header (before first task).

    Returns list of TodoItem instances with source="file".
    """
    from .models import TodoItem
    
    todos = []
    lines = source_text.split("\n")
    
    # Scan lines until we hit the first task (- name:) or play (- hosts:)
    for line in lines:
        stripped = line.strip()
        
        # Stop at first task/play definition
        if stripped.startswith("- name:") or stripped.startswith("- hosts:"):
            break
        
        # Check if it's a comment line
        if stripped.startswith("#"):
            comment_text = stripped[1:].strip()
            
            # Classify and parse if TODO
            comment_type = classify_comment(comment_text)
            if comment_type == "todo":
                todo_item = parse_todo(comment_text)
                if todo_item:
                    # Override source to "file"
                    todos.append(TodoItem(
                        text=todo_item.text,
                        author=todo_item.author,
                        source="file"
                    ))
    
    return todos


def extract_task_annotations(task: TaskData) -> None:
    """Extract task-level annotations from raw block/inline comments.

    Populates TaskData fields from @task.* annotations (Class A):
      - @task.description → task.description
      - @task.note → task.notes (repeatable)
      - @task.warning → task.warnings (repeatable)
      - @task.tag → task.tags (repeatable)

    Also processes:
      - Block prose (non-annotation comments) → task.block_comment
      - Inline comment → task.inline_comment
      - TODO/FIXME in block comments → task.todos with source="task"

    Args:
        task: TaskData instance with _raw_block_comments and _raw_inline_comment attributes
    """
    # Process block comments if they exist
    if hasattr(task, "_raw_block_comments") and task._raw_block_comments:
        block_annotations = {}
        block_prose_lines = []
        
        for line in task._raw_block_comments:
            stripped = line.strip()
            
            # Skip blank lines
            if not stripped:
                continue
            
            # Remove leading # and whitespace
            if stripped.startswith("#"):
                comment_text = stripped[1:].strip()
                
                # Classify the comment
                comment_type = classify_comment(comment_text)
                
                if comment_type == "annotation":
                    # Parse @task.* annotation
                    match = re.match(r"@task\.(\w+)\s*:\s*(.+)", comment_text, re.IGNORECASE)
                    if match:
                        tag = match.group(1).lower()
                        value = match.group(2).strip()
                        
                        if tag not in block_annotations:
                            block_annotations[tag] = []
                        block_annotations[tag].append(value)
                
                elif comment_type == "todo":
                    # Parse TODO/FIXME
                    todo_item = parse_todo(comment_text)
                    if todo_item:
                        task.todos.append(todo_item)
                
                elif comment_type == "prose":
                    # Collect prose lines
                    block_prose_lines.append(comment_text)
        
        # Populate task fields from annotations
        if "description" in block_annotations:
            task.description = block_annotations["description"][0]
        
        if "note" in block_annotations:
            task.notes.extend(block_annotations["note"])
        
        if "warning" in block_annotations:
            task.warnings.extend(block_annotations["warning"])
        
        if "tag" in block_annotations:
            task.tags.extend(block_annotations["tag"])
        
        # Set block_comment from prose lines
        if block_prose_lines:
            task.block_comment = " ".join(block_prose_lines)
    
    # Process inline comment if it exists
    if hasattr(task, "_raw_inline_comment") and task._raw_inline_comment:
        # Inline comments are always prose (never structured)
        task.inline_comment = task._raw_inline_comment
