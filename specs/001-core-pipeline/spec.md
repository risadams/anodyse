# Feature Specification: Core Parse-Extract-Render Pipeline (MVP)

**Feature Branch**: `001-core-pipeline`  
**Created**: 2026-03-01  
**Status**: Draft  
**Input**: User description: "Build the foundational parse-extract-render pipeline for Anodyse — the three-stage process that takes an Ansible playbook or role directory as input and produces user-facing Markdown documentation as output. MVP covers CLI entry point, YAML parser, annotation extractor, Markdown renderer, file output handling, and a basic docs index page."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Analyst Converts Playbook to Documentation (Priority: P1)

A platform analyst has an existing Ansible playbook (`deploy.yml`) with no annotations. They want to generate a skeleton documentation page that lists all tasks, allowing non-technical platform users to understand the playbook's structure.

**Why this priority**: This is the core value proposition — converting raw YAML into readable documentation. Without this, Anodyse has no purpose. P1 users are those generating docs with minimal annotation overhead.

**Independent Test**: Can run `anodyse docs/deploy.yml --output ./docs` and receive a valid Markdown file listing all task names, with an "Undocumented" notice for the description.

**Acceptance Scenarios**:

1. **Given** a valid playbook with tasks but no annotations, **When** processed by Anodyse, **Then** a Markdown file is generated containing the playbook name (or filename), all task names as a list, and a notice indicating "Description not provided".

2. **Given** the same playbook, **When** the user adds a `# @title` annotation, **Then** that title appears in the generated documentation instead of the filename.

3. **Given** a role directory structure (tasks/, defaults/, vars/, meta/), **When** processed, **Then** a Markdown file is generated containing task names from tasks/main.yml and available default variables from defaults/main.yml.

---

### User Story 2 - Annotated Playbook Produces Full Documentation (Priority: P1)

An infrastructure team has carefully annotated their playbooks with `@description`, `@param`, `@warning`, and `@example` comments. They want to generate polished user-facing docs that explain each playbook's purpose, what parameters users can pass, and common usage patterns.

**Why this priority**: This demonstrates the annotation-driven principle from the constitution and shows Anodyse's value when users invest in documentation. Essential for showcase scenarios.

**Independent Test**: Can run `anodyse deploy_annotated.yml --output ./docs` on a fully-annotated playbook and verify that all annotations appear correctly in the rendered Markdown (title, description, param table, warnings, examples).

**Acceptance Scenarios**:

1. **Given** a playbook with `@title`, `@description`, `@param`, and `@example` annotations, **When** processed, **Then** a Markdown file is produced with sections for each annotation type, formatted for readability.

2. **Given** multiple `@warning` annotations, **When** rendered, **Then** all warnings appear in a blockquote list with clear visual emphasis.

3. **Given** multiple `@example` annotations with code blocks, **When** rendered, **Then** each example is formatted as a code block with language syntax highlighting (YAML, shell, etc. preserved from comments).

---

### User Story 3 - Single Command Generates Complete Docs Index (Priority: P1)

An operations team has 20 playbooks and roles across a directory. They want a single command to generate docs for all of them and produce an `index.md` that lists all items, their descriptions, and tags for easy navigation.

**Why this priority**: Scalability and CLI usability. Without index generation, users must manually manage doc discovery. This is the "convention over configuration" principle — sensible defaults.

**Independent Test**: Can run `anodyse . --output ./docs` from a directory containing multiple playbooks/roles and receive both individual .md files and an index.md with all items listed.

**Acceptance Scenarios**:

1. **Given** a directory with multiple playbooks and roles, **When** processed with no target specified (or "." as target), **Then** Anodyse generates docs for all valid items and an index.md.

2. **Given** playbooks with `@tag` annotations, **When** the index is generated, **Then** each item in the index includes its tags for categorization.

3. **Given** an existing docs directory with output files, **When** Anodyse runs again, **Then** existing .md files are backed up with `.bak` extension before being overwritten (unless `--no-backup` flag is used).

---

### User Story 4 - Flow Diagrams Aid Complex Playbook Understanding (Priority: P2)

A user has a complex multi-stage playbook with conditional task execution. They want a visual flow diagram showing the execution order to help non-technical users understand the playbook's logic without reading YAML.

**Why this priority**: Mermaid diagrams enhance usability for complex playbooks but are optional for simple ones. P2 because the feature is complete without them; they are a nice-to-have enhancement.

**Independent Test**: Can run `anodyse complex_playbook.yml --output ./docs --graph` and receive a Markdown file with an embedded Mermaid diagram showing task sequence.

**Acceptance Scenarios**:

1. **Given** the `--graph` flag, **When** a playbook is processed, **Then** an optional Mermaid diagram is included showing all top-level tasks in sequence order.

2. **Given** a playbook with pre_tasks, tasks, and post_tasks, **When** the graph is rendered, **Then** all three stages appear in the diagram in the correct execution order.

---

### User Story 5 - CLI Error Messages Guide Troubleshooting (Priority: P1)

A user provides a path to a non-existent file or a malformed YAML file. They receive a clear error message that explains what went wrong and how to fix it.

**Why this priority**: Error handling directly impacts user experience. Per constitution "fail loudly in CI", non-zero exit codes must be reliable and messages must be clear.

**Independent Test**: Can run `anodyse invalid.yml` and receive exit code 1 with a message that identifies the problem (file not found, YAML parse error, etc.).

**Acceptance Scenarios**:

1. **Given** a path to a non-existent file, **When** processed, **Then** exit code 1 is returned with a message like "File not found: <path>".

2. **Given** a YAML file with syntax errors, **When** processed, **Then** exit code 1 is returned with a YAML error message indicating the line and nature of the error.

3. **Given** a directory with no valid playbooks or roles, **When** processed, **Then** exit code 1 is returned with a message explaining no valid content was found.

---

### Edge Cases

- What happens if a playbook references a role but the role directory does not exist?
- What happens if a `@param` annotation references a variable that does not exist in defaults/vars?
- What happens if YAML contains duplicate task names?
- What happens if a playbook/role name contains special characters that cannot be slugified?
- What happens if the output directory does not exist?
- What happens if existing .bak files already exist (multiple runs)?
- What happens if annotation values contain special characters or newlines?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: CLI MUST accept a target path (file or directory) as a positional argument and process it to generate documentation.

- **FR-002**: CLI MUST support the following options: `--output` (directory path), `--graph` (enable Mermaid diagrams), `--no-backup` (skip backing up existing files), `--verbose` (print detailed output), `--format` (output format, default: markdown).

- **FR-003**: YAML parser MUST load and validate YAML files using ruamel.yaml and return a typed PlaybookData or RoleData dataclass (never a raw dict).

- **FR-004**: Parser MUST identify target type (playbook or role) based on file/directory structure and extract the appropriate data (tasks, defaults, vars, meta).

- **FR-005**: Annotation extractor MUST scan YAML comments for lines matching `# @<tag> <value>` and attach extracted annotations to dataclass fields.

- **FR-006**: Extractor MUST support annotation tags: `@title`, `@description`, `@param` (repeatable), `@warning` (repeatable), `@example` (repeatable), `@tag` (repeatable).

- **FR-007**: Extractor MUST set description fields to None (not generate/invent) when `@description` annotations are absent, per constitution annotation-driven principle.

- **FR-008**: Extractor MUST emit a warning to stdout when mandatory annotations (`@title`, `@description`) are missing but continue processing (graceful degradation).

- **FR-009**: Markdown renderer MUST consume a populated dataclass and render a Markdown document using Jinja2 templates from `anodyse/templates/`.

- **FR-010**: Renderer MUST produce output pages including: title, description (or "Undocumented" notice), parameters table, warnings, usage examples, task summary, and optional Mermaid diagram.

- **FR-011**: Renderer MUST support user-overridable templates by checking for custom templates in `.anodyse/templates/` directory at invocation time.

- **FR-012**: Output handler MUST generate one Markdown file per playbook/role with slugified filenames (lowercase, hyphens, no special characters).

- **FR-013**: Output handler MUST generate an `index.md` listing all parsed items with their `@tag` values and one-line descriptions (mandatory output).

- **FR-014**: Output handler MUST back up existing files as `<filename>.bak` before overwriting, unless `--no-backup` flag is passed.

- **FR-015**: Output handler MUST create the output directory if it does not exist.

- **FR-016**: All output files MUST be UTF-8 encoded.

- **FR-017**: CLI MUST exit with code 0 on success, code 1 on parse errors, and code 2 when warnings are emitted but degraded output is produced.

### Key Entities

- **Playbook**: A single .yml file defining a sequence of tasks to run against hosts. Contains tasks, roles, tags, variables, and metadata.

- **Role**: A directory structure (tasks/, defaults/, vars/, meta/, handlers/) defining reusable automation units.

- **Task**: A named Ansible operation with a module type and arguments. Part of a playbook or role.

- **Annotation**: A structured comment in YAML format (`# @tag value`) providing user-facing documentation hints.

- **PlaybookData**: Python dataclass representing parsed playbook structure with extracted annotations and task list.

- **RoleData**: Python dataclass representing parsed role structure with extracted annotations, tasks, and variables.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can generate documentation for a 20-task playbook in under 2 seconds from a single CLI command.

- **SC-002**: Generated Markdown is valid UTF-8 and renders without errors in standard Markdown viewers (GitHub, GitLab, MkDocs, etc.).

- **SC-003**: A playbook with no annotations produces usable skeleton documentation (task names visible, "Undocumented" notices clear but not blocking).

- **SC-004**: Fully-annotated playbooks produce documentation where all annotations (title, description, params, warnings, examples) appear in the output exactly as provided.

- **SC-005**: 100% of CLI error paths return the correct exit code (0 for success, 1 for parse errors, 2 for warnings).

- **SC-006**: Error messages are human-readable and include the file path and specific problem (not internal tracebacks).

- **SC-007**: The generated index.md successfully lists all playbooks/roles from a multi-item run with no duplicates or omissions.

- **SC-008**: Template files are user-replaceable — users can override default templates and see changes reflected in output.

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

---

## Out of Scope (v1)

- Web server or UI for browsing docs.
- AI-generated descriptions for undocumented annotations.
- External API calls or network features.
- Encrypted vault support.
- Windows path handling.
- Multi-playbook role dependencies or execution graphs.
- Interactive CLI mode (only batch mode).
- PDF or HTML output (Markdown only).
