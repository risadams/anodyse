# Generic CI/CD Integration Guide

Use Anodyse with any CI/CD platform that supports shell script execution. This guide covers common patterns and teaches you how to adapt Anodyse integration to your specific platform.

**Table of Contents**
- [When to Use Generic Patterns](#when-to-use-generic-patterns)
- [Core CLI Patterns](#core-cli-patterns)
- [Portable Shell Script](#portable-shell-script)
- [Platform-Specific Adaptation](#platform-specific-adaptation)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Contributing New Platforms](#contributing-new-platforms)

---

## When to Use Generic Patterns

Use generic patterns when:

✅ Your CI system is not covered by platform-specific guides (Jenkins, Woodpecker, CircleCI, Travis)
✅ You have a custom or proprietary CI system
✅ You want to understand the underlying integration concepts
✅ You need portability across multiple CI systems
✅ You prefer a single shell script over multiple platform configurations

❌ For GitHub, use [GitHub Actions Guide](./CI_INTEGRATION.md#github-actions-integration)
❌ For GitLab, use [GitLab CI/CD Guide](./CI_INTEGRATION.md#gitlab-cicd-integration)
❌ For supported platforms, use their specific guide (usually simpler)

---

## Core CLI Patterns

### Basic Invocation

At its core, Anodyse is a Python CLI tool:

```bash
python -m anodyse \
  --input-path ./playbooks \
  --output-path ./docs
```

**Exit Codes**:
- `0`: Success - documentation generated
- `1`: Failure - check error message in logs
- `2`: Configuration error - invalid arguments

### Environment Variables

All Anodyse configuration can pass via environment variables:

```bash
export ANODYSE_INPUT_DIR=./playbooks
export ANODYSE_OUTPUT_DIR=./docs
export ANODYSE_TEMPLATE_DIR=./templates
export ANODYSE_VERBOSE=true

python -m anodyse \
  --input-path $ANODYSE_INPUT_DIR \
  --output-path $ANODYSE_OUTPUT_DIR \
  --template-dir $ANODYSE_TEMPLATE_DIR
```

**Reference**: See [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md) for complete list.

### Error Handling

Always check exit codes in CI:

```bash
#!/bin/bash
set -e  # Exit on any error

python -m anodyse --input-path ./playbooks --output-path ./docs

if [ $? -ne 0 ]; then
    echo "FATAL: Documentation generation failed"
    exit 1
fi

echo "SUCCESS: Documentation generated"
```

---

## Portable Shell Script

We provide a complete, documented shell script that works on any CI/CD platform:

### Use the Pre-Built Script

```bash
# Copy to your repository
curl -o scripts/generate-docs.sh \
  https://raw.githubusercontent.com/acuity-inc/anodyse/main/docs/examples/scripts/generate-docs.sh

chmod +x scripts/generate-docs.sh

# Run it
./scripts/generate-docs.sh
```

### Script Features

- Automatic Python environment setup (venv)
- Pre-flight checks (Python version, input directory, required commands)
- Comprehensive logging (info, debug, error levels)
- Automatic cleanup (optional venv removal)
- Cross-platform compatibility (Linux, macOS, Windows WSL)
- Extensive error handling and validation

### Script Configuration

Control via environment variables:

```bash
# Override defaults
INPUT_DIR=./ansible
OUTPUT_DIR=./generated-docs
TEMPLATE_DIR=./templates
VERBOSE=true
CLEANUP_VENV=true

./scripts/generate-docs.sh
```

---

## Platform-Specific Adaptation

### Step 1: Identify Platform Requirements

Before adapting Anodyse, understand your CI platform:

| Question | Example |
|----------|---------|
| What shell is available? | bash, sh, powershell |
| Can containers/Docker run? | Docker, Podman, containerd |
| How do you specify environment? | env vars, docker image, setup steps |
| How do I store artifacts? | Registry, S3-compatible, local upload |
| How do I define jobs/stages? | YAML, UI, Groovy DSL |

### Step 2: Understand Your Platform's Build Steps

Most CI systems follow this pattern:

```
1. Checkout code
2. Setup environment (language, packages)
3. Install dependencies
4. Run build script
5. (Optional) Store artifacts
6. (Optional) Deploy
```

Anodyse fits in **steps 3-4**:

```bash
# Step 3: Install Anodyse (as dependency)
pip install anodyse

# Step 4: Run generation
python -m anodyse --input-path ./playbooks --output-path ./docs
```

### Step 3: Adapt from Platform Example

Find the closest example and modify:

| Your Platform | Adapt From |
|---|---|
| Custom Bash | [Shell Script](./examples/scripts/generate-docs.sh) |
| Job queue (Celery, Rq) | [Generic Pattern](#core-cli-patterns) |
| Lambda/Serverless | [Shell Script](#portable-shell-script) with timeout increases |
| Docker/Container only | Any example (remove venv setup) |
| Proprietary | Generic pattern section |

### Step 4: Customize Paths and Triggers

At minimum, customize:

1. **Input/Output directories**: Match your repository layout
2. **Triggers**: When to run (push, PR, schedule, manual)
3. **Python version**: Anodyse requires 3.9+
4. **Artifact handling**: Where to store generated docs

Example customization:

```bash
#!/bin/bash

# Your platform's environment
INPUT_DIR="${MY_REPO}/ansible"
OUTPUT_DIR="${MY_WORKSPACE}/docs"

# Install
pip install anodyse

# Generate
python -m anodyse \
  --input-path "$INPUT_DIR" \
  --output-path "$OUTPUT_DIR"

# Store (your platform's artifact mechanism)
my-platform-store-artifact "$OUTPUT_DIR"
```

---

## Best Practices

### 1. Verify Python Version Early

```bash
python3 --version  # Check 3.9+
pip3 --version
```

### 2. Use Virtual Environments

Isolate Anodyse from system Python:

```bash
python3 -m venv /tmp/anodyse_venv
source /tmp/anodyse_venv/bin/activate
pip install anodyse
```

### 3. Log Important Information

```bash
echo "=========================================="
echo "Anodyse Documentation Generation"
echo "=========================================="
echo "Input:  $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo "Time:   $(date)"
```

### 4. Validate Output Before Publishing

```bash
if [ ! -f "$OUTPUT_DIR/index.md" ]; then
    echo "ERROR: index.md not generated"
    exit 1
fi
```

### 5. Handle Failures Gracefully

```bash
if ! python -m anodyse --input-path "$INPUT_DIR" --output-path "$OUTPUT_DIR"; then
    echo "ERROR: Documentation generation failed"
    exit 1
fi
```

### 6. Clean Up After Yourself

```bash
# Remove temporary virtual environment
rm -rf "$VENV_PATH"

# Remove temporary files
rm -rf /tmp/anodyse_*
```

### 7. Document Your Integration

```bash
# Include comments explaining setup
# This helps future maintainers understand
# why choices were made
```

### 8. Use Meaningful Exit Codes

```bash
# Success
exit 0

# Failure cases
exit 1  # General failure
exit 2  # Configuration error
```

---

## Troubleshooting

### Issue: Python not found

**Symptoms**: Module not found, python command doesn't exist

**Solutions**:
1. Specify full path: `/usr/bin/python3` or `/usr/local/bin/python3`
2. Use system package manager: `apt install python3.11` or `brew install python`
3. Load required modules: `module load python` (on HPC systems)

### Issue: Permission denied

**Symptoms**: Can't execute scripts or write to directories

**Solutions**:
1. Make script executable: `chmod +x generate-docs.sh`
2. Run with proper user: CI systems should handle this
3. Check directory permissions: `chmod -R u+w ./docs`

### Issue: Input directory empty or not found

**Symptoms**: Error: "no YAML files found" or "directory not found"

**Solutions**:
1. Verify working directory: `pwd` and `ls ./playbooks`
2. Use absolute paths: `/home/user/project/playbooks`
3. Check checkout: Ensure code was checked out first

### Issue: Disk space exhausted

**Symptoms**: Artifact upload fails, disk full error

**Solutions**:
1. Clean up temporary files: `rm -rf /tmp/anodyse_*`
2. Increase artifact retention limits
3. Use image with more disk space (Docker/container systems)

### Issue: Network connectivity problems

**Symptoms**: Pip install fails, external templates timeout

**Solutions**:
1. Use `--no-index` to skip PyPI: `pip install --no-index anodyse-wheel.whl`
2. Download templates beforehand
3. Use internal package repository/mirror

---

## Contributing New Platforms

Want to add support for your CI platform?

### Process

1. **Create configuration file**: Follow pattern from existing examples
2. **Write documentation**: Step-by-step setup guide
3. **Test thoroughly**: Run multiple times with different triggers
4. **Document platform requirements**: Python version, runner type, etc.
5. **Submit pull request**: Include example and documentation

### Files to Create

- `docs/examples/[platform]/.platform-specific-file`
- Update [CI_INTEGRATION.md](./CI_INTEGRATION.md) if major platform
- Update [CI_PLATFORM_SUPPORT.md](./CI_PLATFORM_SUPPORT.md)

### Template

Follow this template for new platforms:

```yaml
# [Platform Name] Configuration: Anodyse Documentation Generation
#
# Setup time: X minutes
# Difficulty: Beginner/Intermediate/Advanced
#

# Platform-specific configuration...

# Feature: Environment variables
# Feature: Custom templates
# Feature: Error handling
# Feature: Artifact storage

# Installation/Setup section
# Customization guide section
# Troubleshooting section
```

### Testing Checklist

Before submission:

- [ ] Configuration is valid for the platform
- [ ] Documentation generation works end-to-end
- [ ] Artifacts are generated correctly
- [ ] Errors are handled gracefully
- [ ] README/documentation included
- [ ] Tested on actual CI platform (not just locally)
- [ ] Paths use relative notation (./playbooks)
- [ ] Multiple runtime examples included

---

## Examples by Platform

See specific example configurations:

**Supported Platforms**:
- [Jenkins](./examples/jenkins/Jenkinsfile)
- [Woodpecker CI](./examples/woodpecker/.woodpecker.yml)
- [CircleCI](./examples/circleci/config.yml)
- [Travis CI](./examples/travis/.travis.yml)
- [Shell Script (all platforms)](./examples/scripts/generate-docs.sh)

**Platform Comparison**: See [CI_PLATFORM_SUPPORT.md](./CI_PLATFORM_SUPPORT.md) for feature matrix.

---

## See Also

- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues across all platforms
- [Environment Variables](./ENVIRONMENT_VARIABLES.md) - Complete configuration reference
- [Publishing Guide](./PUBLISHING.md) - Where to host generated documentation
- [Platform Comparison](./PLATFORM_COMPARISON.md) - GitHub Actions vs GitLab CI/CD
- [Contributing Guide](./CI_EXAMPLES_CONTRIBUTING.md) - How to contribute new examples

---

**Last Updated**: March 2026
**Anodyse Version**: 1.0+
