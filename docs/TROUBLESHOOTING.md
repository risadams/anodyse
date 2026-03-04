# Troubleshooting Guide: CI Workflow Integration Issues

Common issues and solutions when integrating Anodyse into your CI/CD pipeline.

**Table of Contents**
- [General Issues](#general-issues)
- [GitHub Actions](#github-actions)
- [GitLab CI/CD](#gitlab-cicd)
- [Generic CI Systems](#generic-ci-systems)
- [Publishing Issues](#publishing)
- [Advanced Debugging](#advanced-debugging)

---

## General Issues

### Issue: `anodyse command not found` or `ModuleNotFoundError: No module named 'anodyse'`

**Symptoms**: Workflow/pipeline fails with module not found error

**Solutions**:

1. **Verify installation step exists**:
   ```bash
   pip install anodyse
   python -m anodyse --help  # Verify installation
   ```

2. **Check Python version** (anodyse requires 3.9+):
   ```bash
   python --version
   ```
   If using Python < 3.9, update:
   - GitHub Actions: Change `python-version: '3.11'`
   - GitLab CI: Change `image: python:3.11-slim`

3. **Verify pip is up to date**:
   ```bash
   pip install --upgrade pip
   pip install anodyse
   ```

4. **Check installation in correct environment**:
   - Virtual env not activated? Source it before running anodyse
   - Using Docker? Install inside container: `RUN pip install anodyse`

---

### Issue: Missing input directory or file not found

**Symptoms**: Error like "Input directory ./playbooks not found" or "No playbooks found"

**Solutions**:

1. **Verify path exists in repository**:
   ```bash
   git ls-files | grep playbooks
   ```

2. **Check relative vs absolute paths**:
   - Use relative paths: `./playbooks` ✅
   - Avoid absolute paths: `/home/user/playbooks` ❌

3. **Check path case sensitivity** (especially important on Linux):
   - Windows: `./Playbooks` and `./playbooks` same
   - Linux: `./Playbooks` and `./playbooks` different ⚠️

4. **Verify working directory**:
   ```yaml
   # Wrong: assumes playbooks in workflow directory
   run: python -m anodyse --input-path ./playbooks
   
   # Right: ensure working directory first
   - name: Generate Documentation
     working-directory: ./project-root
     run: python -m anodyse --input-path ./playbooks
   ```

---

### Issue: No documentation generated (empty or missing main files)

**Symptoms**: Output directory created but is empty or missing `index.md`

**Solutions**:

1. **Verify Ansible syntax**:
   ```bash
   ansible-playbook --syntax-check playbooks/*.yml
   ```

2. **Check Anodyse annotations** in playbooks:
   - Ensure playbooks have proper `vars.description` or roles have documentation
   - Test locally first: `python -m anodyse --input-path ./playbooks --output-path /tmp/test`

3. **Enable verbose logging**:
   ```yaml
   - name: Generate Documentation (verbose)
     env:
      ANODYSE_VERBOSE: 'true'
     run: python -m anodyse --input-path ./playbooks --output-path ./docs
   ```

4. **Check file permissions**:
   - Output directory writable? `chmod 755 ./docs`
   - Input files readable? `chmod 644 ./playbooks/*.yml`

---

### Issue: Timeout during documentation generation

**Symptoms**: Workflow/pipeline aborted after X minutes, documentation not generated

**Solutions**:

1. **Increase timeout**:
   ```yaml
   # GitHub Actions (default 360 min)
   jobs:
     generate-docs:
       timeout-minutes: 60
       runs-on: ubuntu-latest
   ```

   ```yaml
   # GitLab CI (default 1 hour)
   generate_docs:
     timeout: 30 minutes  # Increase as needed
   ```

2. **Check for slow operations**:
   - Large playbook collection? Set up parallelization
   - Network operations? Check connectivity
   - Run locally to baseline: `time python -m anodyse ...`

3. **Profile the invocation**:
   ```bash
   time python -m anodyse --input-path ./playbooks --output-path ./docs --verbose
   ```

---

## GitHub Actions

### Issue: Workflow not triggering

**Symptoms**: Workflow file exists but never executes

**Solutions**:

1. **Verify workflow syntax**:
   ```bash
   # Validate YAML locally
   python -c "import yaml; yaml.safe_load(open('.github/workflows/build.yml'))"
   ```

2. **Check trigger conditions**:
   ```yaml
   on:
     push:
       branches: [main]  # Only triggers on main, not other branches
   
   # To trigger on all branches:
   on: [push, pull_request]
   ```

3. **Verify branch protection rules don't block workflow**:
   - Settings → Branches → Branch protection rules
   - Ensure workflow user has permission to commit

4. **Check workflow is enabled**:
   - Actions tab → Select workflow → "Enable workflow"

---

### Issue: Artifacts not uploading or disappearing after workflow

**Symptoms**: Artifacts tab empty or shows expired artifacts

**Solutions**:

1. **Verify artifact step syntax**:
   ```yaml
   - name: Upload Artifacts
     uses: actions/upload-artifact@v3
     with:
       name: ansible-docs
       path: ./docs/generated
       retention-days: 30
   ```

2. **Check if documentation files created**:
   ```yaml
   - name: Verify Documentation Generated
     run: |
       ls -la ./docs/generated/
       test -f ./docs/generated/index.md || exit 1
   ```

3. **Increase retention-days** if artifacts expiring too fast:
   ```yaml
   retention-days: 90  # Default is 5 days
   ```

4. **Check storage quotas**:
   - Private repos: Limited artifact storage
   - Solution: Archive or delete older artifacts, use external storage

---

### Issue: GitHub Pages not deploying documentation

**Symptoms**: Documentation workflow succeeds but GitHub Pages shows 404 or old content

**Solutions**:

1. **Verify GitHub Pages enabled**:
   - Settings → Pages
   - Source: "GitHub Actions" or specific branch
   - Custom domain (if applicable) correctly configured

2. **Check deployment step**:
   ```yaml
   - name: Deploy to GitHub Pages
     uses: peaceiris/actions-gh-pages@v3
     with:
       github_token: ${{ secrets.GITHUB_TOKEN }}
       publish_dir: ./public  # Must match docs output dir
   ```

3. **Clear browser cache** or use incognito window to see latest

4. **Verify files in publish_dir**:
   ```yaml
   - name: List files for deployment
     run: |
       echo "Files to deploy:"
       find ./public -type f
   ```

---

### Issue: Workflow fails with permission denied

**Symptoms**: Error about insufficient permissions or GitHub token issues

**Solutions**:

1. **Ensure GITHUB_TOKEN scope includes Pages**:
   - Workflows have limited token scope by default
   - For writing to Pages, use: `github_token: ${{ secrets.GITHUB_TOKEN }}`

2. **For custom access**: Create Personal Access Token
   ```yaml
   - uses: peaceiris/actions-gh-pages@v3
     with:
       personal_token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
   ```

3. **Check repository settings**:
   - Settings → Actions → General
   - "Read and write permissions" enabled for workflows

---

### Issue: Runner out of disk space

**Symptoms**: Error like "No space left on device" during documentation generation

**Solutions**:

1. **Clean up before building**:
   ```yaml
   - name: Clean up
     run: |
       df -h
       rm -rf /tmp/*
       sudo apt-get clean
   ```

2. **Use matrix strategy to split work**:
   ```yaml
   strategy:
     matrix:
       playbook-set: [playbooks/{a-m}*, playbooks/{n-z}*]
   ```

3. **Compress artifacts**:
   ```yaml
   - name: Compress Documentation
     run: |
       tar -czf docs.tar.gz ./docs
   
   - name: Upload Compressed
     uses: actions/upload-artifact@v3
     with:
       path: ./docs.tar.gz
   ```

---

## GitLab CI/CD

### Issue: Pipeline not triggering

**Symptoms**: `.gitlab-ci.yml` exists but pipeline never starts

**Solutions**:

1. **Verify `.gitlab-ci.yml` syntax**:
   ```bash
   # Check file is in repository root
   git ls-files | grep gitlab-ci.yml
   ```

2. **Check trigger rules**:
   ```yaml
   generate_docs:
     only:
       - main  # Only runs on main branch
       - merge_requests  # And on MRs
   ```

3. **Enable CI/CD for project**:
   - Project Settings → CI/CD → Enable CI/CD
   - Set runner availability

4. **Verify `.gitlab-ci.yml` is valid**:
   - Go to CI/CD → Pipelines
   - If configuration invalid, error shows here

---

### Issue: Docker runner not available or pulls wrong image

**Symptoms**: Error "No Docker runner available" or wrong Python version used

**Solutions**:

1. **Specify runner tags** if multiple runners available:
   ```yaml
   generate_docs:
     tags:
       - docker
       - ubuntu
   ```

2. **Verify Docker image exists and is correct**:
   ```yaml
   image: python:3.11-slim  # Specific version
   ```

3. **Use shell runner if Docker unavailable**:
   ```yaml
   generate_docs:
     script:
       - python3 -m venv /tmp/anodyse_venv
       - source /tmp/anodyse_venv/bin/activate
       - pip install anodyse
       - python -m anodyse --input-path ./playbooks --output-path ./docs
   ```

4. **Check runner is healthy**:
   - Admin Area → Runners
   - All runners listed should show green status
   - Red status means runner offline/unhealthy

---

### Issue: Artifacts not storing or expiring too quickly

**Symptoms**: Generated files disappear after pipeline completes

**Solutions**:

1. **Verify artifact configuration**:
   ```yaml
   artifacts:
     paths:
       - docs/generated/
     expire_in: 30 days  # Explicit retention
   ```

2. **Check artifact paths are correct**:
   ```yaml
   # List artifacts before uploading
   - name: List artifacts
     run: find ./docs -type f
   ```

3. **Storage quota exceeded**:
   - Check project quota: Settings → CI/CD → Artifacts
   - Delete old artifacts: CI/CD → Artifacts
   - Archive to object storage

---

### Issue: GitLab Pages deployment fails

**Symptoms**: Pipeline succeeds but pages job fails or docs not accessible

**Solutions**:

1. **Verify pages job configuration**:
   ```yaml
   pages:
     stage: deploy
     artifacts:
       paths:
         - public/  # MUST be named 'public/'
     only:
       - main
   ```

2. **Ensure `public/` directory**:
   ```yaml
   variables:
     ANODYSE_OUTPUT_DIR: public  # Generate directly to public/
   ```

3. **Enable GitLab Pages**:
   - Project Settings → Pages
   - Check Pages is enabled and view published URL

4. **Check access restrictions**:
   - Project Settings → Pages
   - Ensure Visibility allows access

---

### Issue: Variable substitution not working

**Symptoms**: `$CI_COMMIT_BRANCH` or other variables appear as literals in output

**Solutions**:

1. **Use correct syntax**:
   ```yaml
   # WRONG (literal $CI_COMMIT_BRANCH)
   - echo 'Branch: $CI_COMMIT_BRANCH'
   
   # RIGHT (variable expansion)
   - echo "Branch: $CI_COMMIT_BRANCH"  # Use double quotes
   ```

2. **Print variable to verify it's set**:
   ```yaml
   - echo "COMMIT_BRANCH=$CI_COMMIT_BRANCH"
   - echo "OUTPUT_DIR=$ANODYSE_OUTPUT_DIR"
   ```

3. **Set variables at correct scope**:
   ```yaml
   variables:           # Global scope
     GLOBAL_VAR: value
   
   job:
     variables:         # Job scope (overrides global)
       JOB_VAR: value
   ```

---

## Generic CI Systems

### Jenkins

**Issue**: Jenkinsfile not recognized

**Solutions**:
1. Verify Jenkinsfile in repository root
2. Check Jenkins has GitHub/GitLab connected
3. Scan repository from Jenkins UI

**Issue**: Permission denied during artifact upload

**Solutions**:
1. Run agent as user with write permissions to workspace
2. Verify `env.WORKSPACE` directory permissions

---

### Woodpecker CI

**Issue**: Docker image not found

**Solutions**:
1. Verify image exists: `docker pull python:3.11`
2. Check Woodpecker has Docker socket access: `/var/run/docker.sock`

**Issue**: Commands execute but steps appear to fail

**Solutions**:
1. Woodpecker exits on first non-zero exit code
2. Use `|| true` to ignore errors: `python -m anodyse ... || true`

---

### CircleCI

**Issue**: `You haven't validated your email address` error

**Solutions**:
1. Check email on CircleCI account settings
2. Click validation link in email
3. Retry pipeline

**Issue**: Workspace not shared between jobs

**Solutions**:
1. Use `persist_to_workspace` in first job:
   ```yaml
   - persist_to_workspace:
       root: .
       paths:
         - docs/
   ```

2. Use `attach_workspace` in later jobs

---

## Publishing

### GitHub Pages

**Issue**: Docs published to wrong URL or not updated

**Solutions**:
1. Check Settings → Pages for configured URL
2. Verify CNAME (custom domain) setup:
   ```bash
   cat CNAME
   # Should contain: docs.company.com
   ```
3. Clear browser cache or use incognito window

**Issue**: Private contents exposed

**Solutions**:
1. Verify repository privacy setting
2. GitHub Pages respects repository visibility
3. Add `.nojekyll` file if using non-Jekyll site

---

### GitLab Pages

**Issue**: 404 error on docs URL

**Solutions**:
1. Verify project is public or use group/instance Pages
2. Check pages job configuration has correct outputs
3. Verify artifacts expire_in is set appropriately

---

## Advanced Debugging

### Enable Verbose Logging

**GitHub Actions**:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
```

**GitLab CI**:
```yaml
variables:
  CI_DEBUG_TRACE: 'true'  # Shows all commands (CAUTION: exposes secrets!)
```

**Anodyse**:
```yaml
env:
  ANODYSE_VERBOSE: true
run: python -m anodyse --input-path ./playbooks --output-path ./docs
```

### Local Testing

Before running in CI, test locally:

```bash
# Setup
python -m venv /tmp/anodyse_test
source /tmp/anodyse_test/bin/activate

# Install and test
pip install anodyse
python -m anodyse \
  --input-path ./playbooks \
  --output-path /tmp/test-docs \
  --verbose

# Verify output
ls -la /tmp/test-docs/
cat /tmp/test-docs/index.md
```

### Comparing Logs

Keep logs from successful runs for reference:

1. Save workflow/pipeline output to file
2. Compare with failed run output
3. Identify differences (environment variables, timeouts, etc.)

---

## Getting Help

If you can't find your issue above:

1. **Check CI platform documentation**:
   - [GitHub Actions](https://docs.github.com/en/actions)
   - [GitLab CI](https://docs.gitlab.com/ee/ci/)

2. **Review Anodyse documentation**:
   - `python -m anodyse --help`
   - Main README: [Anodyse](https://github.com/example/anodyse)

3. **Enable debug logging** and review output carefully

4. **Test locally** to isolate CI-specific vs. Anodyse issues

5. **Create minimal reproducible example**:
   - Single playbook
   - Simple workflow/pipeline
   - Post output in issue

---

**Last Updated**: March 4, 2026  
**Need help?** See [CI_INTEGRATION.md](./CI_INTEGRATION.md) for main documentation
