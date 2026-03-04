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

GitLab CI/CD is GitLab's integrated solution supporting both SaaS (gitlab.com) and self-hosted instances. Use the [GitLab CI/CD Reference Guide](./gitlab-ci-reference.md) for comprehensive schema, runner options, and advanced patterns.

### Platform Overview

- **Pricing**: Free tier includes 400 minutes/month on shared runners
- **Runners**: Docker (recommended), Shell (self-hosted), or Kubernetes
- **Artifacts**: Integrated with configurable retention and branch-specific expiration
- **Secrets**: CI/CD variables (project/group/instance scoped) with masking and protection
- **Configuration**: Single `.gitlab-ci.yml` file in repository root
- **Pages**: Built-in Pages hosting with automatic domain (project.gitlab.io)

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
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: always
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: always
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

### Example Workflows

We provide four ready-to-use example configurations:

#### 1. **Basic Setup** (Start here)
[gitlab-ci-basic.yml](../examples/gitlab-ci-basic.yml) - Minimal working example with Docker runner, generates documentation from playbooks, stores artifacts.

```bash
cp docs/examples/gitlab-ci-basic.yml .gitlab-ci.yml
# Edit paths to match your repository
git add .gitlab-ci.yml && git commit -m "Add Anodyse documentation" && git push
```

#### 2. **With GitLab Pages Publishing**
[gitlab-ci-with-gitlab-pages.yml](../examples/gitlab-ci-with-gitlab-pages.yml) - Generates docs and publishes to GitLab Pages automatically. Documentation becomes accessible at `https://[group].gitlab.io/[project]/`.

```bash
cp docs/examples/gitlab-ci-with-gitlab-pages.yml .gitlab-ci.yml
# Enable Pages in: Settings → Pages
git add .gitlab-ci.yml && git commit -m "Add Anodyse with Pages publishing" && git push
```

#### 3. **Self-Hosted Shell Runner**
[gitlab-ci-shell-runner.yml](../examples/gitlab-ci-shell-runner.yml) - For on-premise deployments or runner machines where you prefer shell execution. Includes Python venv setup, runner tagging, and retry logic.

```bash
cp docs/examples/gitlab-ci-shell-runner.yml .gitlab-ci.yml
# Ensure shell runner is tagged as "shell" in your infrastructure
git add .gitlab-ci.yml && git commit -m "Add Anodyse with shell runner" && git push
```

#### 4. **Custom Template Integration**
[gitlab-ci-custom-templates.yml](../examples/gitlab-ci-custom-templates.yml) - Multiple jobs demonstrating local templates, external downloads, template repositories, and branch-specific variants. Run specific template sets for different documentation styles.

```bash
cp docs/examples/gitlab-ci-custom-templates.yml .gitlab-ci.yml
# Organize your templates in: ./templates/production/, ./templates/development/, etc.
git add .gitlab-ci.yml && git commit -m "Add Anodyse with custom templates" && git push
```

### Runner Options

**Docker Runner** (recommended, automatic setup):
```yaml
generate_docs:
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse --input-path ./playbooks --output-path ./docs
```

**Shell Runner** (for self-hosted or on-premise):
```yaml
generate_docs:
  tags:
    - shell  # Ensure runner has this tag
  script:
    - python3.11 -m venv /tmp/anodyse_venv
    - source /tmp/anodyse_venv/bin/activate
    - pip install anopyse
    - python -m anodyse --input-path ./playbooks --output-path ./docs
```

**Kubernetes Runner** (advanced):
```yaml
generate_docs:
  tags:
    - kubernetes
  script:
    - pip install anodyse
    - python -m anodyse --input-path ./playbooks --output-path ./docs
```

See [gitlab-ci-reference.md](./gitlab-ci-reference.md#docker-vs-shell-runners) for detailed runner comparison and configuration.

### Advanced Configuration

**Publishing to GitLab Pages with environment tracking**:

```yaml
stages:
  - generate
  - deploy

generate_docs:
  stage: generate
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse --input-path ./playbooks --output-path ./public
  artifacts:
    paths:
      - public/
    expire_in: 30 days

pages:
  stage: deploy
  script:
    - echo "Publishing to GitLab Pages"
  artifacts:
    paths:
      - public/
  environment:
    name: production
    url: https://$CI_PROJECT_NAMESPACE.gitlab.io/$CI_PROJECT_NAME/
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: on_success
```

**Using Custom Variables and Templates**:

```yaml
variables:
  ANODYSE_VERBOSE: 'true'
  TEMPLATE_VERSION: 'v1.2.0'

generate_docs:
  script:
    - pip install anodyse
    - |
      if [ -n "$TEMPLATE_VERSION" ]; then
        curl -L https://github.com/company/templates/releases/download/$TEMPLATE_VERSION/templates.tar.gz | tar -xz -C ./templates
      fi
    - python -m anodyse \
        --input-path ./playbooks \
        --output-path ./docs \
        --template-dir ./templates
```

**Scheduled Pipelines** (weekly documentation freshness check):

```yaml
generate_docs:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
      when: always
    - if: '$CI_PIPELINE_SOURCE == "push"'
      when: always
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: always
    - when: never
```

**Multi-Branch Retention Policy**:

```yaml
artifacts:
  paths:
    - docs/generated/
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      expire_in: 90 days
    - if: '$CI_COMMIT_BRANCH == "develop"'
      expire_in: 30 days
    - expire_in: 7 days
```

### Common Customizations

**Only on specific branches**:
```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == "main"'
  - if: '$CI_COMMIT_BRANCH == "develop"'
  - if: '$CI_COMMIT_BRANCH =~ /^release\/.*$/'
```

**Only in merge requests**:
```yaml
rules:
  - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

**Allow failure** (don't block downstream jobs):
```yaml
allow_failure: true
```

**Custom timeout**:
```yaml
timeout: 15 minutes
```

**Skip scheduled runs**:
```yaml
rules:
  - if: '$CI_PIPELINE_SOURCE == "schedule"'
    when: never
  - when: always
```

### Modern `rules` vs. Legacy `only`/`except`

GitLab recommends `rules` (new syntax) over `only`/`except` (legacy):

```yaml
# ❌ Legacy (avoid):
only:
  - main
  - merge_requests

# ✓ Modern (recommended):
rules:
  - if: '$CI_COMMIT_BRANCH == "main"'
  - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

See [gitlab-ci-reference.md](./gitlab-ci-reference.md#triggers--rules) for comprehensive `rules` patterns.

### GitLab CI/CD Troubleshooting

See [TROUBLESHOOTING.md#gitlab-cicd](./TROUBLESHOOTING.md#gitlab-cicd) for detailed solutions to common issues including runner problems, variable scoping, and artifact failures.

---

## Generic CI Patterns

Use Anodyse with any CI system that supports shell script execution: Jenkins, Woodpecker, CircleCI, Travis CI, and others.

### All-in-One Portable Shell Script

We provide a complete shell script that works on every CI platform:

**[generate-docs.sh](./examples/scripts/generate-docs.sh)** (300+ lines)
- Automatic Python environment setup with venv
- Pre-flight checks (Python version, input directory, files)
- Comprehensive logging (info, debug, error levels)
- Error handling and validation
- Cross-platform compatibility (Linux, macOS, Windows WSL)
- Optional cleanup

```bash
# Download and use
curl -o scripts/generate-docs.sh \
  https://raw.githubusercontent.com/acuity-inc/anodyse/main/docs/examples/scripts/generate-docs.sh
chmod +x scripts/generate-docs.sh

# Run with defaults or custom environment
INPUT_DIR=./playbooks \
OUTPUT_DIR=./docs \
VERBOSE=true \
./scripts/generate-docs.sh
```

### Portable Shell Pattern

The minimal pattern that works on any CI system:

```bash
#!/bin/bash
set -e

# Setup
python3 -m venv /tmp/anodyse_venv
source /tmp/anodyse_venv/bin/activate

# Install and run
pip install --upgrade pip
pip install anodyse

# Generate
python -m anodyse \
  --input-path ./playbooks \
  --output-path ./docs

# Verify
if [ ! -f "./docs/index.md" ]; then
  echo "ERROR: Documentation generation failed"
  exit 1
fi

echo "SUCCESS: Documentation generated"
```

### Core CLI Pattern

At the heart of every integration:

```bash
python -m anodyse \
  --input-path ./playbooks \
  --output-path ./docs \
  --template-dir ./templates \
  --verbose
```

**Exit Codes**:
- `0`: Success
- `1`: Failure (check logs for details)
- `2`: Configuration error

### Jenkins Integration

[Complete Jenkinsfile Example](./examples/jenkins/Jenkinsfile) (500+ lines)

**Features**:
- Declarative Pipeline format
- 6 stages: Setup, Prepare, Install, Generate, Verify, Archive
- Environment variables configuration
- Virtual environment management
- Comprehensive error handling
- Customization guide with 10+ patterns

**Quick Start**:
```bash
cp docs/examples/jenkins/Jenkinsfile ./Jenkinsfile
# Edit ANODYSE_INPUT_DIR and ANODYSE_OUTPUT_DIR variables
# Create Jenkins pipeline job pointed to your repository
```

### Woodpecker CI Integration

[Complete Woodpecker Configuration](./examples/woodpecker/.woodpecker.yml) (300+ lines)

**Features**:
- Docker-based pipeline
- Sequential steps (similar to GitLab)
- Trigger configuration (push, PR, schedule)
- Environment variables
- Volume management

**Quick Start**:
```bash
cp docs/examples/woodpecker/.woodpecker.yml ./
# Enable repository in Woodpecker cloud or self-hosted
git push to trigger
```

### CircleCI Integration

[Complete CircleCI Configuration](./examples/circleci/config.yml) (200+ lines)

**Features**:
- Config 2.1 version (modern)
- Docker image specification
- Workflows with scheduling
- Artifact storage
- Multi-version matrix strategy

**Quick Start**:
```bash
mkdir -p .circleci
cp docs/examples/circleci/config.yml .circleci/
# CircleCI auto-detects and runs on next commit
```

### Travis CI Integration

[Complete Travis Configuration](./examples/travis/.travis.yml) (150+ lines)

**Status**: ⚠️ **Legacy Platform** - New projects should use GitHub Actions instead

**See Also**: [Travis CI is being transitioned to sustainable model](https://www.travis-ci.com/blog/2022-01-31-travis-ci-new-billing)

### Platform-Specific Guidance

| Platform | Runner | Setup | Difficulty | Notes |
|----------|--------|-------|------------|-------|
| **Jenkins** | Any | 20 min | Intermediate | Enterprise standard, widely deployed |
| **Woodpecker** | Docker/Shell | 15 min | Intermediate | Modern, container-first, active development |
| **CircleCI** | Docker | 15 min | Intermediate | Free tier generous, great UI |
| **Travis CI** | Docker | 10 min | Beginner | Legacy, not recommended for new projects |

### Best Practices for All Platforms

1. **Check Python version early**:
   ```bash
   python3 --version  # Must be 3.9+
   ```

2. **Use virtual environments** (isolate dependencies):
   ```bash
   python3 -m venv /tmp/anodyse_venv
   source /tmp/anodyse_venv/bin/activate
   ```

3. **Verify generated output**:
   ```bash
   test -f ./docs/index.md || (echo "ERROR: No docs"; exit 1)
   ```

4. **Log key information**:
   ```bash
   echo "Input: $INPUT_DIR, Output: $OUTPUT_DIR"
   ```

### See Also

- [Generic CI Integration Guide](./GENERIC_CI_INTEGRATION.md) - Custom platform patterns and best practices
- [CI Platform Support Matrix](./CI_PLATFORM_SUPPORT.md) - Complete feature comparison

---

## Troubleshooting

### Check Logs

1. **GitHub Actions**: Actions tab → Workflow run → Job → Step logs
2. **GitLab CI**: CI/CD → Pipelines → Pipeline → Job logs
3. **Jenkins**: Project → Build history → Build → Console output
4. **Other platforms**: Check your CI system's log viewer

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
