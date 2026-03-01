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
