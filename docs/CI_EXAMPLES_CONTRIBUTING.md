# Contributing CI Integration Examples

Thank you for helping expand Anodyse's CI/CD platform support! This guide explains how to contribute new CI platform examples and improve existing ones.

## Overview

Anodyse provides copy-paste-ready CI/CD integration examples for:
- **Priority 1 (P1)**: GitHub Actions, GitLab CI/CD
- **Priority 3 (P3)**: Jenkins, Woodpecker, CircleCI, Travis CI, and others

Examples are located in [`docs/examples/`](./examples/) organized by platform.

## Adding a New CI Platform

### Prerequisites

- Experience with the target CI platform
- Access to a test environment (free tier or sandbox acceptable)
- Familiarity with Ansible playbooks and Python

### Submission Process

1. **Check existing examples** in `docs/examples/` to avoid duplication
2. **Create a feature branch**: `git checkout -b feature/ci-examples-<platform-name>`
3. **Add example configuration** following the structure below
4. **Document the integration** in the relevant guide
5. **Test thoroughly** on actual CI platform
6. **Submit pull request** with test results

### Directory Structure

```
docs/examples/
├── workflows/              # GitHub Actions YAML files
├── templates/              # Custom Jinja2 template examples
├── jenkins/                # Jenkins Declarative Pipeline examples
├── woodpecker/             # Woodpecker CI YAML examples
├── circleci/               # CircleCI config.yml examples
└── scripts/                # Portable shell scripts
```

### Example File Format

#### Configuration Files

**GitHub Actions** (`.yml` in `workflows/`):
```yaml
# Minimal example showing all required elements
name: Generate Documentation
# ... rest of config
```

**GitLab CI** (`.yml` in `examples/`):
```yaml
# Minimal example showing all required elements
stages:
  - generate
# ... rest of config
```

**Jenkins** (`Jenkinsfile` in `jenkins/`):
```groovy
// Minimal example showing all required elements
pipeline {
    agent any
    // ... rest of config
}
```

**Other Platforms**: Follow your platform's standard config file naming convention

#### Documentation in Config

Every example must include:
- **Comments explaining each section**
- **Environment variable references** with defaults
- **Error handling patterns**
- **Customization instructions**
- **Link to full guide**

Example:
```yaml
# Set to your Ansible playbooks directory
# Default: ./playbooks
ANODYSE_INPUT_DIR: ./playbooks

# Where to output generated documentation  
# Default: ./docs
ANODYSE_OUTPUT_DIR: ./docs
```

### Documentation Requirements

For each new platform, create or update:

1. **Reference guide**: `docs/<PLATFORM>-ci-reference.md`
   - Schema explanation
   - Configuration options
   - Available runners/executors
   - Customization examples

2. **Integration section** in `docs/CI_INTEGRATION.md#<platform>`
   - Setup steps (with estimated time)
   - Copy-paste quick start
   - Common customizations
   - Platform-specific troubleshooting

3. **Example files** in `docs/examples/<platform>/`
   - Basic configuration
   - Advanced configuration with GitHub/GitLab Pages
   - All-triggers example
   - Custom template example (if applicable)

### Testing Checklist

Before submitting, verify:

- [ ] Configuration file has valid syntax (use platform's linter)
- [ ] Example runs successfully on your test instance
- [ ] Documentation generation completes without errors
- [ ] Generated artifacts are accessible
- [ ] Error handling works (simulate missing files, invalid YAML, timeouts)
- [ ] Environment variables can be customized
- [ ] All comments and examples are accurate
- [ ] No hardcoded secrets or tokens
- [ ] Cross-platform compatibility verified (Windows, macOS, Linux if applicable)

### Pull Request Template

```markdown
## Platform: [Platform Name]

### Description
[Brief description of the CI platform and why it's valuable for Anodyse users]

### What's included
- [ ] Reference guide (`docs/<platform>-ci-reference.md`)
- [ ] Integration section in `docs/CI_INTEGRATION.md`
- [ ] Example configurations in `docs/examples/<platform>/`
- [ ] Troubleshooting section in `docs/TROUBLESHOOTING.md#<platform>`

### Testing
- [ ] Tested on [platform name] (free tier/self-hosted)
- [ ] Verified with actual Ansible playbooks
- [ ] Documentation generates successfully
- [ ] All error scenarios handled gracefully
- [ ] Environment variables customizable

### Notes
[Any platform-specific considerations, limitations, or recommendations]
```

## Style Guide

### YAML/Configuration Style

- Use 2-space indentation
- Include comments explaining non-obvious sections
- Show environment variable usage with `${VAR}` or `$VAR` syntax per platform
- Keep line length ≤ 80 characters for readability

### Documentation Style

- Write in second person: "You can customize..."
- Use step-by-step instructions for setup
- Include estimated time per step
- Link to relevant troubleshooting sections
- Show before/after examples for customizations

### Naming Conventions

- GitHub Actions: `github-actions-<variant>.yml`
  - Examples: `github-actions-basic.yml`, `github-actions-with-github-pages.yml`
  
- GitLab CI: `gitlab-ci-<variant>.yml`
  - Examples: `gitlab-ci-basic.yml`, `gitlab-ci-shell-runner.yml`

- Other platforms: `<platform>-<variant>.<ext>`
  - Examples: `jenkins-basic-Jenkinsfile`, `woodpecker-docker.yml`

## Updating Existing Examples

To improve an existing example:

1. Identify the issue (bug, clarity, missing feature)
2. Create branch: `git checkout -b fix/ci-examples-<platform>-<issue>`
3. Update example and documentation
4. Test thoroughly
5. Submit PR with explanation of changes

## Platform-Specific Guidelines

### GitHub Actions

- Use `v4` of GitHub Actions (latest major version)
- Reference latest Python version available
- Use GitHub's official checkout and setup actions
- Document secrets management
- Show GitHub Pages deployment pattern

### GitLab CI

- Support both Docker and shell runners
- Show `rules:` for modern trigger syntax
- Document CI/CD variable scoping (project/group/instance)
- Show GitLab Pages integration
- Document runner tags if needed

### Jenkins

- Use Declarative Pipeline (not Scripted)
- Document groovy syntax clearly
- Show multi-stage pipeline with error handling
- Include post-build actions (archive artifacts, cleanup)
- Show parameter support for customization

### Woodpecker

- Show Docker image usage
- Document privileged mode if needed
- Show artifact handling
- Include error handling patterns
- Document trigger conditions

### Other Platforms

- Follow community best practices
- Document any non-standard syntax
- Include platform-specific environment variables
- Show how to integrate with external services
- Link to platform documentation

## Questions?

- Check existing examples in `docs/examples/`
- Review completed PRs for patterns
- Open an issue with `[CI-EXAMPLES]` tag in your question
- Reference the [CI Integration Guide](./CI_INTEGRATION.md)

## Thanks!

Your contributions help the Anodyse community integrate Ansible documentation generation into their existing workflows. 🙏

---

**Last Updated**: March 4, 2026  
**Maintained By**: Anodyse Core Team
