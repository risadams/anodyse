# Quickstart: Feature 002 Validation

**Feature**: `002-task-comments-todos`  
**Branch**: `002-task-comments-todos`

## Goal

Validate task-level annotation extraction, prose comment capture, TODO rendering, and index TODO flags/counts with no regression to existing MVP behavior.

## Prerequisites

- Python environment set up for this repo
- Test dependencies installed (`pytest`)
- Working directory: repository root

## 1) Run focused unit tests

```powershell
pytest tests/test_utils.py -q
pytest tests/test_parser.py -q
pytest tests/test_extractor.py -q
pytest tests/test_renderer.py -q
```

Expected:
- `test_utils.py` validates comment classification + TODO parsing.
- `test_parser.py` validates block/inline comment extraction surfaces.
- `test_extractor.py` validates class A/B/C separation and source attribution.
- `test_renderer.py` validates task table fallback + TODO section/index rendering.

## 2) Run integration test with new fixture

```powershell
pytest tests/test_integration.py -k task_annotated -q
```

Expected assertions include:
- Task summary table appears (not flat list) for annotated fixture.
- Task description preference + block-comment fallback works.
- Inline comment appears beneath associated table row.
- TODO section appears with correct `File` vs `Task: <name>` locations.
- Index shows warning indicator and expected TODO count from structured items.

## 3) Run regression guard for MVP baseline

```powershell
pytest tests/test_integration.py -k annotated_playbook -q
```

Expected:
- Existing 001 core pipeline integration behavior remains unchanged.

## 4) Optional manual smoke run

```powershell
anodyse tests/fixtures/playbook_task_annotated.yml --output ./tmp-docs
```

Check output:
- Generated playbook Markdown contains task table + TODO section.
- `index.md` contains TODO column and warning marker for the generated file.

## Troubleshooting

- If parser tests fail, verify comment extraction uses raw comment attributes only (no classification in parser).
- If TODO count mismatches, verify count uses structured TODO lists (`data.todos` + `task.todos`) rather than inline prose scanning.
- If renderer output regresses to table for all files, ensure fallback flat-list path still triggers when no task-level content exists.
