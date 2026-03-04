# Publishing Guide: Hosting Generated Ansible Documentation Online

After generating Ansible documentation with Anodyse in your CI/CD pipeline, you can publish it to various hosting platforms for team access and discoverability.

**Table of Contents**
- [Publishing Platforms](#publishing-platforms)
- [GitHub Pages](#github-pages)
- [GitLab Pages](#gitlab-pages)
- [Read the Docs](#read-the-docs)
- [Static Hosting](#static-hosting)
- [Comparison Matrix](#comparison-matrix)

---

## Publishing Platforms

### 1. GitHub Pages (Recommended for GitHub Users)

**Best For**: Open-source projects, public documentation, GitHub-hosted repositories  
**Cost**: Free  
**Setup Time**: 5-10 minutes  
**Maintenance**: Minimal (automatic via workflow)

#### Setup Instructions

**Step 1: Enable GitHub Pages**
- Go to repository Settings → Pages
- Select "Deploy from a branch" or "GitHub Actions"
- Choose source branch (typically `gh-pages` or `main`)

**Step 2: Add Workflow Step**

```yaml
      - name: Generate Documentation
        run: |
          python -m anodyse \
            --input-path ./playbooks \
            --output-path ./public
      
      - name: Deploy to GitHub Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

**Step 3: Configure Publishing**
- Docs will be published to `https://username.github.io/repo-name`
- Update repository description with documentation link

#### Features
- ✅ Free and included with GitHub
- ✅ No additional configuration needed
- ✅ Automatic updates on push
- ✅ Custom domain support
- ✅ HTTPS by default

#### Limitations
- ❌ Public repositories only (private requires GitHub Pro/Enterprise)
- ❌ Limited to 1 GB of storage
- ❌ 10 builds per hour limit

---

### 2. GitLab Pages

**Best For**: GitLab-hosted repositories, private projects, organizations with GitLab infrastructure  
**Cost**: Free (included with GitLab)  
**Setup Time**: 5-10 minutes  
**Maintenance**: Minimal (automatic via pipeline)

#### Setup Instructions

**Step 1: Configure `.gitlab-ci.yml`**

```yaml
stages:
  - generate
  - deploy

variables:
  ANODYSE_INPUT_DIR: ./playbooks
  ANODYSE_OUTPUT_DIR: public

generate_docs:
  stage: generate
  image: python:3.11-slim
  script:
    - pip install anodyse
    - python -m anodyse --input-path $ANODYSE_INPUT_DIR --output-path $ANODYSE_OUTPUT_DIR
  artifacts:
    paths:
      - public/
    expire_in: 30 days
  only:
    - main

pages:
  stage: deploy
  script:
    - echo "Publishing to GitLab Pages"
  artifacts:
    paths:
      - public/
  only:
    - main
  dependencies:
    - generate_docs
```

**Step 2: Push Configuration**
```bash
git add .gitlab-ci.yml
git commit -m "feat: Enable documentation publishing to GitLab Pages"
git push origin main
```

**Step 3: Verify Deployment**
- Go to Deployments → Environments
- Documentation will be at `https://projectname.gitlab.io/`

#### Features
- ✅ Included with GitLab (free and paid)
- ✅ Works with private projects
- ✅ Automatic deployment on push
- ✅ Custom domains supported
- ✅ HTTPS by default

#### Limitations
- ❌ Limited to GitLab users
- ❌ Self-hosted GitLab has different URL structure
- ❌ Storage quota depends on GitLab plan

---

### 3. Read the Docs

**Best For**: Open-source projects, Sphinx-based documentation, projects needing version management  
**Cost**: Free for open-source  
**Setup Time**: 15-20 minutes  
**Maintenance**: Medium (requires integration setup)

#### Setup Instructions

**Note**: Read the Docs expects Sphinx documentation. For Markdown-based Anodyse output, consider GitHub/GitLab Pages or static hosting instead.

If using Markdown, convert with tool like Sphinx + MyST:

**Step 1: Create Read the Docs Configuration**

`.readthedocs.yml`:
```yaml
version: 2
build:
  os: ubuntu-20.04
  tools:
    python: '3.11'

python:
  install:
    - requirements: docs/requirements.txt
    - path: .

sphinx:
  configuration: docs/conf.py

formats:
  - epub
  - pdf
```

**Step 2: Connect to Read the Docs**
- Create account at readthedocs.org
- Connect GitHub/GitLab account
- Import project

#### Features
- ✅ Professional documentation hosting
- ✅ Automatic version management
- ✅ Search across all versions
- ✅ PDF export included
- ✅ Free for open source

#### Limitations
- ❌ Setup complexity (requires Sphinx)
- ❌ Markdown integration requires MyST extension
- ❌ Paid plans for private projects
- ❌ Build limits on free tier

---

### 4. Static Hosting (S3, Netlify, Vercel, etc.)

**Best For**: Full control, custom domain, advanced features  
**Cost**: Pay-as-you-go (typically $5-20/month)  
**Setup Time**: 10-30 minutes  
**Maintenance**: Moderate (requires integration setup)

#### AWS S3 + CloudFront

**Step 1: Create S3 Bucket**
```bash
aws s3api create-bucket \
  --bucket my-anodyse-docs \
  --region us-east-1
```

**Step 2: Enable Static Website Hosting**
- S3 console → Bucket → Properties → Static website hosting
- Set index document to `index.md` or `index.html`

**Step 3: Add Workflow Step**

```yaml
      - name: Generate Documentation
        run: python -m anodyse --input-path ./playbooks --output-path ./docs
      
      - name: Deploy to S3
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: jakejarvis/s3-sync-action@master
        with:
          args: --acl public-read --follow-symlinks --delete
        env:
          AWS_S3_BUCKET: my-anodyse-docs
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: us-east-1
          SOURCE_DIR: docs
```

**Step 4: Configure CloudFront (Optional)**
- Create CloudFront distribution pointing to S3 bucket
- Enable default index document: `index.md`
- Set to HTTPS

#### Netlify

**Step 1: Create Deployment Key**
```yaml
      - name: Generate Documentation
        run: python -m anodyse --input-path ./playbooks --output-path ./docs
      
      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v2.0
        with:
          publish-dir: ./docs
          deploy-message: 'Deploy from GitHub Actions'
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

**Step 2: Get Credentials**
- Connect Netlify account to GitHub
- Create personal access token for CI/CD
- Store as GitHub Secrets

#### Features
- ✅ Full control over hosting
- ✅ Custom domain support
- ✅ Advanced caching options
- ✅ CDN distribution
- ✅ Analytics available

#### Limitations
- ❌ Ongoing costs
- ❌ More setup and configuration
- ❌ Requires AWS/cloud service knowledge
- ❌ May require technical support

---

## Comparison Matrix

| Feature | GitHub Pages | GitLab Pages | Read the Docs | S3+CloudFront | Netlify |
|---------|---|---|---|---|---|
| **Cost** | Free | Free | Free (OSS) | $5-20/mo | Free-$20/mo |
| **Setup** | 5 min | 10 min | 20 min | 15 min | 10 min |
| **Private Docs** | ❌ | ✅ (Pro) | ❌* | ✅ | ✅ |
| **Custom Domain** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Versioning** | Manual | Manual | ✅ | Manual | Manual |
| **Search** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **CDN** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HTTPS** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CI/CD Integration** | ✅ | ✅ | Manual | Workflow | Webhook |
| **Best For** | GitHub users | GitLab users | OSS projects | Enterprise | Full control |

*Read the Docs paid tier supports private projects with special configuration

---

## Configuration by Use Case

### Open-Source Project

**Recommended**: GitHub Pages (if on GitHub) or Read the Docs (with versioning)

```yaml
# .github/workflows/publish-docs.yml
name: Publish Documentation

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Generate Documentation
        run: python -m anodyse --input-path ./playbooks --output-path ./public
      
      - name: Deploy to GitHub Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

### Enterprise Organization

**Recommended**: Self-hosted GitLab Pages or static hosting (S3/Netlify)

```yaml
# .gitlab-ci.yml
deploy_docs:
  stage: deploy
  script:
    - python -m anodyse --input-path ./playbooks --output-path ./public
    - # Company-specific deployment (rsync, API call, etc.)
  only:
    - main
```

### Team Internal Use

**Recommended**: GitHub Pages (private), GitLab Pages (any), or static hosting

```yaml
# Internal documentation to GitHub Pages Enterprise
- Deploy to company-internal GitHub Pages
- Authenticate with company GitHub Enterprise credentials
- Restrict access via repository permissions
```

---

## Advanced Publishing Patterns

### Multiple Versions Publishing

```yaml
      - name: Generate Main Documentation
        run: python -m anodyse --input-path ./playbooks --output-path ./docs/latest
      
      - name: Generate Release Documentation
        if: startsWith(github.ref, 'refs/tags/')
        run: python -m anodyse --input-path ./playbooks --output-path ./docs/release/${{ github.ref_name }}
      
      - name: Deploy All Versions
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

### Conditional Publishing

```yaml
      - name: Publish to Production (main branch only)
        if: github.ref == 'refs/heads/main'
        run: aws s3 sync ./docs s3://my-docs-bucket/prod

      - name: Publish to Staging (any branch)
        if: github.ref != 'refs/heads/main'
        run: aws s3 sync ./docs s3://my-docs-bucket/staging/${{ github.branch }}
```

### Publishing with Custom Domain

#### GitHub Pages
1. Create `CNAME` file in documentation root:
```
docs.company.com
```

2. Configure DNS:
```
CNAME docs.company.com points to username.github.io
```

#### Netlify
1. Site Settings → Domain Management → Add custom domain
2. Update DNS to point to Netlify nameservers

---

## Troubleshooting

**GitHub Pages not updating**:
1. Verify `.github/workflows/` has your workflow file
2. Check Actions tab for workflow run status
3. Ensure publish_dir contains generated files
4. Check repository Settings → Pages for correct source

**GitLab Pages deployment fails**:
1. Verify `.gitlab-ci.yml` includes `pages:` job
2. Check that `public/` directory contains files
3. Verify pipeline runs successfully (CI/CD → Pipelines)
4. Check Deployments → Environments for errors

**CloudFront caching stale docs**:
1. Create invalidation: `aws cloudfront create-invalidation --distribution-id --paths '/*'`
2. Or shorten cache TTL in CloudFront settings
3. Or use versioning in paths: `/docs/v2/index.html`

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#publishing) for more issues.

---

## Next Steps

1. Choose publishing platform based on your needs
2. Follow setup instructions for your platform
3. Test documentation is accessible at published URL
4. Share documentation link with team
5. Configure team access control (if private)

**Learn More**
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitLab Pages Documentation](https://docs.gitlab.com/ee/user/project/pages/)
- [Read the Docs Documentation](https://docs.readthedocs.io)
- [Netlify Documentation](https://docs.netlify.com)
- [AWS S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)

---

**Last Updated**: March 4, 2026
