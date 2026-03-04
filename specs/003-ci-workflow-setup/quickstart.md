# Quickstart Guide: Using Anodyse in CI/CD

Get started generating Ansible documentation in your CI/CD pipeline in under 20 minutes. Choose your platform below.

## Quick Links

- **[GitHub Actions](#github-actions-5-minute-setup)** - Most common, best supported
- **[GitLab CI/CD](#gitlab-cicd-5-minute-setup)** - GitLab.com and self-hosted
- **[Generic CI/CD](#generic-ci-shell-pattern)** - Any other CI system
- **[Full Documentation](../docs)** - Complete guides with advanced options
- **[Troubleshooting](#troubleshooting)** - Common issues and solutions

---

## GitHub Actions: 5-Minute Setup

### Step 1: Create Workflow File

Create `.github/workflows/generate-docs.yml`:

```yaml
name: Generate Ansible Documentation

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * MON'
  workflow_dispatch:

env:
  ANODYSE_INPUT_DIR: ./playbooks
  ANODYSE_OUTPUT_DIR: ./docs

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Anodyse
        run: pip install anodyse
      
      - name: Generate Docs
        run: |
          mkdir -p ${{ env.ANODYSE_OUTPUT_DIR }}
          python -m anodyse render \
            --input ${{ env.ANODYSE_INPUT_DIR }} \
            --output ${{ env.ANODYSE_OUTPUT_DIR }} \
            --recursive --index --fail-on-error
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: generated-docs
          path: ${{ env.ANODYSE_OUTPUT_DIR }}
```

### Step 2: Customize Paths

Edit the `env` section:
- `ANODYSE_INPUT_DIR`: Where your playbooks/roles are (default: `./playbooks`)
- `ANODYSE_OUTPUT_DIR`: Where docs should go (default: `./docs`)

### Step 3: Commit and Test

```bash
git add .github/workflows/generate-docs.yml
git commit -m "Add Anodyse docs generation workflow"
git push
```

Go to your repo → **Actions** tab → Click the workflow run to see it execute.

### Step 4 (Optional): Publish to GitHub Pages

Add to the workflow file after `Upload Artifacts` step:

```yaml
      - name: Deploy to Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: actions/deploy-pages@v2
```

Then enable Pages in repo settings: **Settings** → **Pages** → **Source: GitHub Actions**

---

## GitLab CI/CD: 5-Minute Setup

### Step 1: Create CI Configuration

Create `.gitlab-ci.yml`:

```yaml
stages:
  - generate

generate-docs:
  stage: generate
  image: python:3.11-slim
  variables:
    ANODYSE_INPUT_DIR: playbooks
    ANODYSE_OUTPUT_DIR: docs/generated
  script:
    - pip install anodyse
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
    expire_in: 30 days
  only:
    - push
    - merge_request
    - schedules
```

### Step 2: Customize Paths

Edit the `variables` section:
- `ANODYSE_INPUT_DIR`: Where your playbooks/roles are
- `ANODYSE_OUTPUT_DIR`: Where docs should go

### Step 3: Commit and Test

```bash
git add .gitlab-ci.yml
git commit -m "Add Anodyse docs generation pipeline"
git push
```

Go to your project → **CI/CD** → **Pipelines** → Check the execution.

### Step 4 (Optional): Publish to GitLab Pages

Add to `.gitlab-ci.yml`:

```yaml
pages:
  stage: generate
  script:
    - pip install anodyse
    - mkdir -p public
    - python -m anodyse render --input playbooks --output public --recursive --index
  artifacts:
    paths:
      - public
  only:
    - main
```

Then enable Pages in project settings: **Settings** → **Pages** → **Public** ✓

---

## Generic CI: Shell Pattern

For Jenkins, CircleCI, Woodpecker, Travis CI, or custom CI systems.

### Create a Build Script

Create `scripts/generate-docs.sh`:

```bash
#!/bin/bash
set -e

# Configuration
ANODYSE_INPUT_DIR="${ANODYSE_INPUT_DIR:-.}"
ANODYSE_OUTPUT_DIR="${ANODYSE_OUTPUT_DIR:-./docs}"

# Setup
python3 -m venv venv
source venv/bin/activate
pip install anodyse

# Generate
mkdir -p "$ANODYSE_OUTPUT_DIR"
python -m anodyse render \
  --input "$ANODYSE_INPUT_DIR" \
  --output "$ANODYSE_OUTPUT_DIR" \
  --recursive \
  --index \
  --fail-on-error

echo "✓ Docs generated in $ANODYSE_OUTPUT_DIR"
```

### Invoke from Your CI

**Jenkins (Declarative)**:
```groovy
stages {
    stage('Generate Docs') {
        steps {
            sh 'bash scripts/generate-docs.sh'
        }
    }
}
```

**CircleCI**:
```yaml
jobs:
  generate:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run: bash scripts/generate-docs.sh
```

**Woodpecker**:
```yaml
pipeline:
  docs:
    image: python:3.11
    commands:
      - bash scripts/generate-docs.sh
```

---

## Verify It Works

After running the workflow:

### GitHub Actions
- ✅ Workflow runs on **Actions** tab
- ✅ Artifacts downloadable from run details
- ✅ (Optional) Published to GitHub Pages URL

### GitLab CI/CD
- ✅ Pipeline runs on **CI/CD → Pipelines** page
- ✅ Artifacts viewable in job details
- ✅ (Optional) Published to `https://<namespace>.<host>/<project>`

### Generic CI
- ✅ Build log shows "✓ Docs generated"
- ✅ `docs/` directory contains generated `.md` files
- ✅ No errors in build logs

---

## Common Customizations

### Change Input/Output Paths

**GitHub Actions**:
```yaml
env:
  ANODYSE_INPUT_DIR: ./contrib/ansible/roles
  ANODYSE_OUTPUT_DIR: ./website/docs/playbooks
```

**GitLab**:
```yaml
variables:
  ANODYSE_INPUT_DIR: ./contrib/roles
  ANODYSE_OUTPUT_DIR: ./site/docs
```

### Use Custom Templates

**GitHub Actions**:
```bash
python -m anodyse render \
  --input ./playbooks \
  --output ./docs \
  --template ./templates/custom
```

**GitLab**:
```yaml
script:
  - python -m anodyse render 
      --input playbooks 
      --output docs 
      --template templates/custom
```

### Run on Specific Branches

**GitHub Actions**:
```yaml
on:
  push:
    branches: [main, develop]
```

**GitLab**:
```yaml
only:
  - main
  - develop
```

### Schedule Daily Regeneration

**GitHub Actions**:
```yaml
schedule:
  - cron: '0 3 * * *'  # Daily 3 AM UTC
```

**GitLab**:
```yaml
# Via project: CI/CD → Schedules
# Or in .gitlab-ci.yml:
only:
  - schedules
```

---

## Troubleshooting

### "Anonyse not found"

**Cause**: Anodyse not installed  
**Fix**: Ensure `pip install anodyse` runs before anodyse command

### "Input directory not found"

**Cause**: Wrong path or checkout didn't work  
**Fix**:
- Check path is correct relative to repo root
- Ensure `checkout` step runs first (GitHub: `uses: actions/checkout@v4`)
- Verify playbooks exist: `ls -la path/to/playbooks`

### "Permission denied: ./docs"

**Cause**: Output directory not writable  
**Fix**: Create directory first with `mkdir -p ./docs`

### "Script returned non-zero exit code"

**Cause**: Anodyse found errors in playbooks  
**Fix**:
- Check build logs for error details
- Verify YAML syntax in playbooks and roles
- Look for missing role metadata annotations
- Run locally: `python -m anodyse render --input ./playbooks --output ./docs`

### "Timeout exceeded"

**Cause**: Large playbook sets take too long  
**Fix**:
- Increase job timeout (GitLab: `timeout: 30 minutes`)
- Use `--parallel` flag in Anodyse
- Split large playbook directories

### Docs not published to Pages

**Cause**: Publication step skipped or failed  
**Fix**:
- Check if running on main branch: GitHub Actions needs `if: github.ref == 'refs/heads/main'`
- Enable Pages in project settings
- Remove `-` from branch rules or use explicit conditions

---

## Next Steps

✓ **Quick setup complete!** Your CI pipeline now generates documentation.

📖 **Ready for more?**
- [Full GitHub Actions Guide](../docs/CI_INTEGRATION.md#github-actions-guide)
- [Full GitLab Guide](../docs/CI_INTEGRATION.md#gitlab-ci-guide)
- [Publishing Guide](../docs/PUBLISHING.md) - Publish docs to the web
- [Advanced Options](../docs/CI_INTEGRATION.md) - Custom templates, error handling, etc.

❓ **Questions?**
- [Troubleshooting](../docs/TROUBLESHOOTING.md)
- [Full Contracts](./CONTRACTS.md) - Technical specifications
- [Issue Tracker](https://github.com/anodyse/anodyse/issues)

---

**Last Updated**: March 4, 2026  
**Status**: ✅ Quickstart Ready
