# anodyse Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-01

## Active Technologies
- Python 3.11+ + `click`, `ruamel.yaml`, `jinja2` (002-task-comments-todos)
- N/A (filesystem input/output only) (002-task-comments-todos)
- YAML (GitHub Actions, GitLab CI) + Markdown documentation + Anodyse CLI (existing), GitHub Actions runtime, GitLab Runner, Jinja2 templates (003-ci-workflow-setup)
- GitHub Pages or GitLab Pages for generated docs (optional, user-configurable) (003-ci-workflow-setup)

- Python 3.11+ + click (CLI framework), ruamel.yaml (YAML parsing with comment preservation), jinja2 (template rendering) (001-core-pipeline)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 003-ci-workflow-setup: Added YAML (GitHub Actions, GitLab CI) + Markdown documentation + Anodyse CLI (existing), GitHub Actions runtime, GitLab Runner, Jinja2 templates
- 002-task-comments-todos: Added Python 3.11+ + `click`, `ruamel.yaml`, `jinja2`

- 001-core-pipeline: Added Python 3.11+ + click (CLI framework), ruamel.yaml (YAML parsing with comment preservation), jinja2 (template rendering)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
