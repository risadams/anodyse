# CI Integration Setup Validation Checklists

Use these checklists to verify your CI/CD integration is set up correctly.

## GitHub Actions Setup Checklist

**Before Setup**
- [ ] You have a GitHub repository with Ansible playbooks/roles
- [ ] You have write access to repository settings
- [ ] Your playbooks directory exists (e.g., `./playbooks`)

**Installation** (3 steps, ~5 minutes)
- [ ] Created `.github/workflows/generate-docs.yml` (or similar)
- [ ] Updated `ANODYSE_INPUT_DIR` to your playbooks directory
- [ ] Updated `ANODYSE_OUTPUT_DIR` to desired output directory (default: `./docs`)

**Verification**
- [ ] Committed workflow file to repository
- [ ] Pushed commit to GitHub
- [ ] Checked Actions tab - workflow appears in list
- [ ] Workflow completed successfully (green checkmark)
- [ ] Artifacts available for download (check Actions tab)
- [ ] Generated documentation files exist in output directory
- [ ] `index.md` file was created

**Customization** (Optional)
- [ ] Changed trigger events as needed (push, PR, schedule, manual)
- [ ] Configured artifact retention period
- [ ] Added custom Python version if needed
- [ ] Tested workflow on pull request (should run but not deploy)

**Publishing** (Optional - to GitHub Pages)
- [ ] Added GitHub Pages deployment step to workflow
- [ ] Enabled GitHub Pages in repository settings
- [ ] Set source to "GitHub Actions"
- [ ] Verified docs are published to `https://username.github.io/repo-name`
- [ ] Cleared browser cache and verified latest docs showing

**Troubleshooting**
- [ ] Workflow logs show no errors
- [ ] Input directory contains valid Ansible files
- [ ] Output files are not in `.gitignore`
- [ ] Python 3.9+ is being used
- [ ] `anodyse` installed successfully (check workflow logs)

**Team Handoff** (Ready to share)
- [ ] Documentation is accessible to team members
- [ ] GitHub Pages is public (or repo is available to team)
- [ ] Team members can download artifacts from Actions tab
- [ ] Documentation updates automatically on commits

---

## GitLab CI/CD Setup Checklist

**Before Setup**
- [ ] You have a GitLab project with Ansible playbooks/roles
- [ ] You have maintainer or owner access to project settings
- [ ] Your playbooks directory exists (e.g., `playbooks/`)
- [ ] A GitLab Runner is available (shared or group runner)

**Installation** (3-4 steps, ~5-10 minutes)
- [ ] Created `.gitlab-ci.yml` in repository root (or added to existing file)
- [ ] Updated `ANODYSE_INPUT_DIR` variable to your playbooks directory
- [ ] Updated `ANODYSE_OUTPUT_DIR` variable to desired output directory
- [ ] Updated Docker image if needed (default: `python:3.11-slim`)

**Verification**
- [ ] Committed `.gitlab-ci.yml` to repository
- [ ] Pushed commit to GitLab
- [ ] Checked CI/CD → Pipelines - pipeline appears in list
- [ ] Pipeline completed successfully (green status)
- [ ] Job artifacts are available for download
- [ ] Artifacts contain generated documentation files
- [ ] `index.md` file was created

**Runner Configuration**
- [ ] Runner is available and healthy (green status)
- [ ] Runner has network access to pull Python packages
- [ ] Runner has sufficient disk space (check `df -h` in job logs)
- [ ] Docker is available or shell runner configured

**Customization** (Optional)
- [ ] Changed trigger events (push, merge_request, schedule)
- [ ] Configured artifact retention period
- [ ] Updated Python version if needed
- [ ] Tested pipeline on merge request (should run but not publish)

**Publishing** (Optional - to GitLab Pages)
- [ ] Added `pages:` job to `.gitlab-ci.yml`
- [ ] Set `artifacts.paths` to `[public/]` or similar
- [ ] Generated docs output to `public/` directory
- [ ] Enabled GitLab Pages in project settings
- [ ] Verified docs are published to project URL
- [ ] Cleared browser cache and verified latest docs showing

**Variable Scoping**
- [ ] Variables accessible to all jobs (if project-level)
- [ ] Group variables accessible if defined (if group-level)
- [ ] No hardcoded secrets in `.gitlab-ci.yml`

**Troubleshooting**
- [ ] Pipeline logs show no errors
- [ ] Input directory contains valid Ansible files
- [ ] Docker image pulls successfully
- [ ] Python 3.9+ is available in image
- [ ] `anodyse` installed successfully (check job logs)

**Team Handoff** (Ready to share)
- [ ] Documentation is accessible to team members
- [ ] GitLab Pages is public (or project is available to team)
- [ ] Team members can download artifacts from CI/CD page
- [ ] Documentation updates automatically on commits

---

## Generic CI Setup Checklist (Jenkins, Woodpecker, CircleCI, Travis)

**Before Setup**
- [ ] You have access to your CI system
- [ ] You have a repository or project set up
- [ ] Your playbooks directory exists and is committed
- [ ] You can edit CI configuration files

**Installation** (varies by platform, ~10-20 minutes)

### Jenkins (Declarative Pipeline)
- [ ] Created `Jenkinsfile` in repository root
- [ ] Updated `sh` commands with your paths
- [ ] Created Jenkins pipeline job pointing to repository
- [ ] Verified pipeline trigger is enabled
- [ ] Ran pipeline manually and verified success

### Woodpecker
- [ ] Created `.woodpecker.yml` in repository root
- [ ] Updated `environment` variables with your paths
- [ ] Enabled repository in Woodpecker UI
- [ ] Verified pipeline trigger is enabled
- [ ] Ran pipeline manually and verified success

### CircleCI
- [ ] Created `.circleci/config.yml`
- [ ] Updated `environment` variables with your paths
- [ ] Connected repository in CircleCI UI
- [ ] Verified pipeline trigger is enabled
- [ ] Ran pipeline manually and verified success

### Travis CI
- [ ] Created `.travis.yml`
- [ ] Updated `env` variables with your paths
- [ ] Connected repository in Travis UI
- [ ] Verified build trigger is enabled
- [ ] Ran build manually and verified success

**Verification**
- [ ] Pipeline/job completed successfully
- [ ] Build logs show no errors
- [ ] Documentation files were generated
- [ ] Artifacts are available for download or viewing
- [ ] `index.md` file was created
- [ ] All expected documentation files present

**Environment Setup**
- [ ] Python 3.9+ available in build environment
- [ ] `pip install anodyse` completed successfully
- [ ] Working directory contains your playbooks
- [ ] Output directory is writable

**Customization** (Optional)
- [ ] Updated trigger conditions (branch, schedule, manual)
- [ ] Added artifact retention period
- [ ] Configured error handling (fail-fast vs. continue)
- [ ] Tested on non-main branches if applicable

**Publishing** (Optional)
- [ ] Configured deployment/publishing step
- [ ] Verified docs accessible after publish
- [ ] Set up custom domain if applicable

**Troubleshooting**
- [ ] Build/pipeline logs show all steps completing
- [ ] Input directory path is correct
- [ ] Ansible files are valid YAML
- [ ] No permission errors in logs
- [ ] Sufficient disk space for generated docs

**Team Handoff** (Ready to share)
- [ ] Documentation is accessible to team
- [ ] Team can trigger builds/pipelines
- [ ] Documentation updates automatically on commits

---

## Post-Setup Validation

**Verify Integration is Working**

After completing platform-specific checklist:

- [ ] Commit a change to your Ansible playbooks
- [ ] Push to your repository
- [ ] Workflow/pipeline triggers automatically
- [ ] Build completes within expected time (usually < 5 minutes)
- [ ] New documentation generated with your changes
- [ ] Team can access generated documentation
- [ ] No errors in build logs

**Advanced Validation**

Test edge cases:

- [ ] Commit to non-main branch - workflow runs but doesn't publish
- [ ] Pull request - documentation generates and artifacts available
- [ ] Scheduled run - documentation regenerated without new code
- [ ] Manual trigger - you can start workflow from UI
- [ ] Invalid YAML - workflow fails gracefully with clear error
- [ ] Missing input directory - workflow fails with helpful message

**Performance Validation**

- [ ] First run takes < 5 minutes
- [ ] Subsequent runs use caching (faster)
- [ ] Generation time scales linearly with playbook size
- [ ] No timeout failures on large playbook collections

**Quality Validation**

- [ ] Generated markdown is properly formatted
- [ ] All playbooks/roles included in index
- [ ] Links between documents are correct
- [ ] Code examples are properly highlighted
- [ ] Task descriptions are complete

---

## Troubleshooting Guide

If any checklist item fails:

1. **Check build logs** - See platform-specific logs for error details
2. **Verify paths** - `ANODYSE_INPUT_DIR` points to real directory
3. **Check permissions** - Output directory is writable
4. **Verify files** - Ansible files are valid YAML
5. **Review docs** - See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

For platform-specific help:
- **GitHub Actions**: [TROUBLESHOOTING.md#github-actions](./TROUBLESHOOTING.md#github-actions)
- **GitLab CI**: [TROUBLESHOOTING.md#gitlab-cicd](./TROUBLESHOOTING.md#gitlab-cicd)
- **Jenkins**: [TROUBLESHOOTING.md#jenkins](./TROUBLESHOOTING.md#jenkins)
- **Generic CI**: [TROUBLESHOOTING.md#generic-ci-systems](./TROUBLESHOOTING.md#generic-ci-systems)

---

## Next Steps

Once setup is validated:

1. **Customize for your workflow**
   - Change triggers, templates, options
   - See [CI_INTEGRATION.md](./CI_INTEGRATION.md) for advanced options

2. **Publish documentation**
   - Set up GitHub Pages, GitLab Pages, or external hosting
   - See [PUBLISHING.md](./PUBLISHING.md)

3. **Share with team**
   - Grant repository access
   - Share documentation links
   - Document team-specific paths/customizations

4. **Monitor and maintain**
   - Watch for build failures
   - Update workflows as Anodyse updates
   - Refresh documentation regularly

5. **Extend with custom templates**
   - Create custom Jinja2 templates
   - Brand documentation with team styling
   - See [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md#optional-variables)

---

**Last Updated**: March 4, 2026  
**See Also**: 
- [CI_INTEGRATION.md](./CI_INTEGRATION.md) - Complete integration guide
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Detailed troubleshooting
- [CI_EXAMPLES_CONTRIBUTING.md](./CI_EXAMPLES_CONTRIBUTING.md) - Contributing examples
