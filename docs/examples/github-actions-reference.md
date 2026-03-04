# GitHub Actions Reference: CI Integration for Anodyse

Complete schema and customization reference for integrating Anodyse with GitHub Actions workflows.

**Table of Contents**
- [Workflow Schema](#workflow-schema)
- [Triggers](#triggers)
- [Steps & Actions](#steps--actions)
- [Environment Variables](#environment-variables)
- [Conditional Execution](#conditional-execution-if-conditions)
- [Artifacts](#artifacts)
- [Secrets & Credentials](#secrets--credentials)
- [Matrix Strategies](#matrix-strategies)
- [Outputs & Context](#outputs--context)
- [Examples](#examples)

---

## Workflow Schema

### Basic Structure

```yaml
name: <string>                    # Workflow name (shown in Actions tab)

on: <trigger>                     # When to trigger (push, PR, schedule, manual)

env:                              # Workflow-level environment variables
  <KEY>: <value>

concurrency:                      # Limit concurrent runs
  group: <group-name>
  cancel-in-progress: true

jobs:
  <job-id>:                       # Unique job identifier
    runs-on: <runner>             # Runner type
    timeout-minutes: <number>     # Job timeout (default: 360)
    
    environment:                  # Environment for deployment
      name: <env-name>
      url: <deployment-url>
    
    permissions:                  # Token permissions
      contents: read
      pages: write
    
    env:                          # Job-level environment variables
      <KEY>: <value>
    
    steps:
      - name: <string>            # Step name/description
        uses: <action>            # Reference to GitHub Action
        with:
          <input>: <value>
        env:                      # Step-level environment variables
          <KEY>: <value>
```

---

## Triggers

### Push Trigger

```yaml
on:
  push:
    branches: [main, develop]           # On push to specific branches
    paths: ['playbooks/**', 'roles/**']  # Only if specific files changed
    tags: ['v*']                        # On version tags
```

### Pull Request Trigger

```yaml
on:
  pull_request:
    branches: [main]                    # On PR to specific branches
    types: [opened, synchronize]        # On PR open/update/etc
    paths: ['playbooks/**']              # Only if specific files changed
```

### Schedule Trigger

```yaml
on:
  schedule:
    - cron: '0 2 * * MON'  # At 02:00 on Monday UTC
    - cron: '30 9 * * 1-5' # At 09:30 on weekdays UTC
```

### Manual Trigger

```yaml
on:
  workflow_dispatch:          # Manual button click in Actions tab
    inputs:
      environment:            # Optional input parameters
        description: 'Target environment'
        required: true
        default: 'staging'
```

### Combined Triggers

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * MON'
  workflow_dispatch:
```

---

## Steps & Actions

### Standard Steps

#### Checkout Code

```yaml
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0        # Full history
          submodules: 'true'    # Include submodules
          ref: ${{ github.ref }}
```

#### Setup Python

```yaml
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'          # Cache pip dependencies
          cache-dependency-path: 'requirements.txt'
```

#### Run Commands

```yaml
      - name: Install Anodyse
        run: |
          pip install --upgrade pip
          pip install anodyse
      
      - name: Generate Documentation
        run: python -m anodyse --input-path ./playbooks --output-path ./docs
```

#### Upload Artifacts

```yaml
      - name: Upload Generated Docs
        uses: actions/upload-artifact@v3
        with:
          name: ansible-docs-${{ github.run_number }}
          path: ./docs
          retention-days: 30
          if-no-files-found: error  # Fail if no files
```

#### Deploy to GitHub Pages

```yaml
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
          cname: docs.example.com    # Custom domain
```

---

## Environment Variables

### Workflow-Level Variables

```yaml
env:                              # Available to all jobs
  ANODYSE_INPUT_DIR: ./playbooks
  ANODYSE_OUTPUT_DIR: ./docs
  ANODYSE_VERBOSE: 'true'
  ENVIRONMENT: production
```

### Job-Level Variables

```yaml
jobs:
  generate-docs:
    env:                          # Available only to this job
      ANODYSE_INPUT_DIR: ./playbooks
```

### Step-Level Variables

```yaml
      - name: Generate
        env:                      # Available only to this step
          DEBUG_MODE: 'true'
        run: python -m anodyse ...
```

### GitHub Context Variables

```yaml
${{ github.ref }}                 # Current branch/tag ref
${{ github.ref_name }}            # Branch or tag name
${{ github.event_name }}          # Trigger event type
${{ github.run_number }}          # Workflow run number
${{ github.run_id }}              # Workflow run ID
${{ github.sha }}                 # Commit SHA
${{ github.actor }}               # Username who triggered
${{ github.repository }}          # owner/repo
```

### Job Context Variables

```yaml
${{ job.status }}                 # Current job status
${{ job.outputs.<name> }}         # Output from job
${{ steps.<step-id>.outputs.<name> }}  # Output from step
```

---

## Conditional Execution (if Conditions)

### Branch-Based

```yaml
      - name: Generate for Main Only
        if: github.ref == 'refs/heads/main'
        run: python -m anodyse ...
      
      - name: Publish on Release Tag
        if: startsWith(github.ref, 'refs/tags/v')
        run: echo "Publishing release docs"
```

### Event-Based

```yaml
      - name: Generate on Push
        if: github.event_name == 'push'
        run: python -m anodyse ...
      
      - name: Generate on PR
        if: github.event_name == 'pull_request'
        run: python -m anodyse ...
      
      - name: Generate on Schedule
        if: github.event_name == 'schedule'
        run: python -m anodyse ...
```

### Job Status

```yaml
      - name: Cleanup on Failure
        if: failure()
        run: rm -rf ./docs
      
      - name: Notify on Success
        if: success()
        run: echo "Documentation generated successfully"
      
      - name: Always Run
        if: always()
        run: echo "Workflow completed"
```

### Skip Draft PRs

```yaml
      - name: Generate (skip draft PRs)
        if: '!github.event.pull_request.draft'
        run: python -m anodyse ...
```

### Skip Dependabot

```yaml
      - name: Generate (skip Dependabot)
        if: github.actor != 'dependabot[bot]'
        run: python -m anodyse ...
```

---

## Artifacts

### Upload Artifacts

```yaml
      - name: Upload Docs
        uses: actions/upload-artifact@v3
        with:
          name: docs-${{ github.run_number }}
          path: ./docs
          retention-days: 30
          if-no-files-found: error
          compression-level: 6
```

### Download Artifacts

```yaml
      - name: Download Previous Docs
        uses: actions/download-artifact@v3
        with:
          name: docs-latest
          path: ./docs
```

### Retention Policies

```yaml
# Keep for 1 day
retention-days: 1

# Keep for 30 days (default)
retention-days: 30

# Keep for 90 days
retention-days: 90
```

---

## Secrets & Credentials

### Using Secrets

```yaml
      - name: Deploy with Credentials
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          aws s3 sync ./docs s3://my-bucket/docs
```

### Creating Secrets

1. Go to repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Enter Name and Value
4. Use in workflow: `${{ secrets.SECRET_NAME }}`

### Personal Access Token

For accessing private repositories:

```yaml
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          repository: other-owner/other-repo
```

### GITHUB_TOKEN Permissions

```yaml
permissions:
  contents: read                   # Read repository content
  pages: write                     # Write to GitHub Pages
  id-token: write                  # Write ID token (for deployment)
  pull-requests: write             # Write comments on PRs
```

---

## Matrix Strategies

### Multiple Python Versions

```yaml
jobs:
  generate-docs:
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Generate for Python ${{ matrix.python-version }}
        run: |
          pip install anodyse
          python -m anodyse --input-path ./playbooks \
            --output-path ./docs/py${{ matrix.python-version }}
```

### Multiple Operating Systems

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.10', '3.11']
runs-on: ${{ matrix.os }}
```

### Fail Fast vs. Continue

```yaml
strategy:
  fail-fast: false  # Continue other matrix jobs on failure
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```

---

## Outputs & Context

### Define Job Outputs

```yaml
jobs:
  generate:
    outputs:
      docs-path: ${{ steps.generate.outputs.path }}
      docs-count: ${{ steps.generate.outputs.file-count }}
    steps:
      - id: generate
        run: |
          echo "path=./docs" >> $GITHUB_OUTPUT
          echo "file-count=42" >> $GITHUB_OUTPUT
```

### Use Outputs in Other Jobs

```yaml
jobs:
  generate:
    outputs:
      docs-path: ${{ steps.generate.outputs.path }}
    steps:
      - id: generate
        run: echo "path=./docs" >> $GITHUB_OUTPUT
  
  publish:
    needs: generate
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: echo "Deploying from ${{ needs.generate.outputs.docs-path }}"
```

---

## Examples

### Minimal Example

```yaml
name: Generate Docs

on:
  push:
    branches: [main]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install anodyse
      - run: python -m anodyse --input-path ./playbooks --output-path ./docs
      - uses: actions/upload-artifact@v3
        with:
          path: ./docs
```

### Complete Example with GitHub Pages

```yaml
name: Generate & Publish Docs

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * MON'
  workflow_dispatch:

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
    
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
            --output-path ./public
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ansible-docs
          path: ./public
          retention-days: 30
      
      - name: Deploy to GitHub Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

---

## Best Practices

✅ **DO**:
- Use `actions/checkout@v4` (latest stable version)
- Cache dependencies: `cache: 'pip'`
- Use specific Python versions: `'3.11'` not `'3'`
- Set reasonable timeouts: `timeout-minutes: 30`
- Always upload artifacts with `if: always()` for debugging
- Use meaningful step names for clarity

❌ **DON'T**:
- Hardcode secrets in workflow files
- Use Docker `FROM` base images in GitHub Actions (use actions instead)
- Create circular job dependencies
- Test with unspecified Python versions
- Forget to add `contents: read` permission
- Use deprecated actions (v1, v2)

---

**Last Updated**: March 4, 2026  
**See Also**: [GitHub Actions Documentation](https://docs.github.com/en/actions)
