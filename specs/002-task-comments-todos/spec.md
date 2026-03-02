# Feature Specification: Task-Level Comments & TODO Detection

**Feature Branch**: `002-task-comments-todos`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: User description: "Task-Level Annotations with Plain Comments & TODO Detection"

## Clarifications

### Session 2026-03-02

- Q: What values should `TodoItem.source` support for provenance? → A: `task` and `file`.
- Q: Which task inline-comment location should be captured? → A: Same-line comment on the first key in the task map.
- Q: What should `todo_count` include? → A: Structured TODO items only (file-level + task-level block TODOs); inline TODO-looking prose is excluded.
- Q: How should TODO author text be normalized? → A: Preserve exact author text from source without normalization.
- Q: How should blank lines affect block-comment attachment to a task? → A: One or more blank lines may appear within an attached block (and before the task) as long as only comments/blank lines appear in that attached region.
- Q: Which `@task.*` value format should be canonical? → A: Colon-required format (`# @task.<tag>: <value>`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Structured Task Documentation (Priority: P1)

A documentation maintainer adds structured annotations to individual tasks in their playbooks using a consistent `@task.*` syntax. These annotations provide rich metadata about each task including descriptions, warnings, notes, and tags. The system captures these task-level annotations and presents them in formatted documentation.

**Why this priority**: Task-level structured documentation is the core value of this feature. Without it, only file-level annotations are captured, leaving detailed task documentation effort wasted.

**Independent Test**: Can be fully tested by annotating tasks with `@task.description`, `@task.note`, `@task.warning`, and `@task.tag`, then verifying the generated documentation includes these annotations in a structured format (table view).

**Acceptance Scenarios**:

1. **Given** a playbook with a task preceded by `# @task.description: Installs required packages`, **When** documentation is generated, **Then** the task table shows "Installs required packages" in the Description column
2. **Given** a task with multiple `# @task.note:` annotations, **When** documentation is generated, **Then** all notes appear in the Notes column
3. **Given** a task with `# @task.warning: Requires elevated privileges`, **When** documentation is generated, **Then** the warning appears prominently in the Warnings column
4. **Given** a task with `# @task.tag: security` and `# @task.tag: critical`, **When** documentation is generated, **Then** both tags appear in the Tags column

---

### User Story 2 - Plain Prose Comment Preservation (Priority: P2)

A developer writes natural language comments above and beside tasks to explain implementation details. These comments don't follow a specific annotation syntax but provide valuable context. The system captures these plain prose comments and includes them in documentation, making no documentation effort wasted.

**Why this priority**: Preserves existing documentation effort. Many playbooks have extensive plain comments that currently go undocumented. This enables gradual adoption without requiring immediate annotation syntax compliance.

**Independent Test**: Can be fully tested by adding plain comments (both block comments above tasks and inline comments) and verifying they appear in the generated documentation as descriptive text.

**Acceptance Scenarios**:

1. **Given** a task with an attached plain-comment block above it (including optional blank lines) and no `@task.description`, **When** documentation is generated, **Then** the plain comment text appears as the task description
2. **Given** a task where the first key line carries an inline comment, **When** documentation is generated, **Then** that inline comment appears as supplementary text below the task
3. **Given** a task with both structured annotations and plain comments, **When** documentation is generated, **Then** plain comments supplement but don't override structured annotations
4. **Given** a task with multiple plain comment lines above it, **When** documentation is generated, **Then** all comment lines are captured as a single prose block

---

### User Story 3 - TODO and FIXME Tracking (Priority: P3)

A team uses TODO and FIXME comments throughout their playbooks to mark incomplete work, known issues, and planned improvements. The system detects these TODO patterns (including optional author attribution), extracts them into a dedicated section, and flags files containing TODOs in the index for easy discovery.

**Why this priority**: TODOs are actionable items that deserve special visibility. While lower priority than core documentation, surfacing them prominently helps teams track technical debt and incomplete work.

**Independent Test**: Can be fully tested by adding `# TODO:` and `# FIXME:` comments (with and without author attribution), then verifying a TODO section appears in documentation and the index shows a warning indicator.

**Acceptance Scenarios**:

1. **Given** a playbook with file-level comment `# TODO: Add error handling`, **When** documentation is generated, **Then** a TODO section appears showing "File" as location and the TODO text
2. **Given** a task with comment `# TODO(alice): Optimize this query`, **When** documentation is generated, **Then** the TODO section shows "Task: [task name]" as location, "alice" as author, and the TODO text
3. **Given** a playbook with multiple TODOs across file-level and tasks, **When** documentation is generated, **Then** the index page shows a ⚠️ indicator and TODO count for that entry
4. **Given** comments using `# FIXME: broken on Ubuntu 20.04`, **When** documentation is generated, **Then** FIXME is treated as a TODO and appears in the TODO section
5. **Given** an inline comment with TODO text like `- name: Task  # TODO: refactor this`, **When** documentation is generated, **Then** it's treated as a plain comment, NOT as a structured TODO (prevents false positives)

---

### Edge Cases

- What happens when a task has both structured `@task.description` and plain prose comments? The structured annotation takes priority; plain prose appears as supplementary text.
- What happens when no task-level content exists (no annotations, no comments, no TODOs)? Documentation renders as a simple ordered list of task names, unchanged from current behavior.
- What happens when a TODO appears inline on a task line? It's captured as a plain comment, not as a structured TODO, to prevent false positives from commented-out code.
- What happens when task annotations from one task might contaminate another? Each task's comments are extracted independently; no cross-contamination occurs.
- How does the system handle case variations in TODO patterns? TODO, Todo, and todo are all recognized (case-insensitive matching).
- What happens when a TODO has no author attribution? The author field shows a dash (—) indicating no author specified.
- What happens when a file has no TODOs at all? No TODO section appears in documentation; no warning indicator in index.
- What happens when one or more blank lines appear inside a comment block above a task? The block remains attached to that task as long as no non-comment, non-blank content appears between the block and the task.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST capture structured task-level annotations using the canonical pattern `# @task.<tag>: <value>` where tag includes: description, note, warning, tag
- **FR-002**: System MUST capture plain prose block comments (not matching annotation or TODO patterns) attached to a task, where the attached region may include one or more blank lines but no non-comment, non-blank lines
- **FR-003**: System MUST capture plain prose inline comments from the same line as the first key in each task map
- **FR-004**: System MUST detect and extract TODO/FIXME comments matching patterns: `# TODO: <text>`, `# TODO(<author>): <text>`, `# TODO <text>`, and equivalent FIXME variants (case-insensitive)
- **FR-005**: System MUST extract author attribution from TODO comments when present in `TODO(<author>):` format
- **FR-006**: System MUST classify each comment line into one of three categories: structured annotation, TODO/FIXME, or plain prose (in that priority order)
- **FR-007**: System MUST treat inline TODO comments as plain prose, not as structured TODOs, to prevent false positives
- **FR-008**: System MUST detect and extract TODOs at both file level (in file header) and task level
- **FR-009**: System MUST render task documentation as a table when any task-level content is present (annotations, comments, or TODOs)
- **FR-010**: System MUST render a dedicated TODO section in documentation when at least one TODO exists, showing location (file vs task), author, and TODO text
- **FR-011**: System MUST add a warning indicator (⚠️) in the index page for files containing TODOs
- **FR-012**: System MUST show TODO count in the index page for each documented file, where count includes structured TODO items only (file-level + task-level block TODOs)
- **FR-013**: System MUST prefer structured `@task.description` over plain prose when both are present, but use plain prose as fallback when `@task.description` is absent
- **FR-014**: System MUST display inline comments as supplementary text below task table rows (not in the main table)
- **FR-015**: System MUST maintain backward compatibility - files without task-level content render as simple task lists unchanged from MVP behavior
- **FR-016**: System MUST NOT emit warnings for absent task-level annotations (unlike file-level annotations which warn when missing)
- **FR-017**: System MUST preserve TODO provenance by setting source to either `task` (task-level TODO) or `file` (file-header TODO)
- **FR-018**: System MUST preserve TODO author text exactly as written in source when present (no normalization or formatting changes)
- **FR-019**: System MUST keep TODO extraction and TODO counting as separate behaviors: inline TODO/FIXME comments remain prose for rendering (not structured TODO items) and do not contribute to `todo_count`

### Key Entities

- **Task-Level Annotation**: Structured metadata attached to a specific task using `@task.*` syntax. Includes description (single value), notes (repeatable), warnings (repeatable), and tags (repeatable).
- **Plain Prose Comment**: Unstructured human-readable text attached to tasks, either in block position (preceding the task) or inline position (same line as task key).
- **TODO Item**: Actionable item extracted from TODO/FIXME comments. Contains message text, optional author attribution preserved exactly as authored, and source in `{task, file}`.
- **Documentation Index Entry**: Catalog entry for each documented file. Extended to include TODO presence indicator and count.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can document individual tasks using structured `@task.*` annotations, and these appear in generated documentation within 10 seconds of running the tool
- **SC-002**: Existing playbooks with plain comments (not using annotation syntax) generate documentation that includes those comments without requiring any changes to source files
- **SC-003**: Teams can identify files with outstanding TODOs by scanning the documentation index (⚠️ indicators visible), reducing time spent searching for TODO items by at least 70%
- **SC-004**: All TODO and FIXME patterns (case-insensitive, with or without author attribution) are detected with 100% accuracy when appearing in block comment position
- **SC-005**: Inline TODO comments never appear in the structured TODO section (zero false positives from commented-out code)
- **SC-006**: Documentation generation completes successfully for playbooks with mixed content (some tasks annotated, some with plain comments, some with both, some with neither) without errors
- **SC-007**: The index page correctly shows TODO counts matching the total number of structured TODO items (file-level plus task-level block TODOs)
- **SC-008**: Documentation for files without any task-level content remains identical to MVP output (zero visual regression)
