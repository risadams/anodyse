# CI Integration Guide: Automated Ansible Documentation with Anodyse

Use Anodyse in your CI/CD pipeline to automatically generate Ansible documentation from annotated playbooks and roles. This guide covers setup for GitHub Actions, GitLab CI/CD, and generic CI systems.

**Table of Contents**
- [Overview](#overview)
- [Quick Links by Platform](#quick-links-by-platform)
- [Core Concepts](#core-concepts)
- [Common Patterns](#common-patterns)
- [GitHub Actions Integration](#github-actions-integration)
- [GitLab CI/CD Integration](#gitlab-cicd-integration)
- [Generic CI Patterns](#generic-ci-patterns)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What You Can Do

- **Automatic Documentation Generation**: Generate updated Markdown documentation on every push, pull request, or scheduled run
- **Multi-Platform Support**: Works with GitHub Actions, GitLab CI/CD, Jenkins, Woodpecker, CircleCI, Travis CI, and any shell-based CI system
- **Artifact Integration**: Generated docs available as workflow artifacts for review and download
- **Optional Publishing**: Publish to GitHub Pages, GitLab Pages, Read the Docs, or static hosting
- **Custom Templates**: Use your own Jinja2 templates to customize documentation output
- **Error Handling**: Fail fast on critical errors or validate documentation as part of CI quality gates

### Who This Is For

- **Ansible users** maintaining playbooks/roles with structured annotations
- **Teams** wanting documentation to stay in sync with code
- **Enterprise organizations** with CI/CD infrastructure (Jenkins, Woodpecker, etc.)
- **Individual contributors** using open-source CI platforms

---

## Quick Links by Platform

| Platform | Setup Time | Best For | Complexity |
|----------|-----------|----------|-----------|
| **[GitHub Actions](#github-actions-integration)** | 5 min | GitHub repos, open-source projects | Low |
| **[GitLab CI/CD](#gitlab-cicd-integration)** | 5-10 min | GitLab.com, self-hosted GitLab | Low-Medium |
| **[Generic CI](#generic-ci-patterns)** | 15-20 min | Jenkins, Woodpecker, CircleCI, Travis | Medium-High |

**First time?** Start with the [Quickstart Guide](../specs/003-ci-workflow-setup/quickstart.md) if your platform is listed.

---

## Core Concepts

### Anodyse CLI Invocation

All CI integrations ultimately invoke the Anodyse CLI tool. The basic pattern:

```bash
python -m anodyse \
  --input-path ./playbooks \
  --output-path ./docs/generated \
  --template-dir ./templates
```

**Key Parameters**:
- `--input-path`: Directory containing Ansible playbooks or roles
- `--output-path`: Where to write generated documentation files
- `--template-dir`: (Optional) Custom Jinja2 templates for output formatting
- `--verbose`: (Optional) Enable debug logging

### Environment Variables

Anodyse respects these environment variables:

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `ANODYSE_INPUT_DIR` | Input playbooks/roles directory | (none, required) | `./playbooks` |
| `ANODYSE_OUTPUT_DIR` | Output documentation directory | `./docs` | `./docs/generated` |
| `ANODYSE_TEMPLATE_DIR` | Custom templates location | (uses built-in) | `./templates` |
| `ANODYSE_VERBOSE` | Enable debug logging | `false` | `true` or `1` |

### Exit Codes

- **0**: Success - documentation generated successfully
- **1**: General error - invalid input, missing files, or generation failure
- **2**: Configuration error - missing required environment variable or invalid parameter
- **127**: Command not found - `anodyse` not in PATH (install via `pip install anodyse`)

### Artifact Storage Patterns

**Pull Requests**: Store artifacts for review
- Typical retention: 30 days
- Reviewers can download and inspect generated docs
- Artifacts prove documentation generation completed without errors

**Main/Release Branches**: Store artifacts for release candidates
- Typical retention: 90+ days (check platform quotas)
- Publish to GitHub Pages, GitLab Pages, or external hosting
- Keep as audit trail of documentation versions

**Scheduled Runs**: Keep minimal or archive
- Typical retention: 7 days
- Use for detecting drift or validating documentation freshness

---

## Common Patterns

### Conditional Execution Based on Branch

Only generate documentation for main/release branches, skip for feature branches:

**GitHub Actions**:
```yaml
- name: Generate Documentation
  if: github.ref == 'refs/heads/main'
  run: python -m anodyse --input-path ./playbooks --output-path ./docs
```

**GitLab CI**:
```yaml
generate:
  script:
    - python -m anodyse --input-path ./playbooks --output-path ./docs
  only:
    - main
    - tags
```

### Error Handling Strategies

**Fail Fast** (default):
```bash
set -e
python -m anodyse --input-path ./playbooks --output-path ./docs
echo "Documentation generated successfully"
```

**Fail Gracefully** (for optional documentation):
```bash
python -m anodyse --input-path ./playbooks --output-path ./docs || {
  echo "Documentation generation failed, but continuing CI pipeline"
  exit 0
}
```

**Fail with Validation**:
```bash
python -m anodyse --input-path ./playbooks --output-path ./docs
if [ ! -f ./docs/index.md ]; then
  echo "ERROR: Generated documentation missing index.md"
  exit 1
fi
```

### Environment Setup Patterns

**Using Command Line Arguments**:
```bash
python -m anodyse \
  --input-path "${INPUT_DIR:=./playbooks}" \
  --output-path "${OUTPUT_DIR:=./docs}" \
  --template-dir "${TEMPLATE_DIR:=./custom-templates}"
```

**Using Environment Variables**:
```bash
export ANODYSE_INPUT_DIR="./playbooks"
export ANODYSE_OUTPUT_DIR="./docs"
export ANODYSE_TEMPLATE_DIR="./custom-templates"
python -m anodyse
```

---

## GitHub Actions Integration

GitHub Actions is GitHub's native CI/CD platform, integrated directly into your repository with no setup required beyond creating a workflow file.

### Platform Overview

- **Pricing**: Free for public repos, pay-per-minute for private (120 free minutes/month included)
- **Runners**: GitHub-hosted (fastest) or self-hosted (for private infrastructure)
- **Artifacts**: Integrated, with configurable retention (free tier: 30 days for private)
- **Secrets**: GitHub Secrets for sensitive data (tokens, credentials, API keys)
- **Workflows**: YAML files in `.github/workflows/` directory

### 3-Step Setup

#### Step 1: Create Workflow File

Create `.github/workflows/generate-docs.yml`:

```yaml
name: Generate Ansible Documentation

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * MON'  # Weekly Monday at 2 AM UTC
  workflow_dispatch:        # Manual trigger via UI

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install Anodyse
        run: pip install anodyse
      
      - name: Generate Documentation
        run: |
          python -m anodyse \
            --input-path ./playbooks \
            --output-path ./docs/generated
      
      - name: Upload Artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: ansible-docs-${{ github.run_number }}
          path: ./docs/generated
          retention-days: 30
```

#### Step 2: Customize Paths

Edit the workflow to match your repository structure:
- Change `./playbooks` to your Ansible directory
- Change `./docs/generated` to your output directory
- Adjust Python version if needed (3.9, 3.10, 3.11, 3.12)

#### Step 3: Push to Repository

```bash
git add .github/workflows/generate-docs.yml
git commit -m "feat: Add Anodyse documentation generation workflow"
git push origin main
```

Workflow will run automatically on next push. Check "Actions" tab to monitor.

### Advanced Configuration

**Publishing to GitHub Pages**:

```yaml
      - name: Generate Documentation
        run: |
          python -m anodyse \
            --input-path ./playbooks \
            --output-path ./docs
      
      - name: Deploy to GitHub Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

**Custom Templates**:

```yaml
      - name: Generate Documentation with Custom Templates
        run: |
          python -m anodyse \
            --input-path ./playbooks \
            --output-path ./docs/generated \
            --template-dir ./templates
```

**Matrix Strategy** (generate docs for multiple Python versions):

```yaml
jobs:
  generate-docs:
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    runs-on: ubuntu-latest
    steps:
      # ... checkout, setup Python ...
      - name: Generate Documentation
        run: |
          python -m anodyse \
            --input-path ./playbooks \
            --output-path ./docs/py${{ matrix.python-version }}
```

### Customization Guide

**Changing Trigger Events**:

| Trigger | Configuration | Example |
|---------|---|---|
| On push to main | `on: push: branches: [main]` | Every commit to main |
| On pull requests | `on: pull_request:` | Every PR created/updated |
| On schedule | `on: schedule: - cron: '0 2 * * *'` | Daily at 2 AM UTC |
| Manual trigger | `on: workflow_dispatch:` | Click button in Actions tab |

**Managing Artifacts**:

```yaml
      - name: Upload Artifacts
        with:
          retention-days: 7    # Keep for 7 days
          if-no-files-found: error  # Fail if no files generated
```

### Common Customizations

**Skip documentation for draft PRs**:
```yaml
      - name: Generate Documentation
        if: '!github.event.pull_request.draft'
        run: python -m anodyse --input-path ./playbooks --output-path ./docs
```

**Use latest Python version**:
```yaml
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
```

**Post comments with artifact links**:
```yaml
      - name: Comment PR with Artifact Link
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'Documentation artifacts available: Check the "Artifacts" section of this workflow run'
            })
```

**Retry on transient failures**:
```yaml
      - name: Generate Documentation (with retry)
        uses: nick-invision/retry@v2
        with:
          timeout_minutes: 5
          max_attempts: 3
          command: python -m anodyse --input-path ./playbooks --output-path ./docs
```

### GitHub Actions Troubleshooting

See [TROUBLESHOOTING.md#github-actions](./TROUBLESHOOTING.md#github-actions) for detailed solutions to common issues.

---

## GitLab CI/CD Integration

GitLab CI/CD is GitLab's integrated solution supporting both SaaS (gitlab.com) and self-hosted instances.

### Platform Overview

- **Pricing**: Free tier includes 400 minutes/month on shared runners
- **Runners**: Group/project runners (Docker, shell, Kubernetes) or shared runners
- **Artifacts**: Integrated with configurable retention and expiration
- **Secrets**: CI/CD variables (project/group/instance scoped)
- **Configuration**: Single `.gitlab-ci.yml` file in repository root

### 3-Step Setup

#### Step 1: Create `.gitlab-ci.yml`

```yaml
stages:
  - generate

variables:
  ANODYSE_INPUT_DIR: ./playbooks
  ANODYSE_OUTPUT_DIR: ./docs/generated

generate_docs:
  stage: generate
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse --input-path $ANODYSE_INPUT_DIR --output-path $ANODYSE_OUTPUT_DIR
  artifacts:
    paths:
      - docs/generated/
    expire_in: 30 days
  only:
    - main
    - merge_requests
  timeout: 10 minutes
```

#### Step 2: Customize for Your Repository

Edit `.gitlab-ci.yml`:
- Change `./playbooks` to your Ansible directory
- Change `./docs/generated` to your output directory
- Adjust Python version if needed

#### Step 3: Commit and Push

```bash
git add .gitlab-ci.yml
git commit -m "feat: Add Anodyse documentation generation pipeline"
git push origin main
```

Pipeline will execute automatically. Check "CI/CD → Pipelines" to monitor.

### Runner Options

**Docker Runner** (recommended, automatic setup):
```yaml
generate_docs:
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse --input-path ./playbooks --output-path ./docs
```

**Shell Runner** (for self-hosted):
```yaml
generate_docs:
  script:
    - python3.11 -m venv /tmp/anodyse_venv
    - source /tmp/anodyse_venv/bin/activate
    - pip install anodyse
    - python -m anodyse --input-path ./playbooks --output-path ./docs
```

### Advanced Configuration

**Publishing to GitLab Pages**:

```yaml
stages:
  - generate
  - deploy

variables:
  ANODYSE_INPUT_DIR: ./playbooks
  ANODYSE_OUTPUT_DIR: public

generate_docs:
  stage: generate
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse --input-path $ANODYSE_INPUT_DIR --output-path $ANODYSE_OUTPUT_DIR
  artifacts:
    paths:
      - public/
    expire_in: 30 days
  only:
    - main

pages:
  stage: deploy
  script:
    - echo "Publishing documentation to GitLab Pages"
  artifacts:
    paths:
      - public/
  only:
    - main
  dependencies:
    - generate_docs
```

**Using Environment Variables**:

```yaml
variables:
  ANODYSE_VERBOSE: 'true'
  CUSTOM_TEMPLATES: './templates'

generate_docs:
  script:
    - pip install anodyse
    - export ANODYSE_TEMPLATE_DIR=$CUSTOM_TEMPLATES
    - python -m anodyse --input-path ./playbooks --output-path ./docs
```

**Scheduled Pipelines**:

```yaml
generate_docs:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
      when: always
    - if: '$CI_PIPELINE_SOURCE == "push"'
      when: always
    - when: never
```

### Common Customizations

**Only on specific branches**:
```yaml
  only:
    - main
    - /^release\/.*$/      # Regex: release/* branches
```

**Only in merge requests**:
```yaml
  only:
    - merge_requests
```

**Allow failure** (don't block pipeline):
```yaml
  allow_failure: true
```

**Custom timeout**:
```yaml
  timeout: 15 minutes
```

### GitLab CI/CD Troubleshooting

See [TROUBLESHOOTING.md#gitlab-cicd](./TROUBLESHOOTING.md#gitlab-cicd) for detailed solutions.

---

## Generic CI Patterns

Use Anodyse with any CI system that supports shell script execution: Jenkins, Woodpecker, CircleCI, Travis CI, and others.

### Portable Shell Pattern

All CI systems can execute this shell script pattern:

```bash
#!/bin/bash
set -e

# Configuration
INPUT_DIR="${INPUT_DIR:=./playbooks}"
OUTPUT_DIR="${OUTPUT_DIR:=./docs}"
TEMPLATE_DIR="${TEMPLATE_DIR:=./templates}"

# Setup Python environment
python3 -m venv /tmp/anodyse
source /tmp/anodyse/bin/activate

# Install and run Anodyse
pip install --upgrade pip
pip install anodyse

# Generate documentation
python -m anodyse \
  --input-path "$INPUT_DIR" \
  --output-path "$OUTPUT_DIR" \
  --template-dir "$TEMPLATE_DIR"

# Verify output
if [ ! -f "$OUTPUT_DIR/index.md" ]; then
  echo "ERROR: Generated documentation missing index.md"
  exit 1
fi

echo "Documentation generated successfully in $OUTPUT_DIR"
```

### Jenkins Integration

See [Jenkins Integration Example](../examples/jenkins/Jenkinsfile) for complete Declarative Pipeline example.

### Woodpecker CI Integration

See [Woodpecker Integration Example](../examples/woodpecker/.woodpecker.yml) for complete example.

### CircleCI Integration

See [CircleCI Integration Example](../examples/circleci/config.yml) for complete example.

### Travis CI Integration

See [Travis CI Integration Example](../examples/travis/.travis.yml) for complete example.

### Platform-Specific Guidance

| Platform | Runner | Setup | Notes |
|----------|--------|-------|-------|
| **Jenkins** | Any | Declarative Pipeline or groovy script | Requires Python 3.9+ installed |
| **Woodpecker** | Docker/Kubernetes | `.woodpecker.yml` | Docker container easier than shell |
| **CircleCI** | Docker | `config.yml` | Free tier includes 6000 minutes/month |
| **Travis CI** | Docker | `.travis.yml` | Legacy platform, moving to sustainable model |

---

## Troubleshooting

### Check Logs

1. **GitHub Actions**: Actions tab → Workflow run → Job → Step logs
2. **GitLab CI**: CI/CD → Pipelines → Pipeline → Job logs
3. **Other platforms**: Check your CI system's log viewer

### Common Issues

**`anodyse` command not found**:
- Solution: Ensure `pip install anodyse` runs before invoking the command
- Verify Python version (3.9+) installed: `python --version`

**Missing input directory**:
- Verify `--input-path` points to valid Ansible directory
- Check for typos in path (paths are case-sensitive on Linux)

**No documentation generated**:
- Check for errors in workflow/pipeline logs
- Verify Ansible playbooks have proper annotations
- Test locally: `python -m anodyse --input-path ./playbooks --output-path ./test-docs`

**Artifact upload fails**:
- Verify output directory exists and has files
- Check storage quotas on your platform
- Ensure artifact path doesn't contain spaces or special characters

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for comprehensive troubleshooting guide.

---

## Next Steps

1. **Choose your platform**: GitHub Actions, GitLab CI/CD, or generic pattern
2. **Follow setup guide**: 5-20 minute setup depending on platform
3. **Test locally**: Verify Anodyse works on your machine first
4. **Customize**: Adjust paths, triggers, and templates for your needs
5. **Publish**: Optional - add GitHub Pages or GitLab Pages deployment

For more details:
- [Quickstart Guide](../specs/003-ci-workflow-setup/quickstart.md) - Fast 5-minute setup
- [Environment Variables Reference](./ENVIRONMENT_VARIABLES.md) - All configuration options
- [Publishing Guide](./PUBLISHING.md) - Host documentation online
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Solve common issues
- [Contributing CI Examples](../CI_EXAMPLES_CONTRIBUTING.md) - Add your platform

---

**Learn More**
- [Anodyse CLI Reference](https://github.com/example/anodyse) - Complete CLI documentation
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/tips_tricks/index.html) - Ansible documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions) - GitHub Actions reference
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/) - GitLab CI/CD reference

**Last Updated**: March 4, 2026
