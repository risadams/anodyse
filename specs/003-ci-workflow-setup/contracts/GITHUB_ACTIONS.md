# GitHub Actions Workflow Contract

**Purpose**: Reference implementation for invoking Anodyse via GitHub Actions  
**Status**: Example/Template  
**Triggers**: Push, Pull Request, Manual, Schedule

## Schema

```yaml
name: Generate Ansible Documentation
on:
  push:
    branches: [main]
    paths: ['playbooks/**', 'roles/**']
  pull_request:
    branches: [main]
    paths: ['playbooks/**', 'roles/**']
  schedule:
    - cron: '0 2 * * MON'  # Weekly Monday 2 AM UTC
  workflow_dispatch:

env:
  ANODYSE_INPUT_DIR: ./playbooks
  ANODYSE_OUTPUT_DIR: ./docs/generated
  ANODYSE_TEMPLATE_DIR: ./templates/custom
  PUBLISH_DOCS: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
          
      - name: Install Anodyse
        run: pip install anodyse
        
      - name: Create output directory
        run: mkdir -p ${{ env.ANODYSE_OUTPUT_DIR }}
        
      - name: Generate documentation
        run: |
          python -m anodyse render \
            --input ${{ env.ANODYSE_INPUT_DIR }} \
            --output ${{ env.ANODYSE_OUTPUT_DIR }} \
            --template ${{ env.ANODYSE_TEMPLATE_DIR }} \
            --recursive \
            --index \
            --fail-on-error
        
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: generated-docs
          path: ${{ env.ANODYSE_OUTPUT_DIR }}
          retention-days: 30
          
      - name: Deploy to GitHub Pages
        if: env.PUBLISH_DOCS == 'true' && github.event_name == 'push'
        uses: actions/configure-pages@v3
        
      - name: Upload pages artifact
        if: env.PUBLISH_DOCS == 'true' && github.event_name == 'push'
        uses: actions/upload-pages-artifact@v2
        with:
          path: ${{ env.ANODYSE_OUTPUT_DIR }}
          
      - name: Deploy pages
        if: env.PUBLISH_DOCS == 'true' && github.event_name == 'push'
        id: deployment
        uses: actions/deploy-pages@v2
```

## Input Contract

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `python-version` | string | No | 3.11 | Python version to use |
| `anodyse-version` | string | No | latest | Anodyse package version (or 'latest') |
| `input-dir` | string | Yes | ./playbooks | Input directory path |
| `output-dir` | string | Yes | ./docs/generated | Output directory path |
| `template-dir` | string | No | null | Custom template directory (optional) |
| `fail-on-error` | boolean | No | true | Fail job on critical errors |
| `publish-docs` | boolean | No | false | Publish to GitHub Pages |
| `publish-branch` | string | No | main | Only publish when pushing to this branch |

## Output Contract

| Artifact | Location | Purpose | Retention |
|----------|----------|---------|-----------|
| generated-docs | ./docs/generated/* | Markdown documentation | 30 days (CI) |
| pages-deployment | GitHub Pages | Published documentation | Permanent (user-configurable) |

## Error Handling Contract

| Error Scenario | Anodyse Exit Code | Job Status | Action |
|---------------|-------------------|-----------|--------|
| Unparseable YAML | 1 | ❌ FAIL | Halt execution, report error |
| Missing input dir | 1 | ❌ FAIL | Halt execution, report error |
| Template error | 1 | ❌ FAIL | Halt execution, report error |
| Undocumented items | 2 | ✅ PASS | Generate docs with warnings |
| Success | 0 | ✅ PASS | Preserve artifacts, optionally publish |

## Variables Reference

```yaml
# GitHub Actions context variables
github.event_name         # Type of event: 'push', 'pull_request', 'schedule', 'workflow_dispatch'
github.ref               # Full ref: 'refs/heads/main'
github.event_name == 'push' && github.ref == 'refs/heads/main'  # Condition for main push
secrets.*               # Access to repository secrets (for credentials)

# Environment variables set by workflow
ANODYSE_INPUT_DIR       # Input playbooks/roles directory
ANODYSE_OUTPUT_DIR      # Output documentation directory
ANODYSE_TEMPLATE_DIR    # Custom template directory
PUBLISH_DOCS            # Whether to publish (conditional)
```

## Customization Points

### Trigger Configuration

**Push on multiple branches**:
```yaml
on:
  push:
    branches: [main, develop, feature/*]
```

**Run on pull request but not main**:
```yaml
on:
  pull_request:
    types: [opened, synchronize]
    branches-ignore: [main]
```

**Daily schedule**:
```yaml
schedule:
  - cron: '0 2 * * *'  # Daily 2 AM UTC
```

### Template Customization

**Use built-in templates only**:
```bash
python -m anodyse render \
  --input ./playbooks \
  --output ./docs
  # No --template flag
```

**Use custom templates from repository**:
```bash
python -m anodyse render \
  --input ./playbooks \
  --output ./docs \
  --template ./templates/custom
```

**Use templates from external repository**:
```yaml
- name: Checkout template repository
  uses: actions/checkout@v4
  with:
    repository: org/anodyse-templates
    path: templates/external
    
- name: Generate documentation
  run: |
    python -m anodyse render \
      --input ./playbooks \
      --output ./docs \
      --template ./templates/external
```

### Publication Configuration

**Publish to GitHub Pages on all pushes**:
```yaml
env:
  PUBLISH_DOCS: ${{ github.event_name == 'push' }}
```

**Publish only for releases**:
```yaml
env:
  PUBLISH_DOCS: ${{ github.event_name == 'release' }}
```

**Manual site staging with artifact download**:
```yaml
- name: Download documentation
  uses: actions/download-artifact@v3
  with:
    name: generated-docs
    path: ./staged-docs
```

---

**Status**: GitHub Actions Contract COMPLETE ✅
