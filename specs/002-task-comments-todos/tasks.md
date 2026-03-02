# Tasks: Anodyse Feature 002 — Task-Level Annotations, Plain Comments & TODO Detection

**Input**: Design documents from `/specs/002-task-comments-todos/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/template-variables.md`

**Tests**: Included because the feature specification explicitly requires unit, renderer, parser, extractor, and integration coverage.

## Phase 1: Setup (Project Initialization)

**Purpose**: Create feature fixture used by parser/extractor/renderer/integration tests.

- [ ] T001 Create task-comment coverage fixture in `tests/fixtures/playbook_task_annotated.yml`
- [ ] T002 Add fixture sanity test hook for parseability in `tests/test_parser.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model and utility changes required before user stories.

**⚠️ CRITICAL**: No user story implementation should start until this phase is complete.

- [ ] T003 Add `TodoItem` dataclass with `Literal["task", "file"]` in `anodyse/models.py`
- [ ] T004 Extend `TaskData` with task annotation/comment/TODO fields in `anodyse/models.py`
- [ ] T005 Extend `PlaybookData` and `RoleData` with `todos` lists in `anodyse/models.py`
- [ ] T006 Extend `IndexEntry` with `has_todos` and `todo_count` in `anodyse/models.py`
- [ ] T007 Create `classify_comment()` with strict priority in `anodyse/utils.py`
- [ ] T008 Add `parse_todo()` pattern parser in `anodyse/utils.py`
- [ ] T009 Migrate `slugify()` to `anodyse/utils.py` and update import in `anodyse/output.py`
- [ ] T010 Add utility unit tests (`test_classify_*`, `test_parse_todo_*`) in `tests/test_utils.py`

**Checkpoint**: Shared types/parsers/utilities are ready for story work.

---

## Phase 3: User Story 1 — Structured Task Documentation (Priority: P1) 🎯 MVP

**Goal**: Extract and render `@task.*` annotations for per-task documentation.

**Independent Test**: Run parser+extractor+renderer tests for structured task annotations and verify task table shows annotation-derived fields.

### Tests for User Story 1

- [ ] T011 [P] [US1] Add parser tests `test_parser_extracts_block_comments_per_task` and `test_parser_extracts_inline_comment_per_task` in `tests/test_parser.py`
- [ ] T012 [P] [US1] Add extractor tests `test_extract_task_annotation_class_a` and `test_extract_task_no_cross_contamination_between_tasks` in `tests/test_extractor.py`
- [ ] T013 [P] [US1] Add renderer tests `test_render_task_summary_table_when_any_content` and `test_render_task_description_uses_annotation_first` in `tests/test_renderer.py`

### Implementation for User Story 1

- [ ] T014 [US1] Implement task block/inline raw comment extraction handoff in `anodyse/parser.py`
- [ ] T015 [US1] Implement `extract_task_annotations()` Class A mapping (`@task.description|note|warning|tag`) in `anodyse/extractor.py`
- [ ] T016 [US1] Wire per-task extraction flow in `extract()` for task lists in `anodyse/extractor.py`
- [ ] T017 [US1] Implement task summary table rendering (Description/Notes/Warnings/Tags) with flat-list fallback in `anodyse/templates/playbook.md.j2`
- [ ] T018 [US1] Implement task summary table rendering (Description/Notes/Warnings/Tags) with flat-list fallback in `anodyse/templates/role.md.j2`

**Checkpoint**: Structured task annotations render end-to-end independent of prose/TODO enhancements.

---

## Phase 4: User Story 2 — Plain Prose Comment Preservation (Priority: P2)

**Goal**: Preserve block prose and inline prose comments as task context.

**Independent Test**: Verify block prose becomes description fallback and inline prose appears beneath corresponding table row.

### Tests for User Story 2

- [ ] T019 [P] [US2] Add parser tests `test_parser_blank_lines_in_block_region_included` and `test_parser_no_cross_task_comment_bleed` in `tests/test_parser.py`
- [ ] T020 [P] [US2] Add extractor tests `test_extract_task_prose_block` and `test_extract_task_inline_comment` in `tests/test_extractor.py`
- [ ] T021 [P] [US2] Add renderer tests `test_render_task_description_falls_back_to_block_comment` and `test_render_task_inline_comment_below_table_row` in `tests/test_renderer.py`

### Implementation for User Story 2

- [ ] T022 [US2] Implement block prose aggregation and inline prose assignment in `extract_task_annotations()` within `anodyse/extractor.py`
- [ ] T023 [US2] Implement description fallback (`task.description` then `task.block_comment`) in `anodyse/templates/playbook.md.j2`
- [ ] T024 [US2] Implement description fallback (`task.description` then `task.block_comment`) in `anodyse/templates/role.md.j2`
- [ ] T025 [US2] Render inline comment beneath task row as italic prose in `anodyse/templates/playbook.md.j2`
- [ ] T026 [US2] Render inline comment beneath task row as italic prose in `anodyse/templates/role.md.j2`

**Checkpoint**: Prose comments are preserved and independently testable without TODO section behavior.

---

## Phase 5: User Story 3 — TODO and FIXME Tracking (Priority: P3)

**Goal**: Extract TODO/FIXME as structured items, render TODO section, and surface index flags/counts.

**Independent Test**: Verify TODO section and index TODO metadata using fixture with file-level and task-level TODOs.

### Tests for User Story 3

- [ ] T027 [P] [US3] Add extractor tests `test_extract_task_todo_in_block`, `test_extract_task_inline_todo_is_prose_not_structured`, `test_extract_file_level_todo_source_is_file`, and `test_extract_no_todos_empty_list` in `tests/test_extractor.py`
- [ ] T028 [P] [US3] Add renderer tests `test_render_todo_section_present_when_todos_exist`, `test_render_todo_section_absent_when_no_todos`, `test_render_todo_table_columns`, `test_render_todo_author_dash_when_none`, `test_render_todo_location_file_vs_task`, `test_render_index_todo_flag_present`, and `test_render_index_todo_count_shown` in `tests/test_renderer.py`
- [ ] T029 [P] [US3] Add integration test `test_full_pipeline_task_annotated_fixture` in `tests/test_integration.py`

### Implementation for User Story 3

- [ ] T030 [US3] Implement TODO/FIXME Class C extraction to `task.todos` with `source="task"` in `anodyse/extractor.py`
- [ ] T031 [US3] Implement file-header TODO extraction to `data.todos` with `source="file"` in `anodyse/extractor.py`
- [ ] T032 [US3] Populate `IndexEntry.has_todos` and structured `todo_count` in pipeline orchestration within `anodyse/cli.py`
- [ ] T033 [US3] Add TODO section rendering (Location/Author/TODO) in `anodyse/templates/playbook.md.j2`
- [ ] T034 [US3] Add TODO section rendering (Location/Author/TODO) in `anodyse/templates/role.md.j2`
- [ ] T035 [US3] Add index TODO indicator and TODOs column in `anodyse/templates/index.md.j2`
- [ ] T036 [US3] Update feature template contract fields in `specs/002-task-comments-todos/contracts/template-variables.md`

**Checkpoint**: TODO extraction/render/index behavior works independently with locked counting/classification rules.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, docs sync, and regression protection.

- [ ] T037 [P] Run feature quickstart validation steps in `specs/002-task-comments-todos/quickstart.md`
- [ ] T038 [P] Verify no regressions in existing parser/extractor/renderer tests across `tests/`
- [ ] T039 Run unchanged 001 regression guard `test_full_pipeline_annotated_playbook` in `tests/test_integration.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: no dependencies.
- **Phase 2 (Foundational)**: depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: depends on Phase 2 completion.
- **Phase 4 (US2)**: depends on Phase 3 parser/extractor baseline (`T014`-`T016`) and Phase 2.
- **Phase 5 (US3)**: depends on Phase 2 and core extraction handoff (`T014`-`T016`).
- **Phase 6 (Polish)**: depends on all prior phases; regression guard is final.

### User Story Completion Order

- **US1 (P1)** → **US2 (P2)** → **US3 (P3)**
- US2 and US3 rely on US1’s parser→extractor task-comment plumbing.

### Within-Story Dependencies

- US1 implementation: `T014` -> `T015` -> `T016` -> `T017`/`T018`.
- US2 implementation: `T022` -> (`T023`,`T024`) -> (`T025`,`T026`).
- US3 implementation: (`T030`,`T031`) -> `T032` -> (`T033`,`T034`,`T035`) -> `T036`.
- Final guard `T039` depends on all tasks `T001`-`T038`.

---

## Parallel Execution Examples

### User Story 1

- Run `T011`, `T012`, and `T013` in parallel (different test files).
- After extractor wiring, `T017` and `T018` can run in parallel (separate templates).

### User Story 2

- Run `T019`, `T020`, and `T021` in parallel (parser/extractor/renderer test files).
- Run `T023` and `T024` in parallel after `T022`.
- Run `T025` and `T026` in parallel after fallback tasks.

### User Story 3

- Run `T027`, `T028`, and `T029` in parallel (test files).
- Run `T033`, `T034`, and `T035` in parallel after `T032`.

---

## Implementation Strategy

### MVP First (US1)

1. Complete Setup + Foundational (`T001`-`T010`).
2. Deliver US1 (`T011`-`T018`) and validate structured task table behavior.
3. Stop and verify MVP value before expanding scope.

### Incremental Delivery

1. Add US2 prose preservation (`T019`-`T026`) and validate fallback/inline behavior.
2. Add US3 TODO tracking (`T027`-`T036`) and validate TODO section + index signals.
3. Finish with cross-cutting validation and regression guard (`T037`-`T039`).

### Final Safety Gate

- Do not mark feature complete until `T039` passes unchanged baseline integration behavior.
