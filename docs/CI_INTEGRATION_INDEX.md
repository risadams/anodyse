# CI Integration Documentation Index

Complete index of all CI/CD integration documentation for Anodyse.

**Quick Links by Use Case**

| Need | Document | Time |
|------|----------|------|
| **Quick start** | [Quickstart Guide](../specs/003-ci-workflow-setup/quickstart.md) | 5 min |
| **GitHub Actions** | [GitHub Actions Reference](./examples/github-actions-reference.md) | 20 min |
| **GitLab CI/CD** | [GitLab CI Reference](./examples/gitlab-ci-reference.md) | 20 min |
| **Jenkins** | [Jenkins Integration Guide](./CI_INTEGRATION.md#generic-ci-patterns) | 30 min |
| **Publishing docs** | [Publishing Guide](./PUBLISHING.md) | 15 min |
| **Environment setup** | [Environment Variables](./ENVIRONMENT_VARIABLES.md) | 10 min |
| **Troubleshooting** | [Troubleshooting Guide](./TROUBLESHOOTING.md) | Variable |
| **Contributing** | [Contributing Examples](./CI_EXAMPLES_CONTRIBUTING.md) | 20 min |

---

## Documentation by Platform

### GitHub Actions (P1 - Recommended)

| Document | Purpose | Audience |
|----------|---------|----------|
| [CI_INTEGRATION.md#github-actions](./CI_INTEGRATION.md#github-actions-integration) | Setup guide with 3-step tutorial | End users |
| [github-actions-reference.md](./examples/github-actions-reference.md) | Complete schema and customization reference | Developers, DevOps |
| [github-actions-basic.yml](./examples/workflows/github-actions-basic.yml) | Minimal working example (copy-paste ready) | End users |
| [github-actions-with-github-pages.yml](./examples/workflows/github-actions-with-github-pages.yml) | Advanced setup with publishing | Power users |
| [github-actions-all-triggers.yml](./examples/workflows/github-actions-all-triggers.yml) | All trigger types demonstration | Reference |
| [github-actions-custom-templates.yml](./examples/workflows/github-actions-custom-templates.yml) | Template customization patterns | Advanced users |

**Get Started**: Copy [github-actions-basic.yml](./examples/workflows/github-actions-basic.yml) to `.github/workflows/generate-docs.yml` and customize paths.

---

### GitLab CI/CD (P2)

| Document | Purpose | Audience |
|----------|---------|----------|
| [CI_INTEGRATION.md#gitlab-cicd](./CI_INTEGRATION.md#gitlab-cicd-integration) | Setup guide with 3-step tutorial | End users |
| [gitlab-ci-reference.md](./examples/gitlab-ci-reference.md) | Complete schema and runner options | Developers, DevOps |
| [gitlab-ci-basic.yml](./examples/gitlab-ci-basic.yml) | Minimal working example (copy-paste ready) | End users |
| [gitlab-ci-with-gitlab-pages.yml](./examples/gitlab-ci-with-gitlab-pages.yml) | Advanced setup with Pages publishing | Power users |
| [gitlab-ci-shell-runner.yml](./examples/gitlab-ci-shell-runner.yml) | Self-hosted runner pattern | Enterprise users |

**Get Started**: Copy [gitlab-ci-basic.yml](./examples/gitlab-ci-basic.yml) to `.gitlab-ci.yml` and customize variables.

---

### Generic CI Systems (P3)

Patterns for Jenkins, Woodpecker, CircleCI, Travis CI, and others.

| Document | Purpose | Audience |
|----------|---------|----------|
| [CI_INTEGRATION.md#generic-ci](./CI_INTEGRATION.md#generic-ci-patterns) | Generic patterns and best practices | Developers |
| [scripts/generate-docs.sh](./examples/scripts/generate-docs.sh) | Portable shell script | All platforms |
| [jenkins/Jenkinsfile](./examples/jenkins/Jenkinsfile) | Jenkins Declarative Pipeline | Jenkins users |
| [woodpecker/.woodpecker.yml](./examples/woodpecker/.woodpecker.yml) | Woodpecker CI configuration | Woodpecker users |
| [circleci/config.yml](./examples/circleci/config.yml) | CircleCI configuration | CircleCI users |
| [travis/.travis.yml](./examples/travis/.travis.yml) | Travis CI configuration | Travis users |

**Get Started**: Review [CI_INTEGRATION.md#generic-ci-patterns](./CI_INTEGRATION.md#generic-ci-patterns) and adapt patterns to your CI system.

---

## Core Documentation

### Setup & Configuration

- **[CI_INTEGRATION.md](./CI_INTEGRATION.md)** (1,200+ lines)
  - Main integration hub
  - Overview and core concepts
  - 3-step setup for GitHub Actions, GitLab CI/CD
  - Generic CI pattern guide
  - Common patterns (branches, error handling, templates)

- **[ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md)** (400+ lines)
  - Complete reference for all variables
  - Anodyse CLI variables
  - CI platform variables (GitHub, GitLab, Jenkins, Woodpecker, CircleCI)
  - Usage patterns and best practices

### Publishing & Deployment

- **[PUBLISHING.md](./PUBLISHING.md)** (600+ lines)
  - Publishing platforms: GitHub Pages, GitLab Pages, Read the Docs, S3, Netlify
  - Setup instructions for each platform
  - Cost and maintenance comparison
  - Advanced patterns (versioning, multiple environments)

### Troubleshooting & Support

- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** (600+ lines)
  - General issues and solutions
  - Platform-specific troubleshooting (GitHub Actions, GitLab CI, Jenkins, etc.)
  - Publishing issues
  - FAQ sections per platform
  - Advanced debugging techniques

### Contributing & Community

- **[CI_EXAMPLES_CONTRIBUTING.md](./CI_EXAMPLES_CONTRIBUTING.md)** (250+ lines)
  - How to contribute new CI platform examples
  - Style guide and naming conventions
  - Testing requirements
  - Pull request process

---

## Example Workflows

### GitHub Actions Examples

```
docs/examples/workflows/
├── github-actions-basic.yml              # 3 triggers, artifact upload
├── github-actions-with-github-pages.yml  # Includes GitHub Pages deployment
├── github-actions-all-triggers.yml       # Complete trigger reference
└── github-actions-custom-templates.yml   # Custom template integration
```

### GitLab CI Examples

```
docs/examples/
├── gitlab-ci-basic.yml              # Docker runner, artifact storage
├── gitlab-ci-with-gitlab-pages.yml  # Includes Pages deployment
├── gitlab-ci-shell-runner.yml       # For self-hosted runners
└── gitlab-ci-custom-templates.yml   # Custom template integration
```

### Generic CI Examples

```
docs/examples/
├── scripts/generate-docs.sh         # Portable shell script
├── jenkins/Jenkinsfile              # Declarative Pipeline
├── woodpecker/.woodpecker.yml       # Woodpecker YAML
├── circleci/config.yml              # CircleCI config
└── travis/.travis.yml               # Travis CI config
```

---

## Common Tasks

### How do I...

**Get started with GitHub Actions?**
1. Read [Quickstart Guide](../specs/003-ci-workflow-setup/quickstart.md#github-actions-5-minute-setup)
2. Copy [github-actions-basic.yml](./examples/workflows/github-actions-basic.yml)
3. Check [CI_INTEGRATION.md#github-actions](./CI_INTEGRATION.md#github-actions-integration) for details

**Get started with GitLab CI/CD?**
1. Read [Quickstart Guide](../specs/003-ci-workflow-setup/quickstart.md#gitlab-cicd-5-minute-setup)
2. Copy [gitlab-ci-basic.yml](./examples/gitlab-ci-basic.yml)
3. Check [CI_INTEGRATION.md#gitlab-cicd](./CI_INTEGRATION.md#gitlab-cicd-integration) for details

**Publish docs to GitHub Pages?**
1. See [PUBLISHING.md#github-pages](./PUBLISHING.md#1-github-pages-recommended-for-github-users)
2. Use [github-actions-with-github-pages.yml](./examples/workflows/github-actions-with-github-pages.yml)
3. Troubleshoot with [TROUBLESHOOTING.md#github-pages](./TROUBLESHOOTING.md#github-pages)

**Publish docs to GitLab Pages?**
1. See [PUBLISHING.md#gitlab-pages](./PUBLISHING.md#2-gitlab-pages)
2. Use [gitlab-ci-with-gitlab-pages.yml](./examples/gitlab-ci-with-gitlab-pages.yml)
3. Troubleshoot with [TROUBLESHOOTING.md#gitlab-pages](./TROUBLESHOOTING.md#gitlab-pages)

**Set up custom templates?**
1. See [ENVIRONMENT_VARIABLES.md#anodyse-specific-variables](./ENVIRONMENT_VARIABLES.md#optional-variables)
2. Use [github-actions-custom-templates.yml](./examples/workflows/github-actions-custom-templates.yml)
3. Check template examples in [examples/templates/](./examples/templates/)

**Troubleshoot a problem?**
1. Search [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for your issue
2. Check platform-specific section (GitHub Actions, GitLab CI, etc.)
3. See FAQ at end of each platform section

**Add my CI platform?**
1. Review [CI_EXAMPLES_CONTRIBUTING.md](./CI_EXAMPLES_CONTRIBUTING.md)
2. Check existing examples in [examples/](./examples/) for patterns
3. Create example configuration and documentation
4. Submit pull request

---

## Quick Reference

### Anodyse CLI

Invoke Anodyse in any CI system with:

```bash
python -m anodyse \
  --input-path ./playbooks \
  --output-path ./docs \
  --template-dir ./templates     # optional
```

### Exit Codes

- **0**: Success
- **1**: General error
- **2**: Configuration error
- **127**: Command not found

### Key Files

| File | Purpose |
|------|---------|
| `CI_INTEGRATION.md` | Main documentation hub |
| `PUBLISHING.md` | Publishing platforms guide |
| `TROUBLESHOOTING.md` | Troubleshooting & FAQ |
| `ENVIRONMENT_VARIABLES.md` | Variables reference |
| `examples/workflows/` | GitHub Actions examples |
| `examples/*-ci-*.yml` | Other CI system examples |
| `examples/scripts/generate-docs.sh` | Portable shell script |

---

## Documentation Statistics

| Metric | Value |
|--------|-------|
| Total documentation files | 8 core docs + examples |
| Total lines of documentation | 4,700+ |
| Example workflows | 4 (GitHub Actions) + 3 (GitLab) + 5 (generic) |
| Platform support | 6+ (GitHub Actions, GitLab, Jenkins, Woodpecker, CircleCI, Travis) |
| Troubleshooting scenarios | 50+ |
| FAQ items | 30+ |

---

## Getting Help

1. **Quick answers**: Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) FAQ sections
2. **Setup help**: Follow [Quickstart Guide](../specs/003-ci-workflow-setup/quickstart.md)
3. **Detailed reference**: See platform-specific reference docs
4. **Not covered?**: Open issue or contribute (see [CI_EXAMPLES_CONTRIBUTING.md](./CI_EXAMPLES_CONTRIBUTING.md))

---

## Navigation by Scenario

### "I use GitHub"
→ [CI_INTEGRATION.md#github-actions](./CI_INTEGRATION.md#github-actions-integration) → [github-actions-basic.yml](./examples/workflows/github-actions-basic.yml)

### "I use GitLab"
→ [CI_INTEGRATION.md#gitlab-cicd](./CI_INTEGRATION.md#gitlab-cicd-integration) → [gitlab-ci-basic.yml](./examples/gitlab-ci-basic.yml)

### "I use Jenkins/Woodpecker/CircleCI/Travis"
→ [CI_INTEGRATION.md#generic-ci-patterns](./CI_INTEGRATION.md#generic-ci-patterns) → [examples/](./examples/)

### "I want to publish docs online"
→ [PUBLISHING.md](./PUBLISHING.md) → Platform-specific section

### "Something is broken"
→ [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) → Platform/issue section

### "I want to contribute"
→ [CI_EXAMPLES_CONTRIBUTING.md](./CI_EXAMPLES_CONTRIBUTING.md)

---

**Last Updated**: March 4, 2026  
**Status**: All core documentation complete ✅  
**Ready for**: Phase 3 (GitLab) and beyond
