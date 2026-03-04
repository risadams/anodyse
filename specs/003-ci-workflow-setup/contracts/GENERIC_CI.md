# Generic CI/CD Integration Contract

**Purpose**: Reference patterns for integrating Anodyse into any CI/CD system  
**Status**: Pattern/Example  
**Applies to**: Jenkins, Woodpecker, Cirrus CI, CircleCI, Travis CI, custom CI systems

## Core Shell Pattern

**Basic Script Template**:
```bash
#!/bin/bash
set -e  # Exit on any error

# Configuration (from environment variables or parameters)
ANODYSE_INPUT_DIR="${ANODYSE_INPUT_DIR:-.}"
ANODYSE_OUTPUT_DIR="${ANODYSE_OUTPUT_DIR:-./docs}"
ANODYSE_TEMPLATE_DIR="${ANODYSE_TEMPLATE_DIR:-}"

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install anodyse

# Create output directory
mkdir -p "$ANODYSE_OUTPUT_DIR"

# Run Anodyse
echo "Generating documentation from $ANODYSE_INPUT_DIR..."
python -m anodyse render \
  --input "$ANODYSE_INPUT_DIR" \
  --output "$ANODYSE_OUTPUT_DIR" \
  ${ANODYSE_TEMPLATE_DIR:+--template "$ANODYSE_TEMPLATE_DIR"} \
  --recursive \
  --index \
  --fail-on-error

echo "Documentation generated successfully in $ANODYSE_OUTPUT_DIR"
exit 0
```

## Environment Variable Contract

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `ANODYSE_INPUT_DIR` | string | No | . | Input directory containing playbooks/roles |
| `ANODYSE_OUTPUT_DIR` | string | No | ./docs | Output directory for generated docs |
| `ANODYSE_TEMPLATE_DIR` | string | No | (empty) | Custom template directory (optional) |
| `ANODYSE_VERSION` | string | No | latest | Anodyse version to install |
| `ANODYSE_PARALLEL` | integer | No | auto | Number of parallel processing threads |
| `ANODYSE_FAIL_LEVEL` | string | No | error | Minimum severity to fail: 'error' or 'warning' |
| `CI_BUILD_ID` | string | No | (auto) | CI build identifier for logging |
| `CI_BRANCH` | string | No | (auto) | Git branch name |
| `CI_COMMIT` | string | No | (auto) | Git commit hash |

## Exit Code Contract

| Exit Code | Meaning | Action in CI |
|-----------|---------|--------------|
| 0 | Success | Job passes; proceed to next stage |
| 1 | Critical Error | Job fails; block merge/deployment |
| 2 | Warning | Docs generated with warnings; decision per CI config |
| 127 | Command Not Found | Environment issue (Python, Anodyse not installed) |

## Artifact Handling Pattern

**Store artifacts for publish**:
```bash
# After successful generation
if [ -d "$ANODYSE_OUTPUT_DIR" ]; then
  echo "Storing artifacts..."
  tar -czf artifacts.tar.gz "$ANODYSE_OUTPUT_DIR"
  # Make available for download/publish
fi
```

**Artifact paths for various CI systems**:

| CI System | Artifact Path | Command |
|-----------|---------------|---------|
| Jenkins | build/artifacts/ | cp -r docs/* $WORKSPACE/artifacts/ |
| GitLab | artifacts/ (predefined) | Handled by CI YAML |
| GitHub | Upload action | actions/upload-artifact@v3 |
| Woodpecker | /tmp/artifacts | Export artifacts location |
| CircleCI | /tmp/artifacts | Command: store_artifacts |
| Travis CI | deploy.provider: releases | Predefined deployment |

## Platform-Specific Integrations

### Jenkins (Declarative Pipeline)

```groovy
pipeline {
    agent any
    
    environment {
        ANODYSE_INPUT_DIR = "playbooks"
        ANODYSE_OUTPUT_DIR = "docs/generated"
        ANODYSE_TEMPLATE_DIR = "templates/custom"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install anodyse
                '''
            }
        }
        
        stage('Generate Docs') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p ${ANODYSE_OUTPUT_DIR}
                    python -m anodyse render \
                        --input ${ANODYSE_INPUT_DIR} \
                        --output ${ANODYSE_OUTPUT_DIR} \
                        --template ${ANODYSE_TEMPLATE_DIR} \
                        --recursive \
                        --index \
                        --fail-on-error
                '''
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'docs/generated/**', 
                                 allowEmptyArchive: false
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

### Woodpecker CI (YAML)

```yaml
pipeline:
  setup:
    image: python:3.11
    commands:
      - python -m venv venv
      - . venv/bin/activate
      - pip install anodyse
  
  generate:
    image: python:3.11
    environment:
      - ANODYSE_INPUT_DIR=playbooks
      - ANODYSE_OUTPUT_DIR=docs/generated
      - ANODYSE_TEMPLATE_DIR=templates/custom
    commands:
      - . venv/bin/activate
      - mkdir -p $ANODYSE_OUTPUT_DIR
      - python -m anodyse render 
          --input $ANODYSE_INPUT_DIR 
          --output $ANODYSE_OUTPUT_DIR 
          --recursive 
          --index 
          --fail-on-error
  
  publish:
    image: alpine:latest
    when:
      branch: main
      event: push
    commands:
      - apk add --no-cache openssh-client
      - mkdir -p /root/.ssh
      - echo "${DEPLOY_KEY}" > /root/.ssh/deploy_key
      - chmod 600 /root/.ssh/deploy_key
      - rsync -avz --delete docs/generated/ user@docs.example.com:/var/www/html/
```

### CircleCI (YML)

```yaml
version: 2.1

jobs:
  generate-docs:
    docker:
      - image: cimg/python:3.11
    
    environment:
      - ANODYSE_INPUT_DIR: playbooks
      - ANODYSE_OUTPUT_DIR: docs/generated
      - ANODYSE_TEMPLATE_DIR: templates/custom
    
    steps:
      - checkout
      - run:
          name: Setup Python environment
          command: |
            python -m venv venv
            . venv/bin/activate
            pip install anodyse
      
      - run:
          name: Generate documentation
          command: |
            . venv/bin/activate
            mkdir -p $ANODYSE_OUTPUT_DIR
            python -m anodyse render \
              --input $ANODYSE_INPUT_DIR \
              --output $ANODYSE_OUTPUT_DIR \
              --recursive \
              --index \
              --fail-on-error
      
      - store_artifacts:
          path: docs/generated
          destination: generated-docs

workflows:
  generate:
    jobs:
      - generate-docs:
          filters:
            branches:
              only: main
```

### TravisCI (.travis.yml)

```yaml
language: python
python:
  - "3.11"

env:
  - ANODYSE_INPUT_DIR=playbooks
  - ANODYSE_OUTPUT_DIR=docs/generated
  - ANODYSE_TEMPLATE_DIR=templates/custom

install:
  - pip install anodyse

script:
  - mkdir -p $ANODYSE_OUTPUT_DIR
  - python -m anodyse render 
      --input $ANODYSE_INPUT_DIR 
      --output $ANODYSE_OUTPUT_DIR 
      --recursive 
      --index 
      --fail-on-error

before_deploy:
  - tar -czf docs.tar.gz $ANODYSE_OUTPUT_DIR

deploy:
  provider: releases
  api_key:
    secure: $GITHUB_TOKEN
  file: docs.tar.gz
  skip_cleanup: true
  on:
    branch: main
    tags: true
```

## Error Handling Patterns

**Fail-fast pattern (stop on any error)**:
```bash
#!/bin/bash
set -e  # Exit immediately on error

python -m anodyse render --input playbooks --output docs --fail-on-error
```

**Graceful degradation (continue despite warnings)**:
```bash
#!/bin/bash
python -m anodyse render --input playbooks --output docs
ANODYSE_EXIT=$?

if [ $ANODYSE_EXIT -eq 0 ]; then
    echo "✓ Documentation generated successfully"
    exit 0
elif [ $ANODYSE_EXIT -eq 2 ]; then
    echo "⚠ Documentation generated with warnings"
    exit 0  # Don't fail
else
    echo "✗ Critical error generating documentation"
    exit 1  # Fail
fi
```

**With error reporting**:
```bash
#!/bin/bash
set -e

OUTPUT_FILE="$ANODYSE_OUTPUT_DIR/index.md"

python -m anodyse render --input playbooks --output docs --fail-on-error

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "ERROR: Expected output file not found: $OUTPUT_FILE" >&2
    exit 1
fi

echo "✓ Docs generated at $OUTPUT_FILE"
```

## Publication Patterns

**Publish to GitHub Pages (via git push)**:
```bash
#!/bin/bash
set -e

cd docs/generated
git init
git config user.email "ci@example.com"
git config user.name "CI Bot"
git add .
git commit -m "Update docs from CI build $CI_BUILD_ID"
git push -f https://token@github.com/org/repo.git master:gh-pages
```

**Publish to static web server (rsync)**:
```bash
#!/bin/bash
set -e

rsync -avz --delete \
    --rsh="ssh -i /tmp/deploy_key" \
    docs/generated/ \
    deploy@docs.example.com:/var/www/docs/
```

**Publish to S3 (AWS CLI)**:
```bash
#!/bin/bash
set -e

aws s3 sync docs/generated/ s3://docs-bucket/ansible/ \
    --delete \
    --region us-east-1
```

## Troubleshooting Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Anodyse not found | "command not found: anodyse" | Install via pip: `pip install anodyse` |
| Missing input files | "Input directory not found" | Check path, use absolute paths, verify checkout step runs |
| Template not found | "Template directory not found" | Ensure template dir exists before running |
| Permission denied | Cannot write to output | Create output dir first: `mkdir -p $ANODYSE_OUTPUT_DIR` |
| Timeout | Job exceeds CI timeout | Increase timeout, optimize playbooks, use parallel flag |
| Import error | "ImportError: anodyse" | Activate venv, check Python version (3.11+) |

---

**Status**: Generic CI/CD Contract COMPLETE ✅
