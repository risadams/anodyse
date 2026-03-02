# Template Variables Contract Delta (Feature 002)

**Base Contract**: `specs/001-core-pipeline/contracts/template-variables.md`  
**Feature**: `002-task-comments-todos`  
**Date**: 2026-03-02

This contract defines additive variables and behavior used by `playbook.md.j2`, `role.md.j2`, and `index.md.j2` for task-level comments and TODO rendering.

## `TaskData` additions

Available in task loops (`data.tasks`, `data.pre_tasks`, `data.post_tasks`, `data.handlers`):

| Field | Type | Default | Description |
|---|---|---|---|
| `task.description` | `str \| None` | `None` | From `@task.description:` annotation.
| `task.notes` | `list[str]` | `[]` | From repeatable `@task.note:`.
| `task.warnings` | `list[str]` | `[]` | From repeatable `@task.warning:`.
| `task.tags` | `list[str]` | `[]` | From repeatable `@task.tag:`.
| `task.block_comment` | `str \| None` | `None` | Aggregated prose block comment attached to task.
| `task.inline_comment` | `str \| None` | `None` | Prose inline comment from first-key line.
| `task.todos` | `list[TodoItem]` | `[]` | Structured TODO/FIXME extracted from block comments only.

## `TodoItem` (new)

| Field | Type | Description |
|---|---|---|
| `todo.text` | `str` | TODO/FIXME message body.
| `todo.author` | `str \| None` | Optional author from `TODO(<author>)`, preserved exactly.
| `todo.source` | `"task" \| "file"` | Provenance marker.

## `PlaybookData` additions

| Field | Type | Default | Description |
|---|---|---|---|
| `data.todos` | `list[TodoItem]` | `[]` | File-header TODO/FIXME items for playbook.

## `RoleData` additions

| Field | Type | Default | Description |
|---|---|---|---|
| `data.todos` | `list[TodoItem]` | `[]` | File-header TODO/FIXME items for role.

## `IndexEntry` additions

| Field | Type | Default | Description |
|---|---|---|---|
| `entry.has_todos` | `bool` | `False` | `True` when total structured TODO items > 0.
| `entry.todo_count` | `int` | `0` | `len(data.todos) + sum(len(task.todos) for task in data.tasks)`.

## Rendering behavior requirements

### Task Summary

- If no task-level content exists on any task, render legacy flat list.
- If any task-level content exists, render table columns:
  - `#`, `Task`, `Description`, `Notes`, `Warnings`, `Tags`
- Description fallback order:
  1. `task.description`
  2. `task.block_comment`
  3. empty
- `task.inline_comment` is rendered beneath its row (italic text), not in table cells.

### TODO Section

- Render section only when at least one structured TODO exists across:
  - `data.todos` (file-level)
  - all `task.todos` (task-level)
- Table columns: `Location`, `Author`, `TODO`
- Location mapping:
  - `data.todos` -> `File`
  - `task.todos` -> `Task: <task.name>`
- Author mapping:
  - `todo.author` string when set
  - `—` when `None`

### Index

- Add `TODOs` column.
- Prefix Title with `⚠️` when `entry.has_todos` is true.
- TODO cell shows `entry.todo_count`; show `—` when zero.
- Warning indicator links to TODO section anchor in target document.

## Non-goals in template contract

- Inline TODO-looking prose does not create `TodoItem` rows.
- No new CLI flags or template lookup behavior changes.
