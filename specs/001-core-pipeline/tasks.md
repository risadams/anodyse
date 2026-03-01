# Tasks: Anodyse MVP — Core Parse-Extract-Render Pipeline

**Feature**: Core Parse-Extract-Render Pipeline (MVP)  
**Branch**: 001-core-pipeline  
**Total Tasks**: 25  
**Estimated Duration**: 3-5 days (sequential) / 2-3 days (with parallelization)

---

## Phase 1: Project Scaffold (Stage 0)

Project foundation and development environment setup. All tasks must complete before moving to Stage 1.

**Stage Goal**: Establish project structure, dependencies, and CI/CD pipeline  
**Independent Test Criteria**: `pip install -e .` succeeds; `pytest --cov` runs; `ruff check` passes

### Tasks

- [ ] T001 Create pyproject.toml with project metadata and dependencies
  - **Complexity**: small
  - **Dependencies**: None
  - **File Path**: pyproject.toml
  - **Checklist**:
    - [ ] Metadata: name=anodyse, version=0.1.0, Python>=3.11
    - [ ] Core dependencies: click, ruamel.yaml, jinja2
    - [ ] Dev dependencies: pytest, pytest-cov, ruff
    - [ ] Entry point: anodyse = anodyse.cli:main
    - [ ] Build system: setuptools, wheel

- [ ] T002 Create anodyse package directory structure with module stubs
  - **Complexity**: small
  - **Dependencies**: T001
  - **File Paths**: anodyse/__init__.py, anodyse/cli.py, anodyse/parser.py, anodyse/extractor.py, anodyse/renderer.py, anodyse/discovery.py, anodyse/models.py, anodyse/exceptions.py, anodyse/output.py
  - **Checklist**:
    - [ ] Create anodyse/__init__.py with package docstring and version
    - [ ] Create all module stubs with module-level docstrings
    - [ ] Each module contains: docstring, pass statement
    - [ ] All modules importable without errors

- [ ] T003 Create templates directory with Jinja2 template stubs
  - **Complexity**: small
  - **Dependencies**: T002
  - **File Paths**: anodyse/templates/playbook.md.j2, anodyse/templates/role.md.j2, anodyse/templates/index.md.j2
  - **Checklist**:
    - [ ] Create anodyse/templates/ directory
    - [ ] Create playbook.md.j2 with minimal structure (stub)
    - [ ] Create role.md.j2 with minimal structure (stub)
    - [ ] Create index.md.j2 with minimal structure (stub)

- [ ] T004 Create test fixtures for parser and discovery testing
  - **Complexity**: small
  - **Dependencies**: T002
  - **File Paths**: tests/fixtures/playbook_annotated.yml, tests/fixtures/playbook_unannotated.yml, tests/fixtures/role_sample/
  - **Checklist**:
    - [ ] tests/fixtures/playbook_annotated.yml: valid playbook with @title, @description, @param, @warning, @example, @tag annotations; 3+ tasks; vars block
    - [ ] tests/fixtures/playbook_unannotated.yml: valid playbook structure without @ annotations
    - [ ] tests/fixtures/role_sample/tasks/main.yml: sample task list
    - [ ] tests/fixtures/role_sample/defaults/main.yml: role defaults
    - [ ] tests/fixtures/role_sample/vars/main.yml: role vars
    - [ ] tests/fixtures/role_sample/meta/main.yml: role metadata

- [ ] T005 Create GitHub Actions CI workflow configuration
  - **Complexity**: small
  - **Dependencies**: T001
  - **File Path**: .github/workflows/ci.yml
  - **Checklist**:
    - [ ] Triggers: push (all branches), pull_request
    - [ ] Matrix: Python 3.11, 3.12
    - [ ] Checkout code
    - [ ] Setup Python
    - [ ] Install dependencies with pip
    - [ ] Ruff lint check (exit if fails)
    - [ ] Pytest with coverage report
    - [ ] Coverage threshold enforced: ≥80%
    - [ ] Artifacts: coverage reports

- [ ] T006 Create ruff linter configuration in pyproject.toml
  - **Complexity**: small
  - **Dependencies**: T001
  - **File Path**: pyproject.toml
  - **Checklist**:
    - [ ] Add [tool.ruff] section to pyproject.toml
    - [ ] Configure line-length = 100
    - [ ] Enable rule sets: E (errors), W (warnings), F (pyflakes), I (isort imports)
    - [ ] Test: `ruff check anodyse/` returns no errors

---

## Phase 2: Data Models (Stage 1)

Core data structures for playbook, role, and index representations.

**Stage Goal**: Establish data model foundation for all downstream modules  
**Independent Test Criteria**: All dataclasses importable; fields match data-model.md exactly

### Tasks

- [ ] T007 Implement dataclasses in models.py: TaskData, PlaybookData, RoleData, IndexEntry
  - **Complexity**: small
  - **Dependencies**: T002
  - **File Path**: anodyse/models.py
  - **Checklist**:
    - [ ] TaskData: name, description, doc_tags, tags (all fields with type hints)
    - [ ] PlaybookData: name, description, hosts, doc_tags, tags, tasks, vars, pre_tasks, post_tasks, roles_referenced (all fields with type hints)
    - [ ] RoleData: name, description, doc_tags, tags, tasks, defaults, vars, metadata (all fields with type hints)
    - [ ] IndexEntry: source_path, source_type, name, description, doc_tags (all fields with type hints)
    - [ ] All fields populated from data-model.md
    - [ ] All classes use @dataclass decorator
    - [ ] No business logic — pure data structures
    - [ ] Test: `from anodyse.models import TaskData, PlaybookData, RoleData, IndexEntry` succeeds

---

## Phase 3: Exception Handling (Stage 2)

Custom exception and warning classes for error handling.

**Stage Goal**: Establish exception hierarchy for downstream error handling  
**Independent Test Criteria**: All exceptions importable; can be raised and caught

### Tasks

- [ ] T008 Implement exceptions.py with ParseError, AnnotationWarning, ManifestError
  - **Complexity**: small
  - **Dependencies**: T002
  - **File Path**: anodyse/exceptions.py
  - **Checklist**:
    - [ ] ParseError(Exception): raised on YAML parse failures, with descriptive messages
    - [ ] AnnotationWarning(Warning): raised when @title or @description missing
    - [ ] ManifestError(Exception): raised on invalid .anodyse.yml schema
    - [ ] Each class: __init__(self, message: str) with docstring
    - [ ] Test: All three can be raised and caught

---

## Phase 4: Discovery Module (Stage 3)

Playbook and role discovery via directory scan or .anodyse.yml manifest.

**Stage Goal**: Enable robust discovery of Ansible playbooks and roles  
**Independent Test Criteria**: Directory scan finds playbooks/roles; manifest parsing works; manifest precedence respected

### Tasks

- [ ] T009 Implement discover() in discovery.py
  - **Complexity**: medium
  - **Dependencies**: T007, T008
  - **File Path**: anodyse/discovery.py
  - **Checklist**:
    - [ ] discover(target: str, config_path: str | None = None) -> list[str]
    - [ ] Mode 1 (directory scan):
      - [ ] Recursively walk target directory
      - [ ] Identify playbooks: .yml/.yaml files with top-level `hosts:` key
      - [ ] Identify roles: directories containing tasks/main.yml
      - [ ] Return list of full paths to discovered playbooks/roles
    - [ ] Mode 2 (manifest):
      - [ ] If config_path provided, read .anodyse.yml from specified path
      - [ ] Validate manifest schema against manifest-schema.md
      - [ ] Parse include and exclude lists
      - [ ] Apply include/exclude filters to discovered paths
      - [ ] Raise ManifestError on invalid schema
      - [ ] Emit AnnotationWarning for declared paths that do not exist (non-fatal)
    - [ ] Manifest mode takes precedence over directory scan when present
    - [ ] Return empty list if no playbooks/roles found (non-fatal)

---

## Phase 5: YAML Parser (Stage 4)

YAML parsing for playbooks and roles with error handling.

**Stage Goal**: Extract structured data from Ansible playbooks and roles  
**Independent Test Criteria**: All parsing functions return correct dataclasses; ParseError raised on malformed YAML

### Tasks

- [ ] T010 Implement detect_type() in parser.py
  - **Complexity**: small
  - **Dependencies**: T007, T008
  - **File Path**: anodyse/parser.py
  - **Checklist**:
    - [ ] detect_type(path: str) -> Literal["playbook", "role", "unknown"]
    - [ ] Heuristics:
      - [ ] If .yml/.yaml with top-level `hosts:`, type = "playbook"
      - [ ] If directory contains tasks/main.yml, type = "role"
      - [ ] Otherwise, type = "unknown"
    - [ ] Test: detect_type() on fixtures returns correct types

- [ ] T011 Implement parse_playbook() in parser.py
  - **Complexity**: medium
  - **Dependencies**: T010
  - **File Path**: anodyse/parser.py
  - **Checklist**:
    - [ ] parse_playbook(path: str) -> PlaybookData
    - [ ] Use ruamel.yaml for YAML loading (round-trip mode)
    - [ ] Extract fields: name, hosts, tasks, tags, vars, pre_tasks, post_tasks, roles referenced
    - [ ] Preserve raw comments and text for extractor (store in source_text parameter)
    - [ ] Raise ParseError with descriptive message on malformed YAML
    - [ ] Return PlaybookData instance, never raw dict
    - [ ] Test: parse_playbook() on annotated fixture returns PlaybookData

- [ ] T012 Implement parse_role() in parser.py
  - **Complexity**: medium
  - **Dependencies**: T010
  - **File Path**: anodyse/parser.py
  - **Checklist**:
    - [ ] parse_role(path: str) -> RoleData
    - [ ] Load: tasks/main.yml (required), defaults/main.yml, vars/main.yml, meta/main.yml
    - [ ] Raise ParseError if tasks/main.yml missing or malformed
    - [ ] Extract fields: name, description, tags, tasks, defaults, vars, metadata
    - [ ] Return RoleData instance, never raw dict
    - [ ] Test: parse_role() on role_sample fixture returns RoleData

---

## Phase 6: Annotation Extractor (Stage 5)

Extraction of @-prefixed annotations from YAML comments.

**Stage Goal**: Parse structured metadata from comments using @tag syntax  
**Independent Test Criteria**: All @-tags extracted correctly; AnnotationWarning emitted for missing titles/descriptions

### Tasks

- [ ] T013 Implement extract() in extractor.py
  - **Complexity**: medium
  - **Dependencies**: T007, T008
  - **File Path**: anodyse/extractor.py
  - **Checklist**:
    - [ ] extract(data: PlaybookData | RoleData, source_text: str) -> PlaybookData | RoleData
    - [ ] Scan source_text for pattern: `# @<tag> <value>`
    - [ ] Support tags: @title, @description, @param, @warning, @example, @tag
    - [ ] @title and @description: single value only (first occurrence wins)
    - [ ] @param format: `@param <name>: <description>` (repeatable, accumulate list)
    - [ ] @warning, @example, @tag: repeatable (accumulate lists)
    - [ ] Set title/description to None if absent (do NOT infer)
    - [ ] Set doc_tags list to extracted @tag values
    - [ ] Emit AnnotationWarning if @title or @description missing
    - [ ] Scope (v1): file-level annotations only (top of playbook/role)
    - [ ] Populate extracted data back into PlaybookData or RoleData
    - [ ] Return updated dataclass instance
    - [ ] Test: extract() with full annotations returns populated fields

---

## Phase 7: Markdown Renderer (Stage 6)

Jinja2-based rendering of parsed data to Markdown documentation.

**Stage Goal**: Generate structured Markdown documentation from parsed playbooks/roles  
**Independent Test Criteria**: All templates load; Markdown output includes required sections; Mermaid diagrams optional

### Tasks

- [ ] T014 Implement Jinja2 template loader in renderer.py
  - **Complexity**: small
  - **Dependencies**: T003, T007
  - **File Path**: anodyse/renderer.py
  - **Checklist**:
    - [ ] Implement template loader with cascading lookup:
      - [ ] Priority 1: .anodyse/templates/ in current working directory
      - [ ] Priority 2: anodyse/templates/ (package default)
    - [ ] Use jinja2.Environment with FileSystemLoader or PackageLoader
    - [ ] Return jinja2.Environment instance for reuse
    - [ ] Test: Template loader finds both custom and default templates

- [ ] T015 Implement render_playbook() in renderer.py
  - **Complexity**: medium
  - **Dependencies**: T014
  - **File Path**: anodyse/renderer.py
  - **Checklist**:
    - [ ] render_playbook(data: PlaybookData, graph: bool = False) -> str
    - [ ] Output sections (in order):
      - [ ] Title (from data.name or "Untitled Playbook")
      - [ ] Description (from data.description or "No documentation provided")
      - [ ] Parameters table (from data fields)
      - [ ] Warnings section (if data.warnings populated)
      - [ ] Usage Examples (if data.examples populated)
      - [ ] Task Summary
      - [ ] Mermaid diagram (if graph=True)
    - [ ] Populate playbook.md.j2 with full template logic (no longer stub)
    - [ ] Return rendered Markdown string
    - [ ] Test: render_playbook() output contains all required sections

- [ ] T016 Implement render_role() in renderer.py
  - **Complexity**: medium
  - **Dependencies**: T014
  - **File Path**: anodyse/renderer.py
  - **Checklist**:
    - [ ] render_role(data: RoleData, graph: bool = False) -> str
    - [ ] Output sections: same as render_playbook (title, description, parameters, warnings, examples, task list, diagram)
    - [ ] Populate role.md.j2 with full template logic (no longer stub)
    - [ ] Return rendered Markdown string
    - [ ] Test: render_role() output contains all required sections

- [ ] T017 Implement render_index() in renderer.py
  - **Complexity**: small
  - **Dependencies**: T014
  - **File Path**: anodyse/renderer.py
  - **Checklist**:
    - [ ] render_index(entries: list[IndexEntry]) -> str
    - [ ] Output: Markdown table of all parsed items
    - [ ] Columns: source_type, name, description (first line), index_file_link
    - [ ] Populate index.md.j2 with table generation logic (no longer stub)
    - [ ] Return rendered Markdown string
    - [ ] Test: render_index() produces valid Markdown table

---

## Phase 8: Output File Handler (Stage 7)

File writing with backup and directory creation.

**Stage Goal**: Output rendered Markdown to files with safe overwrite handling  
**Independent Test Criteria**: Output files created; existing files backed up; directory created if needed

### Tasks

- [ ] T018 Implement write_output() in output.py
  - **Complexity**: small
  - **Dependencies**: T008
  - **File Path**: anodyse/output.py
  - **Checklist**:
    - [ ] write_output(content: str, output_path: str, no_backup: bool = False) -> None
    - [ ] Slugify filename: lowercase all, replace spaces/special chars with hyphens
    - [ ] If output file exists and no_backup=False:
      - [ ] Create backup as <filename>.bak
      - [ ] Don't fail if backup exists (overwrite silently)
    - [ ] If no_backup=True, overwrite without backup (dangerous flag)
    - [ ] Create output directory (and parents) if it does not exist
    - [ ] Write content to output_path as UTF-8
    - [ ] Handle filesystem errors gracefully (raise descriptive exceptions)
    - [ ] Test: write_output() creates file and backup

---

## Phase 9: CLI Entry Point (Stage 8)

Click-based command-line interface wiring all components.

**Stage Goal**: Implement complete CLI with options, exit codes, and error handling  
**Independent Test Criteria**: CLI accepts valid playbook path; exit codes correct; help text displays

### Tasks

- [ ] T019 Implement CLI in cli.py
  - **Complexity**: medium
  - **Dependencies**: T009, T011, T012, T013, T015, T016, T017, T018
  - **File Path**: anodyse/cli.py
  - **Checklist**:
    - [ ] Framework: Click
    - [ ] Command signature: `anodyse [OPTIONS] <target>`
    - [ ] Options per contracts/cli-command.md:
      - [ ] --output / -o PATH: output directory
      - [ ] --graph: include Mermaid diagram in output (flag)
      - [ ] --no-backup: skip backup on overwrite (flag)
      - [ ] --config PATH: path to .anodyse.yml manifest
      - [ ] --verbose / -v: verbose output (flag)
      - [ ] --format {markdown,json}: output format (default: markdown)
    - [ ] Exit codes:
      - [ ] 0: success
      - [ ] 1: parse error (raise on ParseError)
      - [ ] 2: annotation warnings (raise on AnnotationWarning, but complete pipeline)
    - [ ] No business logic in CLI:
      - [ ] Delegate all logic to core modules (discovery, parser, extractor, renderer, output)
    - [ ] Pipeline mode detection:
      - [ ] Detect non-TTY stdout (e.g., piped to file)
      - [ ] In pipeline mode: suppress warning output but still raise exit code 2
    - [ ] Verbose mode output:
      - [ ] Print discovered files count
      - [ ] Print parsed items count
      - [ ] Print annotations found (title/description/params/warnings/examples/tags)
      - [ ] Print output files written
    - [ ] Error handling:
      - [ ] Catch ParseError, AnnotationWarning, ManifestError, filesystem errors
      - [ ] Print human-readable error messages to stderr
      - [ ] Raise corresponding exit code
    - [ ] Test: CLI accepts playbook path and runs full pipeline

---

## Phase 10: Test Suite (Stage 9)

Comprehensive unit and integration tests with ≥80% coverage.

**Stage Goal**: All public functions tested, exit codes verified, full pipeline validated  
**Independent Test Criteria**: pytest runs successfully; coverage ≥80%; all assertions pass

### Tasks

- [ ] T020 Unit tests — parser module
  - **Complexity**: medium
  - **Dependencies**: T011, T012, T004
  - **File Path**: tests/test_parser.py
  - **Checklist**:
    - [ ] Test parse_playbook() with annotated fixture → returns PlaybookData
    - [ ] Test parse_playbook() with unannotated fixture → returns PlaybookData
    - [ ] Test parse_playbook() with malformed YAML → raises ParseError
    - [ ] Test parse_role() with role_sample fixture → returns RoleData
    - [ ] Test detect_type() for playbook (hosts key) → "playbook"
    - [ ] Test detect_type() for role (tasks/main.yml) → "role"
    - [ ] Test detect_type() for unknown → "unknown"
    - [ ] Coverage: 100% of parser public functions

- [ ] T021 Unit tests — extractor module
  - **Complexity**: medium
  - **Dependencies**: T013, T004
  - **File Path**: tests/test_extractor.py
  - **Checklist**:
    - [ ] Test extract() with full annotations present → all fields populated
    - [ ] Test extract() with partial annotations (missing @description) → title populated, description=None
    - [ ] Test extract() with no annotations → fields=None/empty, AnnotationWarning emitted
    - [ ] Test @param repeatable parsing → accumulates list of params
    - [ ] Test @tag repeatable parsing → accumulates list of doc_tags
    - [ ] Test single @title and @description (first wins)
    - [ ] Coverage: 100% of extractor public functions

- [ ] T022 Unit tests — renderer module
  - **Complexity**: medium
  - **Dependencies**: T015, T016, T017
  - **File Path**: tests/test_renderer.py
  - **Checklist**:
    - [ ] Test render_playbook() output contains required sections
    - [ ] Test render_role() output contains required sections
    - [ ] Test render_index() output is valid Markdown table
    - [ ] Test Mermaid diagram present when graph=True
    - [ ] Test Mermaid diagram absent when graph=False
    - [ ] Test template loader finds custom templates (.anodyse/templates/)
    - [ ] Test template loader falls back to default templates
    - [ ] Coverage: 100% of renderer public functions

- [ ] T023 Unit tests — discovery module
  - **Complexity**: medium
  - **Dependencies**: T009, T004
  - **File Path**: tests/test_discovery.py
  - **Checklist**:
    - [ ] Test discover() directory scan mode identifies playbooks correctly
    - [ ] Test discover() directory scan mode identifies roles correctly
    - [ ] Test discover() manifest mode applies include filters
    - [ ] Test discover() manifest mode applies exclude filters
    - [ ] Test discover() manifest precedence over directory scan
    - [ ] Test discover() missing declared manifest path → emits warning, non-fatal
    - [ ] Test discover() invalid manifest schema → raises ManifestError
    - [ ] Coverage: 100% of discovery public functions

- [ ] T024 Unit tests — output module
  - **Complexity**: small
  - **Dependencies**: T018
  - **File Path**: tests/test_output.py
  - **Checklist**:
    - [ ] Test write_output() creates file
    - [ ] Test write_output() creates backup when file exists and no_backup=False
    - [ ] Test write_output() skips backup when no_backup=True
    - [ ] Test write_output() creates output directory if missing
    - [ ] Test write_output() slugifies filename correctly
    - [ ] Coverage: 100% of output public functions

- [ ] T025 Integration test — full pipeline
  - **Complexity**: large
  - **Dependencies**: T020, T021, T022, T023, T024, T019
  - **File Path**: tests/test_integration.py
  - **Checklist**:
    - [ ] Setup: fixtures available (annotated playbook, role_sample)
    - [ ] Execute full pipeline:
      - [ ] discover() → identify playbook fixture
      - [ ] parse_playbook() → extract structured data
      - [ ] extract() → parse annotations
      - [ ] render_playbook() → generate Markdown
      - [ ] write_output() → save to temp directory
    - [ ] Assertions:
      - [ ] Output file exists
      - [ ] Output contains title from @title annotation
      - [ ] Output contains description from @description annotation
      - [ ] Output contains parameters table
      - [ ] Output contains task list
      - [ ] Index file (index.md) generated
    - [ ] Test CLI entry point with `anodyse <fixture-path>`
    - [ ] Assert exit code 0 on success
    - [ ] Assert exit code 2 on warnings (missing @title/@description)
    - [ ] Test graph=True generates Mermaid diagram
    - [ ] Coverage: 80% overall (track with pytest-cov)

---

## Implementation Strategy

### MVP Scope (Recommended for Phase 1)
**Timeline**: 3-5 days with focused team  
**Achievable by**: End of sprint

1. **Stages 0-2** (Days 1): Project scaffold + models + exceptions (~3 hours)
2. **Stage 3-4** (Days 1-2): Discovery + parser (~4 hours)
3. **Stage 5** (Day 2): Extractor (~3 hours)
4. **Stage 6-7** (Day 3): Renderer + output (~5 hours)
5. **Stage 8** (Day 3): CLI integration (~3 hours)
6. **Stage 9** (Days 4-5): Tests and coverage (~8 hours)

### Parallelization Opportunities

**Within Stage 0** (can run in parallel):
- T002, T003, T004, T005 can execute after T001 completes (no inter-dependencies)

**Within Stage 9** (can run in parallel):
- T020, T021, T022, T023, T024 can execute in parallel (independent test modules)
- T025 must wait for all unit tests (T020-T024) to complete

**Cross-Stage Parallelization**:
- Stage 0 blocks all other stages (strict dependency)
- Once T007-T008 complete (by end Stage 1-2), Stage 3-9 can proceed in strict order
- No parallelization possible between Stages 3-9 (each stage depends on prior output)

### Complexity Distribution
- **Small (8 tasks)**: T001, T002, T003, T004, T005, T006, T007, T008, T010, T014, T017, T018, T024
- **Medium (11 tasks)**: T009, T011, T012, T013, T015, T016, T019, T020, T021, T022, T023
- **Large (1 task)**: T025

### Definition of Done

Each task complete when:
1. ✅ Code written to specification
2. ✅ Type hints on all public functions
3. ✅ Docstrings on all classes and public functions
4. ✅ Imports from dependencies work without errors
5. ✅ No ruff linting errors (`ruff check` passes)
6. ✅ Fixtures in place (if task creates them)
7. ✅ Tests pass (for Stage 9) or staging tests can import module (for Stages 0-8)

### Quality Gates

- [ ] All dependencies satisfied (click, ruamel.yaml, jinja2)
- [ ] No external API calls at runtime
- [ ] No credentials or hostnames in output
- [ ] All public functions type-hinted and documented
- [ ] Test coverage ≥80% (Stage 9)

---

## Dependencies Graph

```
T001 (pyproject.toml)
├─→ T002 (package structure)
│   ├─→ T003 (templates)
│   ├─→ T004 (fixtures)
│   └─→ T008 (exceptions)
├─→ T005 (CI workflow)
└─→ T006 (ruff config)

T007 (models) [depends on T002]
T008 (exceptions) [depends on T002]

T009 (discover) [depends on T007, T008]
T010 (detect_type) [depends on T007, T008]
├─→ T011 (parse_playbook) [depends on T010]
└─→ T012 (parse_role) [depends on T010]

T013 (extract) [depends on T007, T008]

T003 (templates) [depends on T002]
├─→ T014 (template loader) [depends on T003, T007]
├─→ T015 (render_playbook) [depends on T014]
├─→ T016 (render_role) [depends on T014]
└─→ T017 (render_index) [depends on T014]

T018 (write_output) [depends on T008]

T019 (CLI) [depends on T009, T011, T012, T013, T015, T016, T017, T018]

T020 (parser tests) [depends on T011, T012, T004]
T021 (extractor tests) [depends on T013, T004]
T022 (renderer tests) [depends on T015, T016, T017]
T023 (discovery tests) [depends on T009, T004]
T024 (output tests) [depends on T018]
T025 (integration test) [depends on T020, T021, T022, T023, T024, T019]
```

---

## Checklist: Task Completeness

- [x] All 25 tasks defined
- [x] Each task has complexity rating (small/medium/large)
- [x] Each task has explicit dependencies
- [x] Each task has specific file paths
- [x] Stage ordering respected (0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9)
- [x] No circular dependencies
- [x] Parallelization opportunities documented
- [x] MVP scope identified (Stages 0-9, all tasks)
- [x] Quality gates defined
- [x] Dependencies graph complete

---

**Next Action**: Begin with Task T001 (Create pyproject.toml). All Stage 0 tasks can proceed after T001 completes.
