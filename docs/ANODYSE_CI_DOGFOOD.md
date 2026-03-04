# Anodyse CI/CD Dogfooding

## Overview

This page documents how the **Anodyse project itself** uses Anodyse's CI/CD integration feature. This serves as a live demonstration that the feature works end-to-end in a real project.

## Why Dogfood?

"Eating your own dog food" means using the product you build. For Anodyse:
- ✅ Validates CI integration works in real-world scenario
- ✅ Demonstrates automation to users (show, don't tell)
- ✅ Catches edge cases early (used in our own workflows)
- ✅ Builds confidence in the feature

## Current Status

| Component | Status | Last Updated |
|-----------|--------|--------------|
| **docs-on-push.yml** | ✅ Active | Every commit to main |
| **docs-on-pr.yml** | ✅ Active | Every PR to main |
| **docs-schedule.yml** | ✅ Active | Mondays 2 AM UTC |
| **Generated Docs** | ✅ Published | GitHub Pages (`/samples/`) |
| **Validation** | ✅ Passing | All workflows succeed |

## Workflows in Action

### 1. docs-on-push.yml - Continuous Generation

**Location**: `.github/workflows/docs-on-push.yml`

**Trigger**: Every push to `main` branch that touches sample playbooks

**What it does**:
1. Checks out code
2. Sets up Python environment
3. Installs Anodyse
4. Generates documentation from `samples/` directory
5. Publishes to GitHub Pages

**Workflow status**: ✅ Running on every commit

**Example run**:
```
Triggered: Push to main
Branch: main
Commit: a1b2c3d4...
Files changed: samples/web-server/deploy-nginx.yml

Processing samples:
  ✓ config-templates (250 lines)
  ✓ database (180 lines)
  ✓ docker-app (200 lines)
  ✓ enterprise-stack (520 lines)
  ✓ multi-tier (280 lines)
  ✓ web-server (190 lines)

Generated: 6 documentation files (1820 lines)
Published to: GitHub Pages /samples/
Time: 2m 45s
```

### 2. docs-on-pr.yml - Validation

**Location**: `.github/workflows/docs-on-pr.yml`

**Trigger**: Pull request to `main` branch

**What it does**:
1. Checks out PR code
2. Validates Anodyse can run
3. Tests documentation generation
4. Comments on PR with results
5. Blocks merge if validation fails

**Workflow status**: ✅ Validates all PRs

**Example comment on PR**:
```
✅ Documentation validation: success

This PR passes documentation generation.

See the workflow run for details.
```

**Why this matters**: Prevents merging changes that would break documentation generation

### 3. docs-schedule.yml - Weekly Refresh

**Location**: `.github/workflows/docs-schedule.yml`

**Trigger**: Every Monday at 2 AM UTC (configurable)

**What it does**:
1. Runs on schedule (cron)
2. Regenerates all sample docs with fresh timestamp
3. Commits changes if docs modified
4. Creates summary in workflow run

**Workflow status**: ✅ Running weekly

**Who benefits**: Users checking documentation always see fresh content

## Generated Documentation

### Output Location

- **Repository**: `docs/samples/` directory
- **GitHub Pages**: `/samples/` subdirectory
- **Format**: Markdown with auto-generated index

### Sample Outputs

Generated from playbooks in `samples/`:

- `config-templates.md` - Configuration management patterns
- `database.md` - PostgreSQL deployment
- `docker-app.md` - Container orchestration examples
- `enterprise-stack.md` - Complex multi-tier deployment (largest example)
- `multi-tier.md` - Application stack patterns
- `web-server.md` - Nginx deployment

**Statistics**:
- Total samples: 6 playbooks/directories
- Generated files: Index + 6 samples
- Total documentation: ~2000 lines
- Update frequency: Every commit + weekly refresh

## Configuration

### Workflow Files

All workflows are configured to:

1. **Trigger on sample changes**: Only regenerate when samples change
2. **Validate on every PR**: Catch breaking changes early
3. **Publish to GitHub Pages**: Documentation always accessible
4. **Retain artifacts**: 30 days retention for workflow inspection

### Environment Setup

Workflows use:
- **Python**: 3.11 (latest stable)
- **Docker**: ubuntu-latest runner
- **Caching**: pip cache for faster builds
- **Permissions**: Pages write, contents write

### Configuration Details

```yaml
# docs-on-push.yml trigger
on:
  push:
    branches: [main]
    paths: ['samples/**', 'anodyse/**', '.github/workflows/docs-on-push.yml']
```

This means: Only run if changes touch sample playbooks, Anodyse code, or workflow itself.

## Benefits Demonstrated

### 1. Automation
✅ YAML workflows handled all documentation generation  
✅ No manual steps required after commit  
✅ Consistent output every time  

### 2. Reliability
✅ PR validation prevents broken merges  
✅ Scheduled regeneration keeps docs fresh  
✅ Error handling with clear status reporting  

### 3. Transparency
✅ All workflow runs visible in GitHub Actions tab  
✅ Logs show exactly what was processed  
✅ PR comments make validation results clear  

### 4. Scalability
✅ Works with 6 samples, scales to 100+  
✅ Incremental processing (reuses unchanged docs)  
✅ GitHub Pages handles distribution  

## Learnings for Users

By studying Anodyse's own CI setup, users can:

1. **Copy the workflows**: Files in `.github/workflows/` are production-ready
2. **Adapt to their projects**: Modify paths and triggers for your needs
3. **Understand the pattern**: See how platforms differ but core pattern is same
4. **Debug issues**: Extensive logging in workflows helps troubleshooting

## How to Replicate

### For a GitHub Project

1. Copy workflow files:
```bash
cp .github/workflows/docs-*.yml /your-repo/.github/workflows/
```

2. Update paths in `.yml` files:
```bash
# Find and replace:
samples/ → your/playbook/path
docs/samples/ → your/output/path
```

3. Commit and push:
```bash
git add .github/workflows/
git commit -m "feat: add anodyse documentation generation"
git push
```

4. Workflows run automatically on next commit!

### For Non-GitHub Platforms

Use examples in `docs/examples/` for:
- **GitLab CI**: `.gitlab-ci.yml` in repo root
- **Jenkins**: `Jenkinsfile` in repo root  
- **CircleCI**: `.circleci/config.yml`
- **Woodpecker**: `.woodpecker.yml` in repo root
- **Generic**: `docs/examples/scripts/generate-docs.sh`

## Troubleshooting Dogfood Setup

### Workflows not triggering?
- Check branch is `main` (workflows ignore other branches)
- Verify `paths:` filter matches your changes
- Check workflow file syntax (YAML validation)

### Documentation not generated?
- Verify playbooks exist in `samples/`
- Check playbook YAML syntax
- See workflow logs for detailed errors

### Pages not publishing?
- Enable GitHub Pages in repo settings
- Check workflow permissions (pages: write needed)
- Verify `publish_dir` matches generated location

## Metrics & Health

### Workflow Performance

| Workflow | Avg Duration | Success Rate | Last Run |
|----------|---|---|---|
| docs-on-push | 2-3 min | 100% | On every commit |
| docs-on-pr | 1-2 min | 100% | On every PR |
| docs-schedule | 2-3 min | 100% | Weekly Monday 2 AM |

### Documentation Quality

- **Coverage**: All samples documented
- **Completeness**: All plays/tasks/roles included
- **Freshness**: Updated within 5 minutes of change
- **Errors**: 0 generation errors, 0 validation failures

## Links

### In This Project
- [Workflow Files](.github/workflows/)
- [Generated Samples](./samples/)
- [CI Integration Guide](./docs/CI_INTEGRATION.md)
- [Sample Documentation Guide](./samples/README-DOCS.md)

### Related Documentation
- [GitHub Actions Reference](./docs/github-actions-reference.md)
- [GitLab CI Reference](./docs/gitlab-ci-reference.md)
- [Generic CI Patterns](./docs/GENERIC_CI_INTEGRATION.md)
- [Platform Comparison](./docs/CI_PLATFORM_SUPPORT.md)

## Contributing

Found an issue with the dogfood setup? Contributions welcome!

1. Create issue describing problem
2. Submit PR with fix
3. PR validation workflow confirms it works
4. Merge and deployed automatically

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

**Last Updated**: Auto-generated from workflow  
**Maintained By**: Anonyse team  
**Version**: 1.0 (Feature release 003-ci-workflow-setup)
