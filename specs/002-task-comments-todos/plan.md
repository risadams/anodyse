# Implementation Plan: Task-Level Annotations, Plain Comments & TODO Detection

**Branch**: `002-task-comments-todos` | **Date**: 2026-03-02 | **Spec**: `specs/002-task-comments-todos/spec.md`
**Input**: Feature specification from `specs/002-task-comments-todos/spec.md`

## Summary

Add task-level comment awareness to Anodyse by extending parser + extractor + renderer with three comment classes (structured `@task.*`, prose, TODO/FIXME), plus file-level TODO detection and index TODO flags/counts, while preserving MVP behavior when no task-level content exists.

This implementation is additive and must preserve all existing file-level annotation behavior and CLI semantics.

Planning decisions locked for implementation:
- Task annotation syntax is colon-required: `# @task.<tag>: <value>`.
- `TodoItem.source` supports `"task" | "file"`.
- Inline TODO/FIXME remains prose (never structured TODO item).
- `todo_count` counts structured TODO items only (file-level + task-level block TODOs), excluding inline TODO prose.
- Blank lines are permitted in attached block comment regions until interrupted by non-comment, non-blank content.
- TODO author text is preserved exactly as authored.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `click`, `ruamel.yaml`, `jinja2`  
**Storage**: N/A (filesystem input/output only)  
**Testing**: `pytest`  
**Target Platform**: Cross-platform CLI (Windows/Linux/macOS)  
**Project Type**: Single-package CLI/library (`anodyse`)  
**Performance Goals**: Maintain current pipeline responsiveness; fixture pipeline test remains within existing test-time envelope  
**Constraints**: Offline-only; no external API calls; no source YAML mutation; no secrets/hostnames leaked in output; no business logic in `cli.py`; type hints + docstrings on public functions  
**Scale/Scope**: One feature slice touching `models.py`, `utils.py` (new), `parser.py`, `extractor.py`, templates, renderer glue, and targeted tests/fixtures

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

| Principle / Rule | Status | Plan Compliance |
|---|---|---|
| User-First Output | PASS | Renderer changes prioritize readable task table + TODO callout/table.
| Annotation-Driven | PASS | Structured fields come only from explicit annotations/comments; no invented intent.
| Graceful Degradation | PASS | Flat task list retained when no task-level content exists.
| Fail Loudly in CI, Gently in CLI | PASS | No exit-code behavior changes planned.
| Convention Over Configuration | PASS | No new flags/config; default pipeline behavior preserved.
| Separation of Concerns | PASS | Parser extracts raw comments only; extractor classifies; renderer renders.
| Dataclass-Only Pipeline | PASS | Model extensions are dataclass-based.
| Dependency Constraints | PASS | No new dependencies.

No constitutional violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/002-task-comments-todos/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── template-variables.md
└── tasks.md                # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
anodyse/
├── cli.py
├── parser.py
├── extractor.py
├── models.py
├── renderer.py
├── output.py
├── utils.py                # new
└── templates/
    ├── playbook.md.j2
    ├── role.md.j2
    └── index.md.j2

tests/
├── fixtures/
│   └── playbook_task_annotated.yml   # new
├── test_utils.py                      # new
├── test_parser.py                     # updates
├── test_extractor.py                  # updates
├── test_renderer.py                   # updates
└── test_integration.py                # updates for full pipeline assertions
```

**Structure Decision**: Keep existing single-package architecture and implement feature in-place across parser/extractor/renderer/model boundaries with one new shared utility module (`anodyse/utils.py`).

## Implementation Order

Implement stages strictly in order:

`Stage 0 -> Stage 1 -> Stage 2 -> Stage 3 -> Stage 4 -> Stage 5 -> Stage 6 -> Stage 7 -> Stage 8`

## Stage Plan (for `/speckit.tasks`)

### Stage 0 — New Test Fixture

- Add `tests/fixtures/playbook_task_annotated.yml`.
- Include file-level `@title`, `@description`, and at least one `@param`.
- Include file-level `TODO`, `TODO(author)`, and `FIXME` examples.
- Include 4 tasks matching the feature acceptance matrix (full annotations + TODO, partial + prose, prose+inline only, unannotated).

### Stage 1 — Data Model Extensions (`models.py`)

1. Add `TodoItem` with `source: Literal["task", "file"]`.
2. Extend `TaskData` with optional comment/annotation/TODO fields using safe defaults (`None` or `field(default_factory=list)`).
3. Extend `PlaybookData` and `RoleData` with `todos` lists.
4. Extend `IndexEntry` with `has_todos` and `todo_count`.

### Stage 2 — Shared Utilities (`utils.py`)

1. Add `classify_comment(line)` for annotation/todo/prose classification.
2. Add `parse_todo(line)` for TODO/FIXME parsing (author preserved exactly; caller sets `source`).
3. Migrate `slugify()` from `output.py` to `utils.py` and update `output.py` imports accordingly.

### Stage 3 — Parser Changes (`parser.py`)

1. Extract task-attached block comments and first-key inline comments from ruamel comment attributes.
2. Pass raw comments downstream without classification.

### Stage 4 — Extractor Changes (`extractor.py`)

1. Add `extract_task_annotations(task, block_comments, inline_comment)`.
2. Classify block comment lines in priority order: annotation -> todo -> prose.
3. Inline comments are always prose (`inline_comment`) and never structured TODO items.
4. Add file-level TODO extraction from file-header comments into `PlaybookData.todos` / `RoleData.todos` with `source="file"`.

### Stage 5 — CLI / Pipeline Changes (`cli.py`)

1. Populate new `IndexEntry` TODO fields.
2. **Explicit counting rule**:
    - `todo_count = len(data.todos) + sum(len(t.todos) for t in data.tasks)`
    - Inline comments matching TODO/FIXME patterns are **not** counted.

### Stage 6 — Renderer & Template Changes

1. Update `playbook.md.j2` / `role.md.j2` task summary behavior:
    - Flat list when no task-level content.
    - Table when any task-level content exists.
2. Description preference: `@task.description` then `block_comment` fallback.
3. Render `inline_comment` beneath row as italic text.
4. Add conditional TODO section with `Location | Author | TODO` table.
5. Update `index.md.j2` with `TODOs` column, warning marker, and count display.
6. Update `specs/002-task-comments-todos/contracts/template-variables.md` with all new template context fields.

### Stage 7 — Tests

1. Add new `tests/test_utils.py` for classification and TODO parsing.
2. Extend `tests/test_parser.py` for block/inline extraction and blank-line handling.
3. Extend `tests/test_extractor.py` for mixed class extraction, source attribution, and no cross-contamination.
4. Extend `tests/test_renderer.py` for table fallback behavior, TODO section rendering, and index TODO fields.
5. Extend `tests/test_integration.py` with full fixture pipeline assertions.

### Stage 8 — Regression Guard

1. Run unchanged 001 integration baseline test (`test_full_pipeline_annotated_playbook`).
2. Treat any baseline failure as regression and block completion until resolved.

## Post-Design Constitution Re-Check

| Principle / Rule | Status | Design Compliance |
|---|---|---|
| User-First Output | PASS | Task table + TODO table are explicit and readable.
| Annotation-Driven | PASS | No synthetic descriptions beyond configured fallback rules.
| Graceful Degradation | PASS | Legacy flat list path preserved.
| CLI Architecture Rule | PASS | `cli.py` only orchestrates TODO flags/count calculation from extracted model state.
| Dependency & Offline Rules | PASS | No external services; stdlib + existing deps only.
| Testing Requirements | PASS | Adds unit tests for utilities/parsing/extraction/rendering + integration/regression guard.

No constitutional violations identified post-design.

## Complexity Tracking

No constitution violations requiring justification.
