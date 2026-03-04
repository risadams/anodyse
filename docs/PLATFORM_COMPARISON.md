# GitHub Actions vs. GitLab CI/CD: Platform Comparison

Side-by-side comparison of GitHub Actions and GitLab CI/CD for Anodyse documentation generation.

**Quick Decision**:
- **GitHub Actions** - Best for GitHub-hosted projects, open-source, simplicity
- **GitLab CI/CD** - Best for GitLab projects, self-hosted, runner flexibility

---

## Feature Comparison Matrix

| Feature | GitHub Actions | GitLab CI/CD | Winner | Notes |
|---------|----------------|-------------|--------|-------|
| **Setup Complexity** | ⭐ Very Simple | ⭐ Simple | GitHub | YAML in `.github/workflows/` vs. `.gitlab-ci.yml` |
| **Learning Curve** | ⭐ Shallow | ⭐⭐ Moderate | GitHub | GitHub has more examples and larger community |
| **Free Tier Minutes** | 2,000/month (public) | 400/month | GitHub | GitHub: unlimited for public repos |
| **Self-Hosted Runners** | Supported | Native (Shell, Docker, Kubernetes) | GitLab | GitLab runner is simpler for self-hosted |
| **Docker Support** | Via actions | Native in job config | GitLab | GitLab simpler: add `image:` directly |
| **Documentation** | Extensive | Very comprehensive | Tie | Both excellent |
| **Community Size** | Large (GitHub ecosystem) | Smaller but active | GitHub | More examples available |
| **Cost for Private** | $0-21/month typical | $0-120/month typical | GitHub | GitHub simpler pricing model |
| **Enterprise Features** | Via GitHub Enterprise | Native to GitLab | GitLab | GitLab better for enterprise deployment |

---

## GitHub Actions Strengths

### ✅ Reasons to Use GitHub Actions

| Strength | Benefit | Example |
|----------|---------|---------|
| **Native to GitHub** | No additional system to manage | Integrated with Issues, PRs, Discussions |
| **Best for Open Source** | Unlimited free minutes on public repos | Perfect for free tier development |
| **Large Marketplace** | 10,000+ pre-built actions | Reduce workflow configuration |
| **Branch Deployments** | Native GitHub Pages integration | One command for publishing |
| **Community** | Largest CI/CD user base | Easiest to find examples and help |
| **Simple Matrix** | Easy multi-version testing | Python 3.9/3.10/3.11 easily parallel |

### GitHub Actions Example

```yaml
name: Generate Docs
on: [push, pull_request, schedule: ['0 0 * * 0']]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: {python-version: '3.11'}
      - run: pip install anodyse
      - run: python -m anodyse --input-path ./playbooks --output-path ./docs
      - uses: actions/upload-artifact@v3
        with: {name: docs, path: ./docs, retention-days: 30}
```

---

## GitLab CI/CD Strengths

### ✅ Reasons to Use GitLab CI/CD

| Strength | Benefit | Example |
|----------|---------|---------|
| **Flexible Runners** | Use Docker, Shell, or Kubernetes | Run anywhere with different executor types |
| **Self-Hosted** | Full control over build infrastructure | On-premise or air-gapped deployments |
| **Native Docker** | Simpler container management | No additional setup for Docker jobs |
| **Rules System** | More powerful conditional logic | Complex branch/tag/manual trigger patterns |
| **Pages Native** | Built-in Pages for every project | Automatic HTTPS with custom domain |
| **Variable Scoping** | Multiple variable scope levels | Project, Group, Instance-level variables |
| **Enterprise Ready** | Better multi-team support | Group-level runners, shared templates |

### GitLab CI/CD Example

```yaml
stages: [generate]

variables:
  ANODYSE_INPUT_DIR: ./playbooks
  ANODYSE_OUTPUT_DIR: ./docs

generate_docs:
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anopyse \
        --input-path $ANODYSE_INPUT_DIR \
        --output-path $ANODYSE_OUTPUT_DIR
  artifacts:
    paths: [docs/]
    expire_in: 30 days
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
```

---

## Detailed Comparison by Aspect

### 1. Configuration

**GitHub Actions**

```yaml
# File: .github/workflows/generate.yml
name: Generate Documentation

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * 0'

jobs:
  generate:
    runs-on: ubuntu-latest
```

**GitLab CI/CD**

```yaml
# File: .gitlab-ci.yml
stages: [generate]

generate_docs:
  image: python:3.11-slim
  script: ...
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
```

**Winner**: 🔗 **Tie** - Both clear, different syntax preferences

---

### 2. Python/Docker Setup

**GitHub Actions**

```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'
```

**GitLab CI/CD**

```yaml
image: python:3.11-slim
cache:
  paths: [.cache/pip]
```

**Winner**: 🎯 **GitLab** - One line vs. three, native Docker, automatic caching

---

### 3. Artifact Management

**GitHub Actions**

```yaml
- uses: actions/upload-artifact@v3
  with:
    name: docs-${{ github.run_number }}
    path: ./docs
    retention-days: 30
```

**GitLab CI/CD**

```yaml
artifacts:
  paths: [docs/]
  expire_in: 30 days
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      expire_in: 90 days
```

**Winner**: 🎯 **GitLab** - Branch-specific retention, simpler syntax

---

### 4. Conditional Execution

**GitHub Actions**

```yaml
- if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  run: echo "Deploy to production"

strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```

**GitLab CI/CD**

```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == "main" && $CI_COMMIT_TAG'
    when: always
  - when: never

parallel:
  matrix:
    - PYTHON_VERSION: ['3.9', '3.10', '3.11']
```

**Winner**: 🎯 **GitLab** - More powerful rules, easier multi-variant logic

---

### 5. Secret Management

**GitHub Actions**

```yaml
- run: python deploy.py
  env:
    API_TOKEN: ${{ secrets.API_TOKEN }}  # GitHub repo secrets
```

**GitLab CI/CD**

```yaml
script:
  - python deploy.py
  
variables:
  API_TOKEN: $CI_VARIABLE  # Project/Group/Instance variables
```

**Winner**: 🔗 **Tie** - Both secure, GitLab more flexible scoping

---

### 6. Publishing to Pages

**GitHub Actions**

```yaml
- uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
```

**GitLab CI/CD**

```yaml
pages:
  artifacts:
    paths: [public/]
  environment:
    url: https://$CI_PROJECT_NAMESPACE.gitlab.io/$CI_PROJECT_NAME/
```

**Winner**: 🎯 **GitLab** - Native, automatic HTTPS, simpler setup

---

### 7. Self-Hosted Runners

**GitHub Actions**

```bash
# Download and run GitHub runner on your machine
./run.sh
```

**GitLab CI/CD**

```bash
# Install GitLab runner
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt-get install gitlab-runner

# Register with shell executor
sudo gitlab-runner register \
  --url https://gitlab.example.com/ \
  --executor shell
```

**Winner**: 🎯 **GitLab** - Simpler setup, more executor options (Docker, Shell, Kubernetes)

---

### 8. Cost Analysis

| Scenario | GitHub Actions | GitLab CI/CD |
|----------|----------------|-------------|
| **Open Source** | Free (unlimited) | Free (400 min/month) |
| **1 private repo, 1 pipeline/week** | Free | Free |
| **5 private repos, 4 pipelines/week** | ~$10-15/month | Free (under quota) |
| **Heavy usage (1000 min/month)** | ~$50-100/month | ~$0-40/month (free tier might suffice) |
| **Large team (10+ developers)** | GitHub Enterprise $20/user/month | GitLab.com Premium $19/user/month |
| **Self-hosted infrastructure** | Free (GitHub Actions) | Free (GitLab Community) |

---

## Decision Tree: Which Platform?

```
Are you using GitHub? 
├─ YES
│  ├─ Public/open-source project?
│  │  └─ YES → GitHub Actions ✅ (free unlimited)
│  └─ Private project with moderate usage?
│     └─ GitHub Actions (simple, good enough)
│
└─ Using GitLab?
   ├─ YES
   │  ├─ Need self-hosted/on-premise?
   │  │  └─ YES → GitLab CI/CD ✅ (best for self-hosted)
   │  ├─ Enterprise team?
   │  │  └─ YES → GitLab CI/CD ✅ (group-level features)
   │  └─ Otherwise → GitLab CI/CD ✅ (integrated experience)
```

---

## Migration Guide

### GitHub Actions → GitLab CI/CD

**Step 1**: Create `.gitlab-ci.yml`
```bash
cp .github/workflows/generate-docs.yml .gitlab-ci.yml
# Clean up to match GitLab syntax
```

**Step 2**: Convert trigger syntax

| GitHub Actions | GitLab CI/CD |
|---|---|
| `on: [push, pull_request]` | `rules: [{if: '$CI_COMMIT_BRANCH == "main"'}, {if: '$CI_PIPELINE_SOURCE == "merge_request_event"'}]` |
| `runs-on: ubuntu-latest` | (omit, use Ubuntu by default or specify `image:`) |
| `code uses: actions/checkout@v4` | (automated, removed) |
| `uses: actions/setup-python@v4` | `image: python:3.11-slim` |

**Step 3**: Test and commit
```bash
git add .gitlab-ci.yml
git commit -m "Add GitLab CI/CD pipeline"
git push
```

### GitLab CI/CD → GitHub Actions

**Step 1**: Create `.github/workflows/generate.yml`

**Step 2**: Convert job to workflow
```yaml
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: {python-version: '3.11'}
      # ... convert scripts to steps
```

**Step 3**: Publish workflow and test

---

## Recommendations for Anodyse Users

### Use GitHub Actions if:
- ✅ Project is on GitHub
- ✅ Open-source (leveraging free unlimited minutes)
- ✅ You prefer large community and many examples
- ✅ Simple, straightforward workflow needed
- ✅ GitHub Pages for documentation hosting

### Use GitLab CI/CD if:
- ✅ Project is on GitLab.com or self-hosted GitLab
- ✅ Need self-hosted runner support
- ✅ Complex conditional logic or multiple variants
- ✅ Prefer GitLab Pages for integrated hosting
- ✅ Enterprise team with multi-repo management
- ✅ Air-gapped or on-premise deployment required

### Use Generic CI Patterns if:
- ✅ Using Jenkins, CircleCI, Travis, Woodpecker, or other CI
- ✅ Portable shell script that works everywhere
- ✅ Already have CI infrastructure chosen
- ✅ Mixed environments

---

## See Also

- [CI Integration Guide](./CI_INTEGRATION.md) - Setup for both platforms
- [GitHub Actions Reference](./github-actions-reference.md) - Detailed GitHub documentation
- [GitLab CI Reference](./gitlab-ci-reference.md) - Detailed GitLab documentation
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Solutions by platform
- [Example Workflows](./examples/) - Copy-paste ready configurations

---

**Last Updated**: March 2026
**Anodyse Version**: 1.0+
