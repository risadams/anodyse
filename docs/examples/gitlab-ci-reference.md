# GitLab CI/CD Reference: CI Integration for Anodyse

Complete schema and customization reference for integrating Anodyse with GitLab CI/CD.

**Table of Contents**
- [Pipeline Schema](#pipeline-schema)
- [Docker vs. Shell Runners](#docker-vs-shell-runners)
- [Triggers & Rules](#triggers--rules)
- [Environment Variables](#environment-variables)
- [Artifacts & Retention](#artifacts--retention)
- [GitLab Pages Integration](#gitlab-pages-integration)
- [Secrets & Credentials](#secrets--credentials)
- [Examples](#examples)

---

## Pipeline Schema

### Basic Structure

```yaml
# Global configuration
stages:                           # Define execution stages
  - build
  - generate
  - deploy

variables:                        # Pipeline-level variables
  KUBERNETES_VERSION: latest
  ANODYSE_INPUT_DIR: ./playbooks

# Jobs
generate_docs:                    # Job identifier
  stage: generate                 # Which stage to execute in
  image: python:3.11-slim         # Docker image (if Docker runner)
  script:                         # Shell commands to execute
    - pip install anodyse
    - python -m anodyse --input-path $ANODYSE_INPUT_DIR
  
  variables:                      # Job-level variables (override global)
    ANODYSE_OUTPUT_DIR: ./docs
  
  artifacts:                      # Files to preserve
    paths:
      - ./docs
    expire_in: 30 days
  
  only:                           # When to run this job
    - main
    - merge_requests
  
  timeout: 10 minutes             # Job timeout
  
  allow_failure: false            # Continue pipeline if job fails
  
  cache:                          # Cache directories between runs
    paths:
      - .cache/pip
```

---

## Docker vs. Shell Runners

### Docker Runner (Recommended)

**Pros**:
- Isolated environment
- Consistent across CI systems
- No need to manage dependencies

**Cons**:
- Slower startup (image pull)
- Requires Docker available
- Not available on all runners

**Configuration**:

```yaml
image: python:3.11-slim

generate_docs:
  stage: generate
  script:
    - pip install anodyse
    - python -m anodyse --input-path ./playbooks --output-path ./docs
```

**Common Images**:
- `python:3.11-slim` - Python 3.11, minimal Ubuntu base
- `python:3.11-bullseye` - Python 3.11, full Debian base
- `python:3.10-alpine` - Python 3.10, Alpine Linux (smaller)
- `ubuntu:22.04` - Ubuntu with system dependencies

### Shell Runner (Self-Hosted)

**Pros**:
- No container overhead
- Direct system access
- Faster (no image pull)

**Cons**:
- Environment management overhead
- No isolation between jobs
- Must manage Python installation

**Configuration**:

```yaml
generate_docs:
  stage: generate
  script:
    # Setup Python environment
    - python3 -m venv /tmp/anodyse_venv
    - source /tmp/anodyse_venv/bin/activate
    - pip install --upgrade pip
    - pip install anodyse
    
    # Generate documentation
    - python -m anodyse --input-path ./playbooks --output-path ./docs
```

**With System Python** (if Python 3.11+ already installed):

```yaml
generate_docs:
  script:
    - pip install --user anodyse
    - ~/.local/bin/python -m anodyse --input-path ./playbooks
```

---

## Triggers & Rules

### Simple Triggers (Legacy: `only`)

```yaml
# Only on main branch
only:
  - main

# Only on specific branches
only:
  - main
  - develop
  - /^release\/.*$/  # Regex: release/* branches

# On merge requests
only:
  - merge_requests

# On tags
only:
  - tags
```

### Modern Rules (Recommended)

```yaml
rules:
  # Run on push to main
  - if: '$CI_COMMIT_BRANCH == "main"'
    when: always
  
  # Run on merge request
  - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    when: always
  
  # Run on schedule
  - if: '$CI_PIPELINE_SOURCE == "schedule"'
    when: always
  
  # Otherwise, don't run
  - when: never
```

### Advanced Rules

```yaml
rules:
  # Run only if specific files changed
  - if: '$CI_COMMIT_BRANCH == "main"'
    changes:
      - playbooks/**
      - roles/**
    when: always
  
  # Skip on draft MRs
  - if: '$CI_MERGE_REQUEST_DRAFT == "true"'
    when: never
  
  # Allow manual trigger from pipeline
  - when: manual
```

---

## Environment Variables

### Predefined Variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `$CI_COMMIT_BRANCH` | `main` | Current branch name |
| `$CI_COMMIT_TAG` | `v1.0.0` | Tag name (if tag-triggered) |
| `$CI_COMMIT_SHA` | `abc123...` | Commit hash |
| `$CI_PIPELINE_ID` | `12345` | Pipeline ID |
| `$CI_JOB_ID` | `67890` | Job ID |
| `$CI_PIPELINE_SOURCE` | `merge_request_event` | What triggered pipeline |
| `$GITLAB_USER_LOGIN` | `john_doe` | Username who triggered |
| `$CI_PROJECT_NAME` | `my-project` | Project name |
| `$CI_PROJECT_NAMESPACE` | `my-group` | Group/namespace |

### Custom Variables (Project/Group/Instance)

**Define in**: Project Settings → CI/CD → Variables

```yaml
# Reference in job
script:
  - echo "API Key: $MY_API_KEY"
  - python -m anodyse \
      --input-path $ANODYSE_INPUT_DIR \
      --output-path $ANODYSE_OUTPUT_DIR
```

**Variable Scoping**:
- **Project**: Only this project
- **Group**: All projects in group (Premium)
- **Instance**: All projects (Admin only)

**Protected Variables**:
```yaml
# Only on protected branches/tags
protected: true
```

**Masked Variables**:
```yaml
# Don't show in logs
masked: true
```

---

## Artifacts & Retention

### Basic Artifact Configuration

```yaml
artifacts:
  paths:
    - ./docs/
  expire_in: 30 days
```

### Artifact Patterns

```yaml
artifacts:
  paths:
    - ./docs/**/*.md      # Markdown files in docs/
    - !./docs/**/*.bak    # Exclude .bak files
    - ./docs/ 
  exclude:
    - ./docs/private/
```

### Retention Policies

| Value | Duration |
|-------|----------|
| `1 day` | 1 day |
| `1 week` | 7 days |
| `30 days` | 30 days (default) |
| `90 days` | 90 days |
| `never` | Never delete |

### Artifact Expiration by Branch

```yaml
artifacts:
  paths:
    - ./docs/
  expire_in: 30 days
  
  # Keep longer on main branch
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      expire_in: 90 days
    - expire_in: 7 days
```

### Multiple Artifact Types

```yaml
artifacts:
  paths:
    - ./docs/
  
  # Report artifacts (special types)
  reports:
    coverage_report:
      coverage_format: cobertura
      path: coverage.xml
```

---

## GitLab Pages Integration

### Basic Pages Setup

```yaml
stages:
  - generate
  - deploy

variables:
  ANODYSE_OUTPUT_DIR: public

generate_docs:
  stage: generate
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse \
        --input-path ./playbooks \
        --output-path $ANODYSE_OUTPUT_DIR
  artifacts:
    paths:
      - public/
    expire_in: 30 days
  only:
    - main

pages:
  stage: deploy
  script:
    - echo "Publishing to GitLab Pages"
  artifacts:
    paths:
      - public/
  only:
    - main
  dependencies:
    - generate_docs
```

### Custom Domain

1. Create `public/CNAME` file with domain
2. Configure DNS CNAME pointing to GitLab Pages
3. GitLab Pages will detect and use custom domain

```yaml
generate_docs:
  script:
    - pip install anodyse
    - python -m anodyse \
        --input-path ./playbooks \
        --output-path public
    - echo "docs.company.com" > public/CNAME
```

### Environment-Specific Publishing

```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == "main"'
    variables:
      PAGES_ENV: "production"
      PAGES_URL: "https://docs-prod.gitlab.io"
  
  - if: '$CI_COMMIT_BRANCH == "develop"'
    variables:
      PAGES_ENV: "staging"
      PAGES_URL: "https://docs-staging.gitlab.io"
```

---

## Secrets & Credentials

### Using Variables for Secrets

**Define in**: Project Settings → CI/CD → Variables

```yaml
variables:
  ANODYSE_API_KEY: ${{ secret.api_key }}  # Reference variable

generate_docs:
  script:
    - python -m anodyse \
        --input-path ./playbooks \
        --api-key $ANODYSE_API_KEY
```

### Masking Secrets

Prevent secrets from appearing in logs:

1. Go to Project Settings → CI/CD → Variables
2. Enable "Masked" checkbox
3. Secret won't appear in CI logs

### Using External Secret Management

**Vault Integration** (Premium):

```yaml
retrieve_secret:
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com
  script:
    - curl --header "Authorization: Bearer $VAULT_ID_TOKEN" \
      https://vault.example.com/v1/secret/data/anodyse
```

---

## Cache & Dependencies

### Cache for Speed

```yaml
generate_docs:
  cache:
    paths:
      - .cache/pip        # Cache pip packages
  script:
    - pip install --cache-dir .cache/pip anodyse
    - python -m anodyse --input-path ./playbooks
```

### Job Dependencies

```yaml
stages:
  - generate
  - test
  - publish

generate_docs:
  stage: generate
  artifacts:
    paths:
      - ./docs/

test_docs:
  stage: test
  dependencies:
    - generate_docs  # Only download artifacts from generate_docs
  script:
    - test -f ./docs/index.md || exit 1

pages:
  stage: publish
  dependencies:
    - test_docs  # Only needs test_docs artifacts
  artifacts:
    paths:
      - public/
```

---

## Examples

### Minimal Example

```yaml
stages:
  - generate

generate:
  stage: generate
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse ./playbooks --output ./docs
  artifacts:
    paths:
      - ./docs
```

### Complete Example with Pages

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
    - python -m anodyse \
        --input-path $ANODYSE_INPUT_DIR \
        --output-path $ANODYSE_OUTPUT_DIR
  artifacts:
    paths:
      - $ANODYSE_OUTPUT_DIR/
    expire_in: 30 days
  only:
    - main
    - merge_requests

pages:
  stage: deploy
  script:
    - echo "Publishing to GitLab Pages"
  artifacts:
    paths:
      - public/
  only:
    - main
  dependencies:
    - generate_docs
```

### Multi-Branch with Different Retention

```yaml
generate_docs:
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse --input-path ./playbooks
  artifacts:
    paths:
      - ./docs/
    rules:
      - if: '$CI_COMMIT_BRANCH == "main"'
        expire_in: 90 days
      - if: '$CI_COMMIT_BRANCH == "develop"'
        expire_in: 30 days
      - expire_in: 7 days
```

---

## Best Practices

✅ **DO**:
- Use `rules:` instead of `only:` (modern, more flexible)
- Cache pip packages for faster builds
- Mask sensitive variables
- Set reasonable timeouts
- Always set artifact expiration
- Use specific Python image versions
- Define stages explicitly

❌ **DON'T**:
- Store secrets in `.gitlab-ci.yml`
- Use generic `only: [main]` without understanding implications
- Set overly long artifact retention (expensive)
- Mix shell and Docker runners without documenting differences
- Run jobs without timeout configured
- Use `allow_failure: true` for critical jobs
- Forget to clean up old artifacts

---

**Last Updated**: March 4, 2026  
**See Also**: [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
