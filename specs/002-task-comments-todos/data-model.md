# Data Model: Task-Level Annotations, Plain Comments & TODO Detection

**Feature**: `002-task-comments-todos`  
**Date**: 2026-03-02

## Overview

This feature extends existing 001 dataclasses with task-level comment capture and TODO tracking while preserving backward compatibility for all existing constructors and render paths.

## Entities

### TodoItem (new)

Represents one extracted TODO/FIXME item.

- **Fields**:
  - `text: str` — TODO body (required, non-empty after trim)
  - `author: str | None` — optional author from `TODO(<author>)`
  - `source: Literal["task", "file"]` — origin marker
- **Validation**:
  - `text` must not be empty
  - `source` must be one of `task`, `file`

### TaskData (extended)

Existing fields preserved: `name`, `module`, `args`.

New optional fields:
- `description: str | None = None`
- `notes: list[str] = field(default_factory=list)`
- `warnings: list[str] = field(default_factory=list)`
- `tags: list[str] = field(default_factory=list)`
- `block_comment: str | None = None`
- `inline_comment: str | None = None`
- `todos: list[TodoItem] = field(default_factory=list)`

Rules:
- `description` prefers `@task.description` only.
- `block_comment` is prose-only aggregation from attached block comments.
- `inline_comment` is prose-only from first-key inline comment.
- `todos` only includes structured block-comment TODO/FIXME entries for the task.

### PlaybookData (extended)

Add:
- `todos: list[TodoItem] = field(default_factory=list)`

Rules:
- Stores file-header TODO/FIXME items only.
- All entries in this list must have `source="file"`.

### RoleData (extended)

Add:
- `todos: list[TodoItem] = field(default_factory=list)`

Rules:
- Stores role-level file-header TODO/FIXME items only.
- All entries in this list must have `source="file"`.

### IndexEntry (extended)

Add:
- `has_todos: bool = False`
- `todo_count: int = 0`

Rules:
- `has_todos` is true when `todo_count > 0`.
- `todo_count = len(data.todos) + sum(len(task.todos) for task in data.tasks)`.
- Inline TODO-looking prose is excluded (not structured TODO).

## Relationships

- `PlaybookData.tasks[*] -> TaskData`
- `RoleData.tasks[*] -> TaskData`
- `TaskData.todos[*] -> TodoItem(source="task")`
- `PlaybookData.todos[*] -> TodoItem(source="file")`
- `RoleData.todos[*] -> TodoItem(source="file")`
- `IndexEntry` summarizes TODO totals from playbook/role models.

## State Transitions

### Task comment lifecycle

1. **Parsed**: parser provides `block_comments[]` + `inline_comment?` (raw strings).
2. **Classified**:
   - `@task.*:` -> structured annotation fields.
   - TODO/FIXME (block only) -> `TaskData.todos`.
   - Other -> prose (`block_comment`, `inline_comment`).
3. **Rendered**:
   - Table description uses `description` else `block_comment` fallback.
   - `inline_comment` rendered under row.
   - Task TODOs rendered in TODO section only.

### File-level TODO lifecycle

1. **Parsed/Extracted**: file-header comments scanned post file-level annotation extraction.
2. **Converted**: TODO/FIXME lines become `TodoItem(source="file")`.
3. **Rendered/Indexed**: displayed in TODO table with `Location=File`; counted in `todo_count`.

## Backward Compatibility

- New fields all default to `None` or empty list.
- Existing call sites constructing 001 models remain valid.
- Existing docs output unchanged when no task-level content exists.
