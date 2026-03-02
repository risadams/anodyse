# Anodyse

## Overview

Anodyse is a CLI tool that auto-generates user-facing documentation from Ansible
playbooks and roles.

The goal is NOT to produce technical READMEs for Ansible authors — the output is
aimed at platform users who consume playbooks without needing to understand the
underlying YAML. Documentation should be clear, structured, and human-readable.

## Core Capabilities

- Parse Ansible playbooks and role structures (tasks, defaults, vars, meta)
- Extract inline annotations using a custom `@` comment schema
- Generate structured Markdown documentation pages per playbook/role
- Render Mermaid flow diagrams showing playbook execution order
- Publish output to a configurable destination (local path, or a docs site directory)
- Run as a standalone CLI or as a step in a CI/CD pipeline

## Annotation Schema

Anodyse reads structured comments from playbook and role YAML files:

```yaml
# @title        Human-readable title
# @description  Plain-language description of what this playbook does
# @param        <name>: <description>
# @warning      Any caveats or pre-requisites users must know
# @example      An illustrative usage example
# @tag          Categorisation tag(s) for the docs index
```

## Tech Stack

- Language: Python 3.11+
- CLI framework: Click
- YAML parsing: ruamel.yaml
- Templating: Jinja2
- Output format: Markdown (with optional Mermaid diagrams)
- Packaging: pip-installable, with a pyproject.toml

## Build and Install

### Prerequisites

- Python 3.11+
- pip

### Install for local development

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -e .[dev]
```

### Run tests and lint

```bash
pytest
ruff check .
```

### Build distributable packages

```bash
python -m pip install build
python -m build
```

Build artifacts are created in `dist/` (`.whl` and `.tar.gz`).

### Install from built wheel

```bash
python -m pip install dist/anodyse-0.1.0-py3-none-any.whl
```

## Quickstart with Sample Files

Use the sample playbooks in `samples/` to test the full parse → extract → render flow.

### 1) Install and verify CLI

```bash
python -m pip install -e .
anodyse --help
```

### 2) Generate docs from one sample playbook

```bash
anodyse samples/web-server/deploy-nginx.yml --output docs/samples --verbose
```

### 3) Generate docs from all sample folders

```bash
anodyse samples/ --output docs/samples --graph --verbose
```

### 4) Check generated output

Expected output files include:

- `docs/samples/index.md`
- One `.md` page per discovered sample playbook/role

### Notes

- `--graph` adds Mermaid flow diagrams.
- Exit code `0` = success, `1` = parse/error failure, `2` = docs generated with warnings.
- To avoid `.bak` files on overwrite, add `--no-backup`.

## Custom Template Overrides (`/.anodyse/templates/`)

Anodyse supports local Jinja2 template overrides from your current working directory.

Template lookup order:

1. `./.anodyse/templates/`
2. Built-in package templates (`anodyse/templates/`)

Supported override filenames:

- `playbook.md.j2`
- `role.md.j2`
- `index.md.j2`

### Quick usage

```bash
mkdir -p .anodyse/templates
cp samples/anodyse-template-overrides/templates/*.j2 .anodyse/templates/
anodyse samples/web-server/deploy-nginx.yml --output docs/custom-templates --verbose
```

PowerShell (Windows):

```powershell
New-Item -ItemType Directory -Path .anodyse/templates -Force | Out-Null
Copy-Item samples/anodyse-template-overrides/templates/*.j2 .anodyse/templates/
anodyse samples/web-server/deploy-nginx.yml --output docs/custom-templates --verbose
```

See `samples/anodyse-template-overrides/` for a complete sample.

## Integration Points

- GitHub Actions: Anodyse should be triggerable as a workflow step
- Output directory should be configurable for use with MkDocs, Docusaurus, or
  a Backstage-style developer portal
- Should exit with non-zero codes on parse failures for CI safety

## Out of Scope (v1)

- Web UI
- Live preview server
- Ansible Galaxy publishing
- AI-generated descriptions (annotation-driven only in v1)
