# Research: Task-Level Annotations, Plain Comments & TODO Detection

**Feature**: `002-task-comments-todos`  
**Date**: 2026-03-02

## Decision 1: Canonical task annotation syntax

- **Decision**: Use colon-required syntax for task annotations: `# @task.<tag>: <value>`.
- **Rationale**: Colon form is explicit, visually consistent with existing annotation style, and avoids ambiguous token splitting when values contain multiple words.
- **Alternatives considered**:
  - Space-separated (`# @task.description <value>`) rejected due to parse ambiguity.
  - Dual support (space + colon) rejected to prevent loose grammar drift.

## Decision 2: TODO/FIXME pattern grammar

- **Decision**: Support case-insensitive patterns for TODO/FIXME in block/file-header comments:
  - `# TODO: <text>`
  - `# TODO(<author>): <text>`
  - `# TODO <text>`
  - `# FIXME: <text>`
  - `# FIXME(<author>): <text>`
  - `# FIXME <text>`
- **Rationale**: Captures common ecosystem variants without adding excessive parsing complexity.
- **Alternatives considered**:
  - `TODO:` only rejected because many teams use `FIXME` and no-colon variants.
  - Regex over all inline YAML comments rejected for false-positive risk in non-task contexts.

## Decision 3: Author preservation

- **Decision**: Preserve `author` text exactly as authored in TODO comments.
- **Rationale**: Avoids unintended normalization/casing changes and keeps provenance faithful.
- **Alternatives considered**:
  - Force lowercase or prepend `@` rejected because it mutates source semantics.

## Decision 4: Parser extraction boundary

- **Decision**: Parser extracts raw task comment surfaces only:
  - Block comment lines attached to each task node
  - Inline comment from the first key line in each task map
  Parser does not classify comments.
- **Rationale**: Enforces architecture separation (parser = structure, extractor = semantics).
- **Alternatives considered**:
  - Classifying in parser rejected due to coupling and test fragility.

## Decision 4a: ruamel.yaml comment attribute mapping

- **Decision**: Use ruamel comment-attribute containers directly for extraction:
  - `CommentedMap.ca.items` for per-key comments (including first-key inline/EOL comments)
  - `CommentedSeq.ca.items` for per-sequence-item comment association
  - `ca.pre` and item comment tuples for pre-item/block comment recovery
- **Rationale**: These are the stable comment surfaces required to reconstruct task-attached block and inline comments without semantic parsing.
- **Alternatives considered**:
  - Textual line scanning without ruamel comment attributes rejected due to fragile indentation/path mapping.

## Decision 5: Block comment attachment with blank lines

- **Decision**: Attached block comment region can contain one or more blank lines and remains attached until a non-comment, non-blank line appears before the task.
- **Rationale**: Matches real-world playbook formatting while keeping deterministic boundaries.
- **Alternatives considered**:
  - Immediate adjacency only rejected as too strict.
  - Unlimited look-back ignoring intervening lines rejected as too permissive.

## Decision 6: TODO provenance model

- **Decision**: `TodoItem.source` supports `"task" | "file"`.
- **Rationale**: Preserves origin for rendering location and downstream indexing.
- **Alternatives considered**:
  - Single fixed source (`"task"`) rejected because file-level TODOs are first-class.

## Decision 7: Counting path vs render path

- **Decision**: Inline TODO/FIXME comments are always prose for rendering and are not emitted as structured `TodoItem` records; `todo_count` is derived from structured TODO items only (file-level + task-level block TODOs).
- **Rationale**: Prevents false-positive TODO rows while keeping counting deterministic from model state.
- **Alternatives considered**:
  - Counting all TODO-looking inline prose rejected because it diverges from extracted TODO model and creates index/render inconsistency.

## Decision 8: Shared utility module

- **Decision**: Add `anodyse/utils.py` for `classify_comment`, `parse_todo`, and migrated `slugify`.
- **Rationale**: Single source of truth for comment/TODO parsing and slug behavior reuse.
- **Alternatives considered**:
  - Duplicated regex logic in extractor/cli rejected for maintenance risk.

## Decision 9: Regression safety strategy

- **Decision**: Preserve MVP fallback rendering (flat task list) when no task-level content exists and retain unchanged CLI/discovery/output naming behaviors.
- **Rationale**: Feature is additive and must not break 001 core pipeline expectations.
- **Alternatives considered**:
  - Always rendering task table rejected due to UX regression for unannotated docs.
