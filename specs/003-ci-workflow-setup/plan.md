# Implementation Plan: CI Workflow Integration Guide for Anodyse Users

**Branch**: `003-ci-workflow-setup` | **Date**: March 4, 2026 | **Spec**: [specs/003-ci-workflow-setup/spec.md](spec.md)
**Input**: Feature specification from `/specs/003-ci-workflow-setup/spec.md`

## Summary

Create comprehensive integration guides and copy-paste-ready example workflows for Anodyse users to incorporate Anodyse into their CI/CD pipelines for automated Ansible documentation generation. The feature covers three priority platforms: GitHub Actions (primary), GitLab CI/CD (equivalent), and generic CI/CD patterns for custom systems. Deliverables include integration guides, working workflow examples with configurable input/output paths, error handling, multi-trigger support (push/PR/scheduled), template customization guidance, and publication patterns. The anodyse repository will demonstrate this via GitHub Actions workflows built from sample playbooks.

## Technical Context

**Project Type**: Documentation + Example Workflows (non-code feature)  
**Language/Version**: YAML (GitHub Actions, GitLab CI) + Markdown documentation  
**Primary Dependencies**: Anodyse CLI (existing), GitHub Actions runtime, GitLab Runner, Jinja2 templates  
**Storage**: GitHub Pages or GitLab Pages for generated docs (optional, user-configurable)  
**Testing**: Manual validation - end users follow guides and verify workflow execution  
**Target Platform**: Multi-platform (GitHub, GitLab, generic CI systems)  
**Performance Goals**: Workflows complete documentation generation in <5 minutes for typical playbook sets; setup/integration <20 minutes per platform  
**Constraints**: Fail-fast on critical errors; support configurable paths and template mounts; no external dependencies required  
**Scale/Scope**: 3 primary platforms (GitHub Actions P1, GitLab CI P2, Generic CI patterns P3); ~5-7 working example workflows

## Constitution Check

✅ **Core Principles Alignment**:
- **User-First Output** ✅ Documentation written for Anodyse users (platform consumers), not internal developers
- **Annotation-Driven** ✅ Guides users to add annotations to playbooks for better documentation
- **Graceful Degradation** ✅ Workflows can generate docs even with minimal annotations
- **Fail Loudly in CI, Fail Gently on CLI** ✅ CI workflows fail-fast on errors; documentation provides troubleshooting
- **Convention Over Configuration** ✅ Sensible workflow defaults with configuration options for customization

✅ **Code Standards Compliance**: N/A (documentation and workflow YAML, not Python code)

✅ **Architecture Alignment**: Workflows invoke existing Anodyse CLI as-is (no architectural changes required)

✅ **Output Rules Alignment**: 
- Generated markdown output follows UTF-8 Markdown spec
- Existing files backed up before overwrite
- Index page generated summarizing all processed items

✅ **What Anodyse Must Never Do** - All constraints respected:
- Will not modify source playbooks
- Will not make assumptions about undocumented intent
- Does not require network access (Anodyse runs locally)
- Does not expose internal architecture in docs

**Constitutional Status**: ✅ APPROVED - No violations | All principles aligned

## Phase 0: Outline & Research

**Status**: NEEDS EXECUTION → Generate `research.md` with clarification of best practices

### Research Tasks

1. **GitHub Actions Best Practices for CI Documentation Pipelines**
   - How to invoke custom CLI tools in GitHub Actions
   - Artifact storage and retention patterns
   - GitHub Pages deployment from workflows
   - Secret management and environment variables
   - Matrix builds and multi-trigger patterns
   - Error handling and exit codes in workflows

2. **GitLab CI/CD Runner Patterns**
   - `.gitlab-ci.yml` structure and syntax
   - Docker runner vs. shell runner considerations
   - Artifact handling in GitLab CI
   - GitLab Pages publish integration
   - Variable scoping (global, job, environment-level)
   - Pipeline triggers (push, MR, schedule)

3. **Generic CI/CD Integration Patterns**
   - CLI invocation patterns across platforms
   - Environment variable naming conventions
   - Exit code semantics and error signaling
   - Artifact storage abstraction
   - Template mounting strategies (Docker volumes, file copies)

4. **Documentation Publishing Strategies**
   - GitHub Pages workflow (gh-pages branch, actions/deploy-pages)
   - GitLab Pages `.gitlab-ci.yml` integration
   - Read the Docs integration patterns
   - Static hosting options (Netlify, Vercel)
   - Documentation site generation tools compatibility

### Questions to Resolve via Research

- NEEDS CLARIFICATION: What is the minimum supported Python version for anodyse users running in CI?
- NEEDS CLARIFICATION: Should example workflows demonstrate Docker container usage or assume local anodyse installation?
- NEEDS CLARIFICATION: How should users handle anodyse updates/pinning - specific version, latest, or version ranges?
- NEEDS CLARIFICATION: What are the timeout recommendations for large Ansible playbook sets?

## Phase 1: Design & Contracts

### Data Model: CI Integration Components

File: `data-model.md` (to be generated)

**Key Entities**:

1. **Workflow Configuration** (GitHub Actions YAML / GitLab CI YAML)
   - Trigger events: push, pull_request, schedule, manual_dispatch
   - Jobs: run anodyse, generate docs, publish artifacts
   - Configuration: input paths, output paths, template dirs, publication targets
   - Error handling: exit code capture, conditional steps
   - Secrets/Environment: credential injection, variable sourcing

2. **Example Workflows** (deliverables)
   - GitHub Actions basic (push + PR triggers)
   - GitHub Actions advanced (push + PR + scheduled + GitHub Pages publish)
   - GitLab CI basic (push + MR triggers)
   - GitLab CI advanced (push + MR + scheduled + GitLab Pages publish)
   - Generic CI/CD shell script patterns (Jenkins, Woodpecker, CircleCI)

3. **Integration Guide Structure**
   - Platform-specific setup (runner config, env vars, secrets)
   - Workflow copy-paste examples with inline comments
   - Configuration walkthrough (input/output paths, templates)
   - Customization guide (timeout, error handling, triggers)
   - Troubleshooting section (common errors, debug steps)
   - Publication guide (platform-specific hosting options)

4. **Publication Targets**
   - GitHub Pages (deployment via gh-pages branch or direct)
   - GitLab Pages (public_dir artifact)
   - Generic hosting (artifacts download, manual upload)
   - Read the Docs integration (webhook triggers on commit)

### Contracts: User-Facing Workflows

File: `contracts/` (to be generated)

1. **GitHub Actions Workflow Contract** (`contracts/github-actions-basic.yml`)
   - Inputs: PLAYBOOK_DIR, OUTPUT_DIR, TEMPLATE_DIR, PUBLISH (optional)
   - Outputs: artifact path, documentation URL (if published)
   - Triggers: on push, on pull_request, on schedule
   - Error handling: fail if anodyse returns non-zero

2. **GitLab CI Configuration Contract** (`contracts/gitlab-ci-basic.yml`)
   - Variables: PLAYBOOK_DIR, OUTPUT_DIR, TEMPLATE_DIR, PUBLISH (optional)
   - Artifacts: generated documentation files
   - Triggers: push, merge_request, schedule
   - Error handling: fail if script returns non-zero

3. **Generic CI Shell Pattern Contract** (`contracts/ci-pattern.sh`)
   - Input parameters: playbook_dir, output_dir, template_dir
   - Environment variables: ANODYSE_CONFIG, CI_BUILD_ID
   - Exit code: 0 on success, non-zero on critical errors
   - Artifact handling: copy docs to CI artifact staging area

### Quickstart Guide

File: `quickstart.md` (to be generated)

**Structure**:
- "Get Started in 5 Minutes" per platform
- Copy-paste ready workflow YAML
- Basic setup (clone repo, set paths, run anodyse)
- Where to find help (docs, examples, troubleshooting)

## Project Structure

### Documentation Deliverables

```text
docs/
├── CI_INTEGRATION.md
│   ├── GitHub Actions Guide
│   │   ├── Installation
│   │   ├── Basic Setup
│   │   ├── Advanced Options (triggers, templates, publishing)
│   │   ├── Troubleshooting
│   │   └── Examples
│   ├── GitLab CI Guide
│   │   ├── Runner Setup
│   │   ├── Basic .gitlab-ci.yml
│   │   ├── Advanced Options
│   │   ├── Troubleshooting
│   │   └── Examples
│   └── Generic CI/CD Guide
│       ├── CLI Patterns
│       ├── Shell Script Examples
│       ├── Environment Variables
│       ├── Error Handling
│       └── Multi-Platform Examples
│
├── examples/
│   ├── github-actions-basic.yml
│   ├── github-actions-with-github-pages.yml
│   ├── github-actions-schedule-all-triggers.yml
│   ├── gitlab-ci-basic.yml
│   ├── gitlab-ci-with-gitlab-pages.yml
│   ├── gitlab-ci-schedule-all-triggers.yml
│   ├── jenkins-dsl.groovy
│   ├── circleci-config.yml
│   └── generic-ci-script.sh
│
├── PUBLISHING.md
│   ├── GitHub Pages Setup
│   ├── GitLab Pages Setup
│   ├── Read the Docs Integration
│   └── Custom Static Hosting
│
└── TROUBLESHOOTING.md
    ├── Common Errors
    ├── Debug Steps
    ├── Performance Tuning
    └── FAQ
```

### Repository Integration (anodyse dogfood)

```text
.github/workflows/
├── docs-on-push.yml           # On push to main, regenerate all docs
├── docs-on-pr.yml              # On PR, validate docs can regenerate
└── docs-schedule.yml           # Weekly schedule to regenerate all docs

samples/                        # Existing sample playbooks
├── README.md                   # Updated with CI integration links
└── [existing samples]

```

## Phase 1: Output - Generated Artifacts

### Output Artifacts (Phase 1)

1. **Research** → `research.md`
   - Best practices per platform
   - Technology decisions: Docker vs. local runners, version pinning approach
   - Integration patterns across platforms

2. **Data Model** → `data-model.md`
   - CI integration component structure
   - Configuration schema (environs, paths, triggers)
   - Error handling contract

3. **Contracts** → `contracts/`
   - `github-actions-schema.yml` - Workflow input/output specification
   - `gitlab-ci-schema.yml` - `.gitlab-ci.yml` structure definition
   - `generic-cli-contract.sh` - Shell invocation contract

4. **Quickstart** → `quickstart.md`
   - 5-minute setup per platform
   - Copy-paste ready examples
   - Common customizations

### Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`
- Add: GitHub Actions YAML schema, GitLab CI configuration patterns, shell scripting best practices
- Preserve: Existing anodyse architecture context

## Complexity Tracking

| Decision | Why Needed | Simpler Alternative Rejected |
|----------|-----------|-------------------------------|
| Three platforms (GitHub, GitLab, Generic) | User base spans all three; documentation-only feature, no code complexity | Covering only GitHub would exclude GitLab users and enterprise CI customers |
| Multi-trigger support (push/PR/schedule) | Different teams have different documentation generation policies | Single-trigger workflows would not serve common use cases (PR validation, periodic updates) |
| Template customization examples | Organizations need custom branding/formatting in docs | Built-in templates only would limit adoption in enterprise environments |
| Publication guidance (3 platforms) | Users need to publish docs after generation (stated in acceptance criteria) | Omitting this would leave generated docs inaccessible |

## Phase 2: Task Decomposition (Deferred)

Task breakdown into sprint-ready items will be generated via `/speckit.tasks` command.

---

**Status**: Implementation Plan COMPLETE ✅  
**Next**: Generate Phase 0 research via subagent, then Phase 1 contracts/design, then Phase 2 tasks.
