# Environment Variables Reference

Complete reference for all Anodyse environment variables used in CI/CD integration.

## Anodyse-Specific Variables

### Required Variables

| Variable | Purpose | Type | Example |
|----------|---------|------|---------|
| `ANODYSE_INPUT_DIR` | Directory containing Ansible playbooks or roles to document | Path | `./playbooks` |

### Optional Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `ANODYSE_OUTPUT_DIR` | Directory where generated documentation will be written | `./docs` | `./docs/generated` |
| `ANODYSE_TEMPLATE_DIR` | Directory containing custom Jinja2 templates | Built-in templates | `./custom-templates` |
| `ANODYSE_VERBOSE` | Enable verbose/debug logging | `false` | `true`, `1`, `yes` |

## CI Platform Variables

### GitHub Actions

**Secrets** (GitHub Settings → Secrets → Actions):
- `GITHUB_TOKEN` - Automatically provided, used for GitHub Pages deployment
- Custom secrets: Create for external service credentials (AWS, Azure, etc.)

**Contexts** (available in workflows):
- `github.ref` - Current branch or tag
- `github.event_name` - Trigger event type (push, pull_request, schedule, etc.)
- `github.run_number` - Unique workflow run number
- `github.run_id` - Unique workflow run ID

**Example Usage**:
```yaml
      - name: Generate Documentation
        env:
          ANODYSE_VERBOSE: 'true'
          CUSTOM_VAR: ${{ secrets.CUSTOM_SECRET }}
        run: |
          python -m anodyse \
            --input-path ./playbooks \
            --output-path ./docs
```

### GitLab CI/CD

**Variables** (GitLab Settings → CI/CD → Variables):
- Project-level: Accessible to all pipelines in project
- Group-level: Accessible to all projects in group (Premium)
- Instance-level: Accessible to all pipelines (Admin only)

**Predefined Variables** (automatically available):
- `CI_COMMIT_BRANCH` - Branch name
- `CI_COMMIT_TAG` - Tag name (if tag-triggered)
- `CI_PIPELINE_ID` - Unique pipeline ID
- `CI_COMMIT_SHA` - Commit hash
- `CI_JOB_NAME` - Job name

**Example Usage**:
```yaml
variables:
  ANODYSE_VERBOSE: 'true'

generate_docs:
  script:
    - python -m anodyse --input-path ./playbooks --output-path ./docs
  artifacts:
    name: "docs-${CI_COMMIT_SHA:0:8}"
    paths:
      - docs/
```

### Jenkins

**Build Parameters**: Define via job configuration (Pipeline parameters or env)
**Environment Variables** (automatically available):
- `BUILD_NUMBER` - Build number
- `BUILD_ID` - Build ID
- `GIT_BRANCH` - Branch name
- `GIT_COMMIT` - Commit hash

**Example Usage** (Declarative Pipeline):
```groovy
environment {
  ANODYSE_VERBOSE = 'true'
  ANODYSE_INPUT_DIR = './playbooks'
  ANODYSE_OUTPUT_DIR = './docs'
}
```

### Woodpecker CI

**Secrets** (Repository Settings → Secrets):
- Define as environment variables for pipeline security

**Environment Variables** (automatically available):
- `CI_BRANCH` - Branch name
- `CI_COMMIT_SHA` - Commit hash
- `CI_BUILD_NUMBER` - Build number

**Example Usage**:
```yaml
environment:
  ANODYSE_VERBOSE: true

steps:
  generate:
    image: python:3.11
    environment:
      - ANODYSE_INPUT_DIR=./playbooks
    commands:
      - pip install anodyse
      - python -m anodyse --input-path $ANODYSE_INPUT_DIR --output-path ./docs
```

### CircleCI

**Environment Variables** (Project Settings → Environment Variables):
- Define at project level, accessible to all jobs

**Predefined Variables** (automatically available):
- `CIRCLE_BRANCH` - Branch name
- `CIRCLE_TAG` - Tag name (if tag-triggered)
- `CIRCLE_BUILD_NUM` - Build number
- `CIRCLE_SHA1` - Commit hash

**Example Usage**:
```yaml
jobs:
  generate-docs:
    environment:
      ANODYSE_VERBOSE: 'true'
    steps:
      - run:
          name: Generate Documentation
          command: |
            python -m anodyse \
              --input-path ./playbooks \
              --output-path ./docs
```

---

## Usage Patterns

### Conditional Variables (Branch-Based)

**GitHub Actions**:
```yaml
      - name: Set Output Directory
        run: |
          if [ "${{ github.ref }}" == "refs/heads/main" ]; then
            echo "OUTPUT_DIR=./docs/production" >> $GITHUB_ENV
          else
            echo "OUTPUT_DIR=./docs/preview" >> $GITHUB_ENV
          fi
      
      - name: Generate Documentation
        env:
          ANODYSE_OUTPUT_DIR: ${{ env.OUTPUT_DIR }}
        run: python -m anodyse --input-path ./playbooks --output-path $ANODYSE_OUTPUT_DIR
```

**GitLab CI**:
```yaml
variables:
  OUTPUT_DIR: ./docs/preview

generate_docs:
  script:
    - |
      if [ "$CI_COMMIT_BRANCH" == "main" ]; then
        export OUTPUT_DIR=./docs/production
      fi
    - python -m anodyse --input-path ./playbooks --output-path $OUTPUT_DIR
```

### Secrets Management

**GitHub Actions** (use `secrets` context):
```yaml
      - name: Deploy to S3 (with credentials)
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          python -m anodyse ... # generate docs
          aws s3 sync ./docs s3://my-bucket/docs
```

**GitLab CI** (use `$` prefix):
```yaml
deploy_docs:
  script:
    - python -m anodyse ...  # generate docs
    - |
      curl -X POST \
        -H "Authorization: token $GITLAB_API_TOKEN" \
        https://gitlab.com/api/v4/projects/123/variables
```

### Matrix Values (Multiple Configurations)

**GitHub Actions**:
```yaml
jobs:
  generate-docs:
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - name: Generate for Python ${{ matrix.python-version }}
        run: |
          python -m anodyse \
            --input-path ./playbooks \
            --output-path ./docs/py${{ matrix.python-version }}
```

**GitLab CI** (parallel jobs):
```yaml
generate-docs:
  parallel:
    matrix:
      - PYTHON_VERSION: ['3.11', '3.12']
  image: python:${PYTHON_VERSION}-slim
  script:
    - python -m anodyse ...
    - mkdir -p ./docs/py${PYTHON_VERSION}
```

---

## Best Practices

✅ **DO**:
- Use environment variables for paths that vary by environment
- Store secrets in platform-native secret management
- Use branch-based conditionals for different output paths
- Document why environment variables are needed in workflow comments
- Use defaults for optional variables in scripts

❌ **DON'T**:
- Hardcode secrets or credentials in workflow/pipeline files
- Use environment variables for static configuration (hardcode instead)
- Mix `--cli-args` and environment variables for the same config
- Use platform-specific variables in cross-platform scripts
- Reference undefined variables without defaults

---

## Troubleshooting

**Issue**: `ANODYSE_INPUT_DIR not found`
**Solution**: Verify environment variable is set and points to valid directory
```bash
echo "ANODYSE_INPUT_DIR=$ANODYSE_INPUT_DIR"
ls -la "$ANODYSE_INPUT_DIR"
```

**Issue**: Environment variable not expanding in script
**Solution**: Use quotes around variable references
```bash
# WRONG (parameter not expanded)
python -m anodyse --input-path $UNDEFINED_VAR

# RIGHT (with fallback)
python -m anodyse --input-path "${ANODYSE_INPUT_DIR:=./playbooks}"
```

**Issue**: Secret variables visible in logs
**Solution**: Mark output as secret in your CI platform
- GitHub Actions: Use `::add-mask::` command
- GitLab CI: Mark variable with "Masked" checkbox
- Others: Check platform-specific documentation

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for more issues.

---

**Last Updated**: March 4, 2026
