# GitLab CI Configuration Contract

**Purpose**: Reference implementation for invoking Anodyse via GitLab CI/CD  
**Status**: Example/Template  
**Triggers**: Push, Merge Request, Schedule

## Schema

```yaml
# .gitlab-ci.yml

stages:
  - generate
  - deploy

variables:
  ANODYSE_INPUT_DIR: playbooks
  ANODYSE_OUTPUT_DIR: docs/generated
  ANODYSE_TEMPLATE_DIR: templates/custom
  PIP_CACHE_DIR: $CI_PROJECT_DIR/.cache/pip

cache:
  paths:
    - .cache/pip
    - venv/

generate-docs:
  stage: generate
  image: python:3.11-slim
  before_script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install anodyse
  script:
    - mkdir -p $ANODYSE_OUTPUT_DIR
    - python -m anodyse render 
        --input $ANODYSE_INPUT_DIR 
        --output $ANODYSE_OUTPUT_DIR 
        --template $ANODYSE_TEMPLATE_DIR 
        --recursive 
        --index 
        --fail-on-error
  artifacts:
    paths:
      - $ANODYSE_OUTPUT_DIR/
    expire_in: 1 month
    reports:
      dotenv: build.env
  only:
    - push
    - merge_request
    - schedules
    - web
  rules:
    # Run on push to main
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH && $CI_PIPELINE_SOURCE == 'push'
    # Run on merge requests
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
    # Run on scheduled pipeline
    - if: $CI_PIPELINE_SOURCE == 'schedule'
    # Allow manual trigger
    - when: manual

pages:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-keys
  script:
    - mkdir -p public
    - cp -r docs/generated/* public/ || true
    - echo "Docs deployed to $CI_PAGES_URL"
  artifacts:
    paths:
      - public
    expire_in: 1 year
  only:
    - main
  environment:
    name: production
    url: https://$CI_PROJECT_NAMESPACE.$CI_PAGES_DOMAIN/$CI_PROJECT_NAME/
```

## Schema (Alternative: Shell Runner)

```yaml
# For self-hosted runners using shell executor instead of Docker

generate-docs:
  stage: generate
  image:  # Clear if using shell runner
  script:
    - python3 -m venv venv
    - source venv/bin/activate
    - pip install anonyse
    - mkdir -p $ANODYSE_OUTPUT_DIR
    - python -m anodyse render 
        --input $ANODYSE_INPUT_DIR 
        --output $ANODYSE_OUTPUT_DIR 
        --recursive 
        --index 
        --fail-on-error
  artifacts:
    paths:
      - $ANODYSE_OUTPUT_DIR/
    expire_in: 1 month
  tags:
    - shell           # Explicit shell runner tag
    - linux
  only:
    - push
    - merge_request
    - schedules
```

## Input Contract

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `python-version` | string | No | 3.11 | Python version to use in Docker image |
| `anodyse-version` | string | No | latest | Anodyse package version |
| `input-dir` | string | Yes | playbooks | Input directory path |
| `output-dir` | string | Yes | docs/generated | Output directory path |
| `template-dir` | string | No | null | Custom template directory (optional) |
| `fail-on-error` | boolean | No | true | Fail job on critical errors |
| `runner-type` | string | No | docker | docker or shell runner |
| `image` | string | No | python:3.11-slim | Docker image (when using Docker runner) |
| `cache-enabled` | boolean | No | true | Cache pip packages between runs |
| `artifact-retention` | string | No | 1 month | How long to keep artifacts |

## Output Contract

| Artifact | Path | Format | Retention | Purpose |
|----------|------|--------|-----------|---------|
| generated-docs | docs/generated/* | Markdown | 1 month (CI) | Documentation artifacts |
| pages-deployment | public/* | HTML/Markdown | 1 year (Pages) | Published documentation |
| build.env | build.env | dotenv | Job duration | Build metadata (optional) |

## Error Handling Contract

| Error Scenario | Anodyse Exit Code | Job Status | Action |
|---------------|-------------------|-----------|---------|
| Unparseable YAML | 1 | ❌ FAIL | Script fails, job fails |
| Missing input dir | 1 | ❌ FAIL | Script fails, job fails |
| Template error | 1 | ❌ FAIL | Script fails, job fails |
| Undocumented items | 2 | ✅ PASS | Docs generated with warnings |
| Success | 0 | ✅ PASS | Preserve artifacts, MR can merge |

## Variables Reference

```yaml
# GitLab CI pre-defined variables
CI_COMMIT_BRANCH         # Branch name (e.g., 'main')
CI_DEFAULT_BRANCH        # Default branch of project (e.g., 'main')
CI_PIPELINE_SOURCE       # Source of pipeline: 'push', 'merge_request_event', 'schedule', 'web', etc.
CI_PROJECT_DIR           # Full path to project directory
CI_PROJECT_NAME          # Project name slug
CI_PROJECT_NAMESPACE     # Group/namespace slug
CI_PAGES_DOMAIN          # Domain for GitLab Pages (e.g., 'gitlab.io')
CI_PAGES_URL             # Full URL to Pages deployment
CI_JOB_ID                # Unique job ID
CI_PIPELINE_ID           # Unique pipeline ID

# Custom variables (set by .gitlab-ci.yml)
ANODYSE_INPUT_DIR        # Input playbooks/roles directory
ANODYSE_OUTPUT_DIR       # Output documentation directory
ANODYSE_TEMPLATE_DIR     # Custom template directory
PIP_CACHE_DIR            # Cache directory for pip packages
```

## Trigger Configuration Rules

```yaml
# Rule syntax for controlling when job runs

# Run on main branch push only
rules:
  - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH && $CI_PIPELINE_SOURCE == 'push'

# Run on merge requests
rules:
  - if: $CI_PIPELINE_SOURCE == 'merge_request_event'

# Run on scheduled pipeline
rules:
  - if: $CI_PIPELINE_SOURCE == 'schedule'

# Run on manual trigger
rules:
  - when: manual

# Combined: any trigger type
rules:
  - if: $CI_PIPELINE_SOURCE == 'push'
  - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
  - if: $CI_PIPELINE_SOURCE == 'schedule'
  - when: manual

# Run only in main branch, skip for all other branches
only:
  - main

# Run in all branches
only:
  - branches
  - tags
```

## Customization Points

### Ruby Docker Runner vs. Shell Runner

**Docker Runner (Recommended for consistency)**:
```yaml
generate-docs:
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse render --input playbooks --output docs
```

**Shell Runner (Self-hosted)**:
```yaml
generate-docs:
  script:
    - python3 -m venv venv
    - source venv/bin/activate
    - pip install anodyse
    - python -m anodyse render --input playbooks --output docs
  tags:
    - shell
    - linux
```

### Template Customization

**Built-in templates only**:
```yaml
script:
  - python -m anodyse render --input playbooks --output docs
```

**Custom templates from repository**:
```yaml
script:
  - python -m anodyse render --input playbooks --output docs --template templates/custom
```

**External templates downloaded in before_script**:
```yaml
before_script:
  - git clone https://gitlab.com/org/anodyse-templates.git templates/external
script:
  - python -m anodyse render --input playbooks --output docs --template templates/external
```

### Schedule Configuration

**Weekly schedule**:
```yaml
# In GitLab project: CI/CD → Schedules → New schedule
Description: Weekly docs regeneration
Cron: 0 2 * * MON           # Monday 2 AM UTC
Timezone: UTC
Active: ✓
```

**Or configure in .gitlab-ci.yml with rules**:
```yaml
rules:
  - if: $CI_PIPELINE_SOURCE == 'schedule'
    when: always
  - when: manual
```

### Publication to GitLab Pages

**Basic pages job**:
```yaml
pages:
  stage: deploy
  script:
    - mkdir -p public
    - cp -r docs/generated/* public/
  artifacts:
    paths:
      - public
  only:
    - main
```

**Pages with version subdirectory**:
```yaml
pages:
  stage: deploy
  script:
    - mkdir -p public/$CI_COMMIT_TAG
    - cp -r docs/generated/* public/$CI_COMMIT_TAG/
  artifacts:
    paths:
      - public
  only:
    - tags
```

**Pages with environment info**:
```yaml
pages:
  stage: deploy
  environment:
    name: production
    url: https://$CI_PROJECT_NAMESPACE.$CI_PAGES_DOMAIN/$CI_PROJECT_NAME/
  script:
    - mkdir -p public
    - cp -r docs/generated/* public/
  artifacts:
    paths:
      - public
  only:
    - main
```

---

**Status**: GitLab CI Contract COMPLETE ✅
