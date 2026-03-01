# Feature Specification: Core Parse-Extract-Render Pipeline (MVP)

**Feature Branch**: `001-core-pipeline`  
**Created**: 2026-03-01  
**Status**: Draft  
**Input**: User description: "Build the foundational parse-extract-render pipeline for Anodyse — the three-stage process that takes an Ansible playbook or role directory as input and produces user-facing Markdown documentation as output. MVP covers CLI entry point, YAML parser, annotation extractor, Markdown renderer, file output handling, and a basic docs index page."

## Clarifications

### Session 2026-03-01

**Ambiguity Resolution from Structured Specification Review:**

- Q: Where in the YAML hierarchy should @annotations be extracted? → A: All levels including role vars (playbook-level, task-level, and within role defaults/vars comments for @param cross-reference)

- Q: How detailed should Mermaid diagrams be with the --graph flag? → A: Complex flowchart with conditionals and branches (show conditional branches, loops, and task relationships visually)

- Q: What should be documented for roles in generated output? → A: Tasks + annotated params only (task names and descriptions, plus parameters that have explicit @param annotations; unmarked defaults omitted)

- Q: When running `anodyse .` on a directory, what should be included in index.md? → A: Directory-first discovery with manifest override — Mode 1: recursive directory scan finds .yml files with `hosts:` key (playbooks) and directories with `tasks/main.yml` (roles). Mode 2: optional `.anodyse.yml` manifest file allows explicit include/exclude lists. Zero-config by default, explicit control when needed.

- Q: How should user-provided templates be validated and handled? → A: Schema-validated with warnings (validate templates against Jinja2 variable schema; warn on incompatibility instead of failing, per constitution's graceful degradation principle)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Analyst Converts Playbook to Documentation (Priority: P1)

A platform analyst has an existing Ansible playbook (`deploy.yml`) with no annotations. They want to generate a skeleton documentation page that lists all tasks, allowing non-technical platform users to understand the playbook's structure.

**Why this priority**: This is the core value proposition — converting raw YAML into readable documentation. Without this, Anodyse has no purpose. P1 users are those generating docs with minimal annotation overhead.

**Independent Test**: Can run `anodyse docs/deploy.yml --output ./docs` and receive a valid Markdown file listing all task names, with an "Undocumented" notice for the description.

**Acceptance Scenarios**:

1. **Given** a valid playbook with tasks but no annotations, **When** processed by Anodyse, **Then** a Markdown file is generated containing the playbook name (or filename), all task names as a list, and a notice indicating "Description not provided".

2. **Given** the same playbook, **When** the user adds a `# @title` annotation (at playbook top level or within first task), **Then** that title appears in the generated documentation instead of the filename.

3. **Given** a role directory structure (tasks/, defaults/, vars/, meta/), **When** processed, **Then** a Markdown file is generated containing task names from tasks/main.yml and variables from defaults/main.yml that have `@param` annotations.

---

### User Story 2 - Annotated Playbook Produces Full Documentation (Priority: P1)

An infrastructure team has carefully annotated their playbooks with `@description`, `@param`, `@warning`, and `@example` comments at playbook level and/or task level. They want to generate polished user-facing docs that explain each playbook's purpose, what parameters users can pass, and common usage patterns.

**Why this priority**: This demonstrates the annotation-driven principle from the constitution and shows Anodyse's value when users invest in documentation. Essential for showcase scenarios.

**Independent Test**: Can run `anodyse deploy_annotated.yml --output ./docs` on a fully-annotated playbook and verify that all annotations (at playbook and task levels) appear correctly in the rendered Markdown (title, description, param table, warnings, examples).

**Acceptance Scenarios**:

1. **Given** a playbook with `@title`, `@description`, `@param`, and `@example` annotations at playbook level, **When** processed, **Then** a Markdown file is produced with sections for each annotation type, formatted for readability.

2. **Given** tasks with individual `@description` annotations, **When** rendered, **Then** task-level descriptions appear in the task summary or as a separate task detail section.

3. **Given** multiple `@warning` annotations (at playbook or task level), **When** rendered, **Then** all warnings appear in a blockquote list with clear visual emphasis.

4. **Given** multiple `@example` annotations with code blocks, **When** rendered, **Then** each example is formatted as a code block with language syntax highlighting (YAML, shell, etc. preserved from comments).

---

### User Story 3 - Single Command Generates Complete Docs Index (Priority: P1)

An operations team has 20 playbooks and roles across a directory structure. They want a single command to generate docs for all items via automatic discovery and produce an `index.md` that lists all items, their descriptions, and tags for easy navigation. In some cases, they need to exclude scratch files or include only specific subsets.

**Why this priority**: Scalability and CLI usability. Without automatic discovery and index generation, users must manually manage doc discovery. This is the "convention over configuration" principle — sensible defaults with opt-in override.

**Independent Test**: Can run `anodyse ./playbooks --output ./docs` and receive both individual .md files for all auto-discovered playbooks/roles plus an index.md. Can optionally add `.anodyse.yml` to control discovery.

**Acceptance Scenarios**:

1. **Given** a directory containing multiple .yml files with `hosts:` keys and role directories with `tasks/main.yml`, **When** processed, **Then** Anodyse auto-discovers all playbooks and roles, generates docs for each, and creates an index.md listing all items.

2. **Given** a `.anodyse.yml` manifest file with `include:` list, **When** present in the target directory (or repo root), **Then** only the explicitly included paths are documented and appear in the index.

3. **Given** a `.anodyse.yml` manifest file with `exclude:` list, **When** present, **Then** the listed paths are excluded from documentation even if otherwise valid playbooks/roles.

4. **Given** playbooks with `@tag` annotations, **When** the index is generated, **Then** each item in the index includes its tags for categorization.

5. **Given** an existing docs directory with output files, **When** Anodyse runs again, **Then** existing .md files are backed up with `.bak` extension before being overwritten (unless `--no-backup` flag is used).

---

### User Story 4 - Flow Diagrams Aid Complex Playbook Understanding (Priority: P2)

A user has a complex multi-stage playbook with conditional task execution, task loops, and handler definitions. They want a visual flow diagram showing the execution order, including branching logic, to help non-technical users understand the playbook's logic without reading YAML.

**Why this priority**: Mermaid diagrams enhance usability for complex playbooks but are optional for simple ones. P2 because the feature is complete without them; they are a nice-to-have enhancement.

**Independent Test**: Can run `anodyse complex_playbook.yml --output ./docs --graph` and receive a Markdown file with an embedded Mermaid diagram showing task sequence including pre_tasks, tasks, post_tasks, handlers, and conditional branches.

**Acceptance Scenarios**:

1. **Given** the `--graph` flag, **When** a complex playbook is processed, **Then** an optional Mermaid diagram is included showing all top-level tasks in sequence order with conditional branches.

2. **Given** a playbook with pre_tasks, tasks, post_tasks, and handlers, **When** the graph is rendered, **Then** all four stages appear in the diagram in the correct execution order.

3. **Given** tasks with `when` conditions or `loop` clauses, **When** the graph is rendered, **Then** conditional branches or loops are visually represented in the diagram.

---

### User Story 5 - CLI Error Messages Guide Troubleshooting (Priority: P1)

A user provides a path to a non-existent file, a malformed YAML file, or a directory with incompatible user templates. They receive a clear error message that explains what went wrong and how to fix it.

**Why this priority**: Error handling directly impacts user experience. Per constitution "fail loudly in CI", non-zero exit codes must be reliable and messages must be clear.

**Independent Test**: Can run `anodyse invalid.yml` and receive exit code 1 or 2 with a message that identifies the problem (file not found, YAML parse error, template incompatibility, etc.).

**Acceptance Scenarios**:

1. **Given** a path to a non-existent file, **When** processed, **Then** exit code 1 is returned with a message like "File not found: <path>".

2. **Given** a YAML file with syntax errors, **When** processed, **Then** exit code 1 is returned with a YAML error message indicating the line and nature of the error.

3. **Given** a directory with no valid playbooks or roles, **When** processed, **Then** exit code 1 is returned with a message explaining no valid content was found.

4. **Given** incompatible user templates in `.anodyse/templates/`, **When** processed, **Then** exit code 2 is returned with a warning message describing the incompatibility, and degraded output is produced using default templates.

---

### Edge Cases

- What happens if a .yml file has a `hosts:` key but is not a valid Ansible playbook?
- What happens if a directory has `tasks/main.yml` but is not a valid role structure?
- What happens if `.anodyse.yml` manifest includes a path that does not exist?
- What happens if `.anodyse.yml` manifest has invalid YAML syntax?
- What happens if a `@param` annotation references a variable that does not exist in defaults/vars?
- What happens if YAML contains duplicate task names?
- What happens if a playbook/role name contains special characters that cannot be slugified?
- What happens if the output directory does not exist?
- What happens if existing .bak files already exist (multiple runs)?
- What happens if annotation values contain special characters or newlines?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: CLI MUST accept a target path (file or directory) as a positional argument and process it to generate documentation.

- **FR-002**: CLI MUST support the following options: `--output` (directory path), `--graph` (enable Mermaid diagrams), `--no-backup` (skip backing up existing files), `--verbose` (print detailed output), `--format` (output format, default: markdown), `--config` (explicit path to `.anodyse.yml` manifest file, overrides auto-discovery at target directory or repo root).

- **FR-003**: YAML parser MUST load and validate YAML files using ruamel.yaml and return a typed PlaybookData or RoleData dataclass (never a raw dict).

- **FR-004**: Parser MUST identify target type (playbook or role) based on file/directory structure and extract the appropriate data (tasks, pre_tasks, post_tasks, handlers, roles, defaults, vars, meta).

- **FR-005**: Annotation extractor MUST scan YAML comments at all levels (playbook-level, task-level, and within role vars/defaults comments) for lines matching `# @<tag> <value>` and attach extracted annotations to dataclass fields.

- **FR-006**: Extractor MUST support annotation tags: `@title`, `@description`, `@param` (repeatable), `@warning` (repeatable), `@example` (repeatable), `@tag` (repeatable).

- **FR-007**: Extractor MUST set description fields to None (not generate/invent) when `@description` annotations are absent, per constitution annotation-driven principle.

- **FR-008**: Extractor MUST emit a warning to stdout when mandatory annotations (`@title`, `@description`) are missing but continue processing (graceful degradation).

- **FR-009**: When processing a directory, parser MUST recursively scan for valid playbooks (any .yml/.yaml file containing a top-level `hosts:` key) and roles (any directory containing `tasks/main.yml`). Parser MAY optionally load a `.anodyse.yml` manifest file from the target directory or repo root to override discovery with explicit `include:` and `exclude:` lists.

- **FR-010**: Markdown renderer MUST consume a populated dataclass and render a Markdown document using Jinja2 templates from `anodyse/templates/`.

- **FR-011**: Renderer MUST produce output pages including: title, description (or "Undocumented" notice), parameters table (only for annotated @param), warnings, usage examples, task summary (with task-level descriptions if annotated), and optional Mermaid diagram showing pre_tasks, tasks, post_tasks, handlers, and conditional branches.

- **FR-012**: Renderer MUST support user-overridable templates by checking for custom templates in `.anodyse/templates/` directory at invocation time. User templates MUST be validated against Jinja2 variable schema; incompatible templates trigger a warning (exit code 2) but rendering continues with defaults.

- **FR-013**: Output handler MUST generate one Markdown file per playbook/role with slugified filenames (lowercase, hyphens, no special characters).

- **FR-014**: Output handler MUST generate an `index.md` listing all discovered and documented items with their `@tag` values and one-line descriptions (mandatory output). Index MUST reflect the actual discovery result (auto-discovered items or manifest-filtered items).

- **FR-015**: Output handler MUST back up existing files as `<filename>.bak` before overwriting, unless `--no-backup` flag is passed.

- **FR-016**: Output handler MUST create the output directory if it does not exist.

- **FR-017**: All output files MUST be UTF-8 encoded.

- **FR-018**: CLI MUST exit with code 0 on success, code 1 on parse errors or file not found, and code 2 when warnings are emitted (missing mandatory annotations or template incompatibility) but degraded output is produced.

### Key Entities

- **Playbook**: A single .yml file defining a sequence of tasks to run against hosts. Contains pre_tasks, tasks, post_tasks, handlers, roles, tags, variables, and metadata.

- **Role**: A directory structure (tasks/, defaults/, vars/, meta/, handlers/) defining reusable automation units. Can be referenced by playbooks.

- **Task**: A named Ansible operation with a module type and arguments. Can have task-level annotations describing its purpose. Part of a playbook or role.

- **Annotation**: A structured comment in YAML format (`# @tag value`) providing user-facing documentation hints. Can appear at playbook level, task level, or within role vars/defaults comments.

- **PlaybookData**: Python dataclass representing parsed playbook structure with extracted annotations, task list, and role references.

- **RoleData**: Python dataclass representing parsed role structure with extracted annotations, tasks, and annotated variables (from defaults/vars).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can generate documentation for a 20-task playbook (without complex conditionals) in under 2 seconds from a single CLI command.

- **SC-002**: Generated Markdown is valid UTF-8 and renders without errors in standard Markdown viewers (GitHub, GitLab, MkDocs, etc.).

- **SC-003**: A playbook with no annotations produces usable skeleton documentation (task names visible, "Undocumented" notices clear but not blocking).

- **SC-004**: Fully-annotated playbooks produce documentation where all annotations (title, description, params, warnings, examples) appear in the output exactly as provided.

- **SC-005**: 100% of CLI error paths return the correct exit code (0 for success, 1 for parse errors, 2 for warnings).

- **SC-006**: Error messages are human-readable and include the file path and specific problem (not internal tracebacks).

- **SC-007**: The generated index.md successfully lists all playbooks/roles (including discovered role dependencies) from a multi-item run with no duplicates or omissions.

- **SC-008**: Template files are user-replaceable — users can override default templates and see changes reflected in output. Incompatible templates produce warnings but do not block rendering.

- **SC-009**: Pipeline produces zero modifications to source playbook or role files (read-only verification).

- **SC-010**: Test coverage for parser, extractor, and renderer modules is ≥80% per constitution requirements.

---

## Assumptions

- Input is well-formed Ansible syntax; Anodyse validates YAML but does not validate Ansible-specific semantics (e.g., module existence).
- Playbook/role names contain only alphanumeric characters, underscores, and hyphens; special characters are slugified.
- Output directory is writable and has sufficient disk space (no explicit quota checks).
- Users have basic familiarity with Markdown and CLI tools; help text is included but extensive tutorials are out of scope.
- No encrypted vaults or secrets are present in input files; Anodyse does not handle vault decryption (out of scope).
- Linux/macOS file paths only; Windows path handling deferred to v2.
- Role circular dependencies are rare and will be handled with a maximum recursion depth limit (implementation detail, not tested in MVP).

---

## Out of Scope (v1)

- Web server or UI for browsing docs.
- AI-generated descriptions for undocumented annotations.
- External API calls or network features.
- Encrypted vault support.
- Windows path handling.
- Interactive CLI mode (only batch mode).
- PDF or HTML output (Markdown only).
- Full DAG execution analysis (complex flowchart visualizations are single-level, not tracking nested role calls).
