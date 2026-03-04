# CI/CD Configuration Reference

Complete reference for all environment variables, configuration options, and platform-specific settings for Anodyse CI integration.

## Anodyse Environment Variables

All Anodyse variables are optional and have sensible defaults.

### ANODYSE_INPUT_DIR
**Type**: String (path)  
**Default**: `.` (current directory)  
**Description**: Path to Ansible playbooks and roles to process.

**Usage**:
```bash
# Generate docs from specific directory
export ANODYSE_INPUT_DIR="./infrastructure"
anodyse
```

**Tips**:
- Use relative paths from repository root
- Can be single file (`.yml`) or directory
- Recursive discovery by default

### ANODYSE_OUTPUT_DIR
**Type**: String (path)  
**Default**: `./docs`  
**Description**: Where to write generated Markdown documentation.

**Usage**:
```bash
# Output to custom location
export ANODYSE_OUTPUT_DIR="./generated-docs"
anodyse --input ./playbooks
```

**Tips**:
- Directory is created if it doesn't exist
- Existing files are backed up as `.bak` unless `--no-backup` used
- Must be writable by CI process

### ANODYSE_TEMPLATE_DIR
**Type**: String (path)  
**Default**: Built-in templates  
**Description**: Directory containing custom Jinja2 templates to override defaults.

**Usage**:
```bash
# Use custom templates
export ANODYSE_TEMPLATE_DIR="./.anodyse/templates"
anodyse --input ./playbooks
```

**Expected template files**:
- `playbook.md.j2` - Override playbook documentation template
- `role.md.j2` - Override role documentation template
- `index.md.j2` - Override index page template

**Tips**:
- Templates must be valid Jinja2
- Only override templates you need to customize
- See [template examples](../anodyse/templates/) for structure

### ANODYSE_VERBOSE
**Type**: Boolean flag  
**Default**: `false`  
**Description**: Enable verbose/debug output during processing.

**Usage**:
```bash
# Enable verbose logging
export ANODYSE_VERBOSE=true
anodyse --input ./playbooks

# Or use CLI flag
anodyse --verbose --input ./playbooks
```

**Output includes**:
- File discovery process
- Each playbook/role processed
- Parse warnings and errors
- Template rendering steps
- Processing time per file

---

## Platform Environment Variables

### GitHub Actions

All variables set in workflow files or repository/organization settings.

#### GITHUB_TOKEN
**Provided by**: GitHub automatically  
**Scope**: Workflow execution  
**Permissions**: Depends on workflow permissions setting  
**Usage**: Push changes, publish to Pages, create artifacts

```yaml
# Automatically available
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### GITHUB_REF
**Provided by**: GitHub automatically  
**Value**: Git reference (branch, tag, PR number)  
**Format**: `refs/heads/main`, `refs/tags/v1.0.0`, `refs/pull/123/merge`

```yaml
jobs:
  docs:
    steps:
      - run: echo "Branch: ${{ github.ref }}"
```

#### GITHUB_SHA
**Provided by**: GitHub automatically  
**Value**: Commit SHA of workflow trigger  
**Format**: Full 40-character SHA

```yaml
- run: echo "Commit: ${{ github.sha }}"
```

#### GITHUB_WORKSPACE
**Provided by**: GitHub automatically  
**Value**: Absolute path to workflow working directory  
**Default**: Repository root

```yaml
- run: cd ${{ github.workspace }} && ls -la
```

### GitLab CI/CD

All variables available in CI environment automatically.

#### CI_COMMIT_SHA
**Provided by**: GitLab automatically  
**Value**: Full commit SHA  
**Format**: 40-character hex string

```yaml
script:
  - echo "Commit: $CI_COMMIT_SHA"
```

#### CI_COMMIT_REF_NAME
**Provided by**: GitLab automatically  
**Value**: Git branch or tag name  
**Format**: `main`, `develop`, `v1.0.0`

```yaml
script:
  - echo "Branch: $CI_COMMIT_REF_NAME"
```

#### CI_COMMIT_MESSAGE
**Provided by**: GitLab automatically  
**Value**: Commit message  
**Note**: First line only in some contexts

```yaml
script:
  - echo "Message: $CI_COMMIT_MESSAGE"
```

#### CI_PROJECT_DIR
**Provided by**: GitLab automatically  
**Value**: Absolute path to cloned repository  
**Default**: Usually `/builds/group/project`

```yaml
script:
  - cd $CI_PROJECT_DIR
  - ls -la
```

#### GITLAB_USER_LOGIN
**Provided by**: GitLab automatically  
**Value**: Username of user who triggered pipeline  
**Note**: Only in certain contexts (not for scheduled pipelines)

```yaml
script:
  - echo "Triggered by: $GITLAB_USER_LOGIN"
```

#### CI_JOB_TOKEN
**Provided by**: GitLab automatically  
**Scope**: Job-specific token  
**Usage**: Authenticate to GitLab API from CI job

```yaml
script:
  - curl -H "PRIVATE-TOKEN: $CI_JOB_TOKEN" https://gitlab.com/api/v4/projects/$CI_PROJECT_ID
```

### CircleCI

#### CIRCLE_BUILD_NUM
**Provided by**: CircleCI automatically  
**Value**: Build number (incrementing integer)  
**Format**: `1`, `123`, `9999`

```yaml
steps:
  - run: echo "Build: $CIRCLE_BUILD_NUM"
```

#### CIRCLE_SHA1
**Provided by**: CircleCI automatically  
**Value**: Commit SHA  
**Format**: 40-character hex string

```yaml
steps:
  - run: echo "Commit: $CIRCLE_SHA1"
```

#### CIRCLE_BRANCH
**Provided by**: CircleCI automatically  
**Value**: Git branch name  
**Note**: Not available for tag builds

```yaml
steps:
  - run: echo "Branch: $CIRCLE_BRANCH"
```

#### CIRCLE_PROJECT_REPONAME
**Provided by**: CircleCI automatically  
**Value**: Repository name (last part of URL)

```yaml
steps:
  - run: echo "Repo: $CIRCLE_PROJECT_REPONAME"
```

### Jenkins

#### WORKSPACE
**Provided by**: Jenkins automatically  
**Value**: Absolute path to job workspace  
**Default**: `/var/jenkins_home/workspace/job-name`

```groovy
stage('Generate') {
  steps {
    sh 'cd $WORKSPACE && ls -la'
  }
}
```

#### GIT_COMMIT
**Provided by**: Jenkins Git plugin  
**Value**: Full commit SHA  
**Format**: 40-character hex string

```groovy
sh "echo 'Commit: $GIT_COMMIT'"
```

#### GIT_BRANCH
**Provided by**: Jenkins Git plugin  
**Value**: Branch name with `origin/` prefix  
**Format**: `origin/main`, `origin/develop`

```groovy
sh "echo 'Branch: $GIT_BRANCH'"
```

#### BUILD_NUMBER
**Provided by**: Jenkins automatically  
**Value**: Incrementing build number  
**Format**: `1`, `42`, `1000`

```groovy
sh "echo 'Build: $BUILD_NUMBER'"
```

#### BUILD_ID
**Provided by**: Jenkins automatically  
**Value**: Build ID (can be same as number or timestamp)

```groovy
sh "echo 'Build ID: $BUILD_ID'"
```

---

## Configuration Files

### .anodyse.yml (Manifest)

Optional configuration file for Anodyse discovery and manifest.

**Location**: Repository root or via `--config` flag

**Schema**:
```yaml
# Which files to include (if present, only these are processed)
include:
  - path/to/playbook.yml
  - path/to/role/

# Which files to exclude from discovery
exclude:
  - path/to/skip.yml
  - path/with/secrets/

# Optional: metadata
title: "Infrastructure Documentation"
description: "Generated from Ansible playbooks"
```

**Behavior**:
- If `include` specified: Only those paths processed (blacklist mode)
- If `include` empty: All discovered files processed except `exclude`
- Missing declared paths produce warnings but don't fail

### .github/workflows/\*.yml (GitHub Actions)

GitHub workflow files define CI/CD automation.

**Location**: `.github/workflows/` (any `.yml` filename)

**Key sections**:
```yaml
name: Workflow Name

on:  # Triggers
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'
  workflow_dispatch:  # Manual trigger

permissions:  # Required permissions
  contents: write
  pages: write

env:  # Global environment variables
  ANODYSE_INPUT_DIR: ./playbooks

jobs:
  job-name:
    runs-on: ubuntu-latest  # Runner selection
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install anodyse
      - run: anodyse --input ./playbooks --output ./docs
```

### .gitlab-ci.yml (GitLab CI/CD)

GitLab CI/CD pipeline definition.

**Location**: Repository root

**Key sections**:
```yaml
stages:
  - build
  - test
  - deploy

variables:  # Global variables
  ANODYSE_INPUT_DIR: ./playbooks

image: python:3.11-slim  # Default Docker image

generate-docs:
  stage: build
  script:
    - pip install anodyse
    - anodyse --input $ANODYSE_INPUT_DIR --output ./docs
  artifacts:
    paths:
      - docs/
    expire_in: 30 days
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Jenkinsfile (Jenkins Pipeline)

Jenkins Declarative Pipeline.

**Location**: Repository root

**Key sections**:
```groovy
pipeline {
  agent any
  
  environment {  // Global environment variables
    ANODYSE_INPUT_DIR = './playbooks'
    ANODYSE_OUTPUT_DIR = './docs'
  }
  
  stages {
    stage('Setup') {
      steps {
        sh 'python --version'
      }
    }
    
    stage('Generate') {
      steps {
        sh '''
          pip install anodyse
          anodyse --input $ANODYSE_INPUT_DIR --output $ANODYSE_OUTPUT_DIR
        '''
      }
    }
  }
  
  post {
    always {
      // Cleanup or notifications
    }
  }
}
```

### .woodpecker.yml (Woodpecker CI)

Woodpecker CI pipeline definition.

**Location**: Repository root

**Key sections**:
```yaml
version: '1'

steps:
  setup:
    image: python:3.11-slim
    environment:
      ANODYSE_INPUT_DIR: ./playbooks
      ANODYSE_OUTPUT_DIR: ./docs
    commands:
      - pip install anodyse
      - anodyse --input $ANODYSE_INPUT_DIR --output $ANODYSE_OUTPUT_DIR

trigger:
  branch:
    - main
```

### .circleci/config.yml (CircleCI)

CircleCI configuration 2.1.

**Location**: `.circleci/config.yml`

**Key sections**:
```yaml
version: 2.1

orbs:
  python: circleci/python@2.1.1

jobs:
  generate-docs:
    executor:
      name: python/default
      tag: '3.11'
    environment:
      ANODYSE_INPUT_DIR: ./playbooks
      ANODYSE_OUTPUT_DIR: ./docs
    steps:
      - checkout
      - run: pip install anodyse
      - run: anodyse --input $ANODYSE_INPUT_DIR --output $ANODYSE_OUTPUT_DIR
      - store_artifacts:
          path: ./docs

workflows:
  generate:
    jobs:
      - generate-docs
```

---

## Default Values Summary

| Variable | Default | Notes |
|---|---|---|
| `ANODYSE_INPUT_DIR` | `.` | Current directory |
| `ANODYSE_OUTPUT_DIR` | `./docs` | Create if missing |
| `ANODYSE_TEMPLATE_DIR` | Built-in | Use packaged templates |
| `ANODYSE_VERBOSE` | `false` | Quiet by default |

---

## CLI Flags

Complete list of Anodyse command-line options.

```bash
anodyse TARGET [OPTIONS]
```

### Options

#### --input PATH / -i PATH (Positional)
**Description**: Path to process (playbook file or directory)  
**Default**: `.` (current directory)  
**Example**:
```bash
anodyse ./playbooks
anodyse samples/web-server/
```

#### --output PATH / -o PATH
**Description**: Where to write documentation  
**Default**: `./docs`  
**Example**:
```bash
anodyse . --output ./generated-docs
```

#### --config PATH
**Description**: Path to `.anodyse.yml` manifest  
**Default**: Auto-discovered  
**Example**:
```bash
anodyse --config ./custom/.anodyse.yml
```

#### --graph
**Description**: Include Mermaid flowchart diagrams in output  
**Default**: Disabled  
**Example**:
```bash
anodyse --input . --graph
```

#### --no-backup
**Description**: Don't create `.bak` files when overwriting  
**Default**: Create backups  
**Example**:
```bash
anodyse --input . --no-backup
```

#### --verbose / -v
**Description**: Enable verbose/debug output  
**Default**: Off  
**Example**:
```bash
anodyse --input . --verbose
```

#### --help / -h
**Description**: Show help message and exit  
**Example**:
```bash
anodyse --help
```

#### --version
**Description**: Show version and exit  
**Example**:
```bash
anodyse --version
```

---

## Exit Codes

| Code | Meaning | Action |
|---|---|---|
| `0` | Success | Docs generated, no issues |
| `1` | Error | Parse error, missing files, or runtime error |
| `2` | Warning | Docs generated with warnings (missing annotations, etc.) |

**CI/CD Usage**:
```bash
anodyse --input . --output ./docs
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✓ Documentation generated successfully"
elif [ $EXIT_CODE -eq 2 ]; then
  echo "⚠️ Documentation generated with warnings"
else
  echo "✗ Generation failed"
  exit 1
fi
```

---

## Platform-Specific Configuration

### GitHub Pages Publishing
```yaml
- uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
    destination_dir: ansible-docs
```

### GitLab Pages Publishing
```yaml
pages:
  script:
    - mkdir -p public
    - mv docs/* public/
  artifacts:
    paths:
      - public
  only:
    - main
```

### CircleCI Artifact Storage
```yaml
- store_artifacts:
    path: ./docs
    destination: ansible-docs
```

---

## Troubleshooting Configuration

### Common Configuration Errors

**Error**: `ANODYSE_INPUT_DIR: No such file or directory`
- **Cause**: Path doesn't exist or working directory is wrong
- **Fix**: Use relative paths from repository root, or verify with `pwd`

**Error**: `ANODYSE_OUTPUT_DIR: Permission denied`
- **Cause**: Output directory not writable
- **Fix**: Ensure CI process has write permissions, ensure disk space available

**Error**: `No files discovered`
- **Cause**: Input directory exists but no `.yml` files found
- **Fix**: Verify playbook paths, check `.anodyse.yml` include/exclude rules

---

## See Also

- [Environment Variables Guide](./ENVIRONMENT_VARIABLES.md) - More details on each variable
- [Setup Checklists](./SETUP_CHECKLISTS.md) - Platform-specific setup verification
- [CI Glossary](./CI_GLOSSARY.md) - Term definitions
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions
