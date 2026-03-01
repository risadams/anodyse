<!-- 
SYNC IMPACT REPORT
==================
Version Change: INITIAL → 1.0.0
Ratification Date: 2026-03-01
Last Amended: 2026-03-01

SECTIONS CREATED:
✅ Core Principles (5 principles)
✅ Code Standards
✅ Architecture Rules
✅ Output Rules
✅ Testing Requirements
✅ Versioning & Compatibility
✅ What Anodyse Must Never Do
✅ Governance

TEMPLATES VERIFIED:
✅ plan-template.md - Aligned (includes Constitution Check gate)
✅ spec-template.md - Aligned (no conflicts)
✅ tasks-template.md - Aligned (task organization conforms)
✅ agent-file-template.md - Aligned (generic, no conflicts)
✅ checklist-template.md - Aligned (generic, no conflicts)
✅ README.md - Aligned (already references annotation-driven and user-first principles)

NO INTENTIONAL PLACEHOLDERS DEFERRED.
All bracket tokens have been replaced with concrete project values.
-->

# Anodyse Constitution

## Core Principles

### I. User-First Output
Documentation is written for platform consumers, not Ansible engineers. Every output decision
prioritises clarity for a non-technical reader. Anodyse assumes minimal technical background and
defaults to simple, clear explanations over detailed technical accuracy when the two conflict.

### II. Annotation-Driven
Anodyse does not invent descriptions from YAML alone. If a `@description` annotation is absent,
the output clearly indicates the field is undocumented rather than hallucinating intent. This
preserves accuracy and prevents misleading documentation.

### III. Graceful Degradation
If a playbook has no annotations, Anodyse still produces a useful skeleton doc with available
structural data (task names, variables, tags). Incomplete documentation is better than no
documentation, and the system fails predictably without data loss.

### IV. Fail Loudly in CI, Fail Gently on the CLI
Non-zero exit codes on errors when running in pipeline mode (CI/CD); warnings with continued
execution in interactive mode (local CLI). This allows automation to catch issues while keeping
local development workflows unblocked.

### V. Convention Over Configuration
Sensible defaults for all options; config file support for overrides, not required for basic
usage. New users succeed without reading extensive configuration docs. Advanced users can
customise as needed.

## Code Standards

- Python 3.11+ only
- Type hints required on all public functions and methods
- All modules must have docstrings
- Follow PEP 8; enforce with ruff
- Tests required for all parsers and renderers; use pytest
- No external API calls — Anodyse must work fully offline
- Dependencies must be minimal and well-maintained

## Architecture Rules

- Separate concerns strictly: parsing, enrichment, and rendering are distinct pipeline stages
- Parsers return plain Python dataclasses, never raw dicts
- Renderers consume dataclasses only — no YAML or raw strings passed into template context
- Templates live in a dedicated `/templates` directory and are user-overridable
- CLI commands must not contain business logic — delegate to core modules

## Output Rules

- All output is UTF-8 Markdown
- File naming follows the playbook/role name, slugified
- Mermaid diagrams are optional and toggled via a `--graph` flag
- A docs index page (`index.md`) is always generated summarising all parsed playbooks/roles
- Existing files are backed up before overwrite unless `--no-backup` is passed

## Testing Requirements

- Unit tests for: YAML parser, annotation extractor, Jinja2 renderer
- Integration test: full parse-to-output pipeline on a fixture playbook
- CI must run tests on Python 3.11 and 3.12
- Coverage threshold: 80% minimum

## Versioning & Compatibility

- Semantic versioning (semver)
- Changelog maintained in CHANGELOG.md

## What Anodyse Must Never Do

- Modify source playbook or role files
- Make assumptions about undocumented intent
- Require network access at runtime
- Produce output that exposes internal platform architecture details (e.g., hostnames,
  credentials referenced in vars)

## Governance

All development MUST comply with this constitution. PRs must verify adherence to all principles
and standards before merge. Amendment process: proposal → discussion → consensus → documentation →
migration plan where applicable.

**Version**: 1.0.0 | **Ratified**: 2026-03-01 | **Last Amended**: 2026-03-01
