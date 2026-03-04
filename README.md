# Anodyse

Anodyse is a CLI that turns Ansible playbooks and roles into user-facing Markdown docs.

It scans files, extracts `@` annotations and TODO/FIXME comments, then renders:
- one doc page per playbook/role
- an `index.md` summary page

## Why use it

- Keeps operational docs close to automation code
- Produces readable docs for consumers (not just Ansible authors)
- Works for single files, role directories, or whole trees
- Fits CI usage via clear exit codes

## Install

Requirements:
- Python 3.11+

Install locally:

```bash
python -m pip install -e .
```

Install with dev tools:

```bash
python -m pip install -e .[dev]
```

Verify:

```bash
anodyse --help
```

## Quick start

Generate docs from one playbook:

```bash
anodyse samples/web-server/deploy-nginx.yml --output docs/samples --verbose
```

Generate docs from a directory (recursive discovery):

```bash
anodyse samples/ --output docs/samples --graph --verbose
```

Typical output:
- `docs/samples/index.md`
- one markdown file per discovered playbook/role

## Using Anodyse in CI/CD

Integrate Anodyse into your CI/CD pipeline to automatically generate documentation:

- **[CI Integration Guide](./docs/CI_INTEGRATION.md)** - Setup for GitHub Actions, GitLab CI/CD, Jenkins, etc.
- **[Quickstart](./specs/003-ci-workflow-setup/quickstart.md)** - 5-minute setup guides by platform
- **[Publishing Guide](./docs/PUBLISHING.md)** - Publish docs to GitHub Pages, GitLab Pages, S3, and more

**Getting started**:
1. Choose your platform: [GitHub Actions](./docs/CI_INTEGRATION.md#github-actions-integration), [GitLab CI/CD](./docs/CI_INTEGRATION.md#gitlab-cicd-integration), or [other](./docs/CI_INTEGRATION.md#generic-ci-patterns)
2. Copy example workflow from [examples/workflows/](./docs/examples/workflows/)
3. Adjust paths and triggers for your repository
4. Commit and push to auto-generate docs

Example (GitHub Actions):
```yaml
name: Generate Docs
on: [push, pull_request]
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install anodyse
      - run: python -m anodyse . --output ./docs
      - uses: actions/upload-artifact@v3
        with:
          path: ./docs
```

## CLI

```text
anodyse TARGET [OPTIONS]
```

`TARGET` can be:
- a playbook file (`.yml` / `.yaml`)
- a role directory (contains `tasks/main.yml`)
- a directory containing multiple playbooks/roles

Options:
- `-o, --output PATH` output directory (default: `./docs`)
- `--graph` include Mermaid flowchart diagrams
- `--no-backup` do not create `.bak` files when overwriting
- `--config PATH` explicit path to `.anodyse.yml`
- `-v, --verbose` detailed processing output

Exit codes:
- `0` success
- `1` parse/runtime error
- `2` generated with annotation warnings (for example missing `@title` or `@description`)

## Supported annotations

File-level annotations:

```yaml
# @title Human-readable title
# @description Plain-language summary
# @param name: what this parameter means
# @warning Caveat or prerequisite
# @example Example invocation or usage
# @tag category-or-label
```

Task-level annotations:

```yaml
# @task.description: Task summary
# @task.note: Extra context
# @task.warning: Task-specific warning
# @task.tag: Task label
```

TODO tracking:
- `TODO:` and `FIXME:` are collected from file headers and task comments
- optional author form is supported (for example `TODO(ops): ...`)

## Manifest config (`.anodyse.yml`)

You can control discovery with an optional manifest:

```yaml
include:
  - samples/web-server/deploy-nginx.yml
  - samples/database/deploy-postgresql.yml

exclude:
  - samples/missing-comments/deploy-unannotated.yml
```

Rules:
- If `include` is present, only those paths are used
- Otherwise, `exclude` removes paths from discovered results
- Missing declared paths produce warnings

Manifest lookup order:
1. `--config` path (if provided)
2. `.anodyse.yml` near the target
3. `.anodyse.yml` in repo root (detected via `.git`)

## Template overrides

Override built-in templates by adding files in:

```text
./.anodyse/templates/
```

Supported override filenames:
- `playbook.md.j2`
- `role.md.j2`
- `index.md.j2`

Lookup order:
1. local overrides in `./.anodyse/templates/`
2. packaged defaults in `anodyse/templates/`

Example (PowerShell):

```powershell
New-Item -ItemType Directory -Path .anodyse/templates -Force | Out-Null
Copy-Item samples/anodyse-template-overrides/templates/*.j2 .anodyse/templates/
anodyse samples/web-server/deploy-nginx.yml --output docs/custom-templates --verbose
```

## Development

Run tests:

```bash
pytest
```

Run lint:

```bash
ruff check .
```

Build package:

```bash
python -m pip install build
python -m build
```
