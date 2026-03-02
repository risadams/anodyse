"""Shared utilities for comment classification, TODO parsing, and slugification."""

from __future__ import annotations

import re
from typing import Literal

from .models import TodoItem

_TASK_ANNOTATION_RE = re.compile(r"^\s*@task\.(description|note|warning|tag):\s+.+$")
_TODO_RE = re.compile(
    r"^\s*(TODO|FIXME)(?:\(([^)]+)\))?(?::|\s)\s*(.+?)\s*$",
    re.IGNORECASE,
)


def classify_comment(line: str) -> Literal["annotation", "todo", "prose"]:
    """Classify a comment line as annotation, todo, or prose.

    Expects the comment content WITHOUT the leading `#`.

    Priority order is strict:
      1. `@task.<tag>: <value>` => "annotation"
      2. TODO/FIXME patterns => "todo"
      3. everything else => "prose"
    """
    if _TASK_ANNOTATION_RE.match(line):
        return "annotation"
    if _TODO_RE.match(line):
        return "todo"
    return "prose"


def parse_todo(line: str) -> TodoItem | None:
    """Parse a TODO/FIXME comment into a TodoItem.

    Expects the comment content WITHOUT the leading `#`.

    Supports case-insensitive variants:
      - `TODO: <text>`
      - `TODO(<author>): <text>`
      - `TODO <text>`
      - `FIXME: <text>`
      - `FIXME(<author>): <text>`
      - `FIXME <text>`

    Returns `None` when input does not match a TODO/FIXME pattern.
    """
    match = _TODO_RE.match(line)
    if not match:
        return None

    author = match.group(2)
    text = (match.group(3) or "").strip()
    if not text:
        return None

    return TodoItem(text=text, author=author, source="task")


def slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    slug = text.lower()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug or "untitled"
