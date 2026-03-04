# CI Platform Support Matrix

Comprehensive comparison of all supported CI/CD platforms for Anodyse integration.

---

## Platform Support Levels

| Platform | Status | Setup Time | Difficulty | Experience |
|---|---|---|---|---|
| **GitHub Actions** | ✅ Recommended | 5 min | Beginner | 10,000+ users |
| **GitLab CI/CD** | ✅ Recommended | 10 min | Beginner | 5,000+ users |
| **Generic/Shell** | ✅ Supported | 15 min | Intermediate | Works everywhere |
| **Jenkins** | ✅ Supported | 20 min | Intermediate | 1,000+ enterprises |
| **Woodpecker CI** | ✅ Supported | 15 min | Intermediate | Growing community |
| **CircleCI** | ✅ Supported | 15 min | Intermediate | 500+ users |
| **Travis CI** | ⚠️ Legacy | 10 min | Beginner | Declining |
| **Other** | 🔨 Custom | Variable | Advanced | Adapt generic patterns |

---

## Feature Comparison

| Feature | GitHub Actions | GitLab CI | Jenkins | Woodpecker | CircleCI | Travis |
|---|---|---|---|---|---|---|
| **Docker Support** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Shell/Bash** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Python Language** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Artifact Storage** | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Limited | ✅ Yes | ✅ Yes |
| **Environment Variables** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Secrets Management** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Scheduled Runs** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Manual Triggers** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Matrix Strategy** | ✅ Yes | ✅ Yes | ⚠️ Limited | ⚠️ Limited | ✅ Yes | ⚠️ Limited |
| **Self-Hosted Runners** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **On-Premise Deploy** | ⚠️ Enterprise | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ❌ No |

---

## Cost Comparison (Typical Anodyse Usage)

Based on 2 documentation generations per week (small projects):

| Platform | Monthly Cost | Annual Cost | Free Tier |
|---|---|---|---|
| **GitHub Actions** | $0 | $0 | Unlimited (public repos) |
| **GitLab CI/CD** | $0 | $0 | 400 min/month |
| **Jenkins** | $0 | $0 | Self-hosted (infrastructure cost) |
| **Woodpecker** | $0 | $0 | Self-hosted or <$50/month cloud |
| **CircleCI** | $0 | $0 | 6,000 credits/month (~300 builds) |
| **Travis CI** | $0 | $0 | Unlimited (legacy, declining support) |

**Detailed Build Costs**:

| Metric | GitHub | GitLab | CircleCI |
|---|---|---|---|
| Small build (2-3 min) | Free | 6-9 min quota | ~2 credits |
| Medium build (5-10 min) | Free | 12-18 min quota | ~4-8 credits |
| Large build (15-20 min) | Free | 45-60 min quota | ~12-16 credits |

---

## Platform-Specific Guides

### ✅ Recommendation: GitHub Actions (P1)

**When to Use**:
- Primary repository is on GitHub
- Public/open-source project (unlimited free minutes)
- Want easy setup with good documentation
- Prefer integrated experience with GitHub

**Setup**: 5 minutes  
**Complexity**: Beginner  
**Experience**: Most extensive docs, largest community

**Quick Start**:
```bash
cp docs/examples/workflows/github-actions-basic.yml .github/workflows/generate-docs.yml
# Customize paths
git add .github/workflows/generate-docs.yml && git commit -m "Add docs workflow"
```

**See**: [GitHub Actions Integration](./CI_INTEGRATION.md#github-actions-integration)

---

### ✅ Recommendation: GitLab CI/CD (P2)

**When to Use**:
- Primary repository is on GitLab.com or self-hosted GitLab
- Need more powerful conditional logic (rules)
- Want flexible runner options (Docker, Shell, Kubernetes)
- Prefer GitLab Pages for documentation hosting

**Setup**: 10 minutes  
**Complexity**: Beginner-Intermediate  
**Experience**: Comprehensive schema reference, growing community

**Quick Start**:
```bash
cp docs/examples/gitlab-ci-basic.yml .gitlab-ci.yml
# Customize variables
git add .gitlab-ci.yml && git commit -m "Add docs pipeline"
```

**See**: [GitLab CI/CD Integration](./CI_INTEGRATION.md#gitlab-cicd-integration)

---

### 🔧 Generic Pattern (All Platforms)

**When to Use**:
- Custom or proprietary CI system
- Multiple CI platforms
- Want best portability
- Prefer shell scripts over platform configs

**Setup**: 15-20 minutes  
**Complexity**: Intermediate  
**Experience**: Works with any CI system

**Quick Start**:
```bash
cp docs/examples/scripts/generate-docs.sh ./scripts/
chmod +x scripts/generate-docs.sh
# Add to your CI system to call: ./scripts/generate-docs.sh
```

**See**: [Generic CI Integration](./GENERIC_CI_INTEGRATION.md)

---

### Jenkins (Enterprise Standard)

**When to Use**:
- Organization standardized on Jenkins
- Need on-premise/self-hosted CI
- Have Jenkins infrastructure already built

**Setup**: 20 minutes  
**Complexity**: Intermediate  
**Experience**: Large enterprise user base

**Quick Start**:
```bash
# Copy Jenkinsfile to repository root
cp docs/examples/jenkins/Jenkinsfile ./Jenkinsfile
# Create Jenkins pipeline job pointed to this repository
```

**See**: [jenkins/Jenkinsfile](./examples/jenkins/Jenkinsfile)

---

### Woodpecker CI (Modern Open Source)

**When to Use**:
- Using Woodpecker cloud or self-hosted
- Want modern, container-first CI
-Prefer YAML over complex DSLs
- Open-source friendly

**Setup**: 15 minutes  
**Complexity**: Intermediate  
**Experience**: Growing Drone/Woodpecker community

**Quick Start**:
```bash
cp docs/examples/woodpecker/.woodpecker.yml ./
# Enable repository in Woodpecker UI
```

**See**: [woodpecker/.woodpecker.yml](./examples/woodpecker/.woodpecker.yml)

---

### CircleCI (Open Source with Free Tier)

**When to Use**:
- Using CircleCI cloud
- Need generous free tier (6,000 credits/month)
- Like CircleCI's web UI and debugging
- Good example of config.yml-based CI

**Setup**: 15 minutes  
**Complexity**: Intermediate  
**Experience**: Popular with startups, mid-size teams

**Quick Start**:
```bash
mkdir -p .circleci
cp docs/examples/circleci/config.yml .circleci/
# CircleCI will auto-detect and run
```

**See**: [circleci/config.yml](./examples/circleci/config.yml)

---

### Travis CI (Legacy - Not Recommended)

**Recommendation**: ⚠️ Archive status - use GitHub Actions instead

Travis CI is actively transitioning to "sustainable open source" model. While it still works, new projects should use:
- GitHub Actions (for GitHub)
- GitLab CI/CD (for GitLab)
- CircleCI (for Docker focus)

**Historical Note**: Travis was first major SaaS CI/CD platform before GitHub Actions.

**See**: [travis/.travis.yml](./examples/travis/.travis.yml)

---

## Decision Tree

```
How does your organization host code?

├─ GitHub
│  ├─ Public/open-source?
│  │  └─ YES → GitHub Actions ✅ (Recommended)
│  └─ Private commercial?
│     └─ YES → GitHub Actions (good free tier) or CircleCI
│
├─ GitLab Cloud (gitlab.com) or Self-Hosted?
│  └─ → GitLab CI/CD ✅ (Recommended)
│
├─ On-Premise/Custom?
│  ├─ Already have Jenkins?
│  │  └─ → Jenkins Jenkinsfile
│  ├─ Want modern container-first?
│  │  └─ → Woodpecker CI
│  └─ Want portable solution?
│     └─ → Generic/Shell Pattern
│
└─ Other platform (Bitbucket, Gitea, etc)?
   └─ → Generic/Shell Pattern
```

---

## Migration Guide

### Migrating Between Platforms

**GitHub Actions → GitLab CI/CD**:
1. Export GitHub Actions workflow to YAML
2. Convert step syntax to GitLab script syntax
3. Convert GitHub secrets to GitLab variables
4. Test on GitLab project

**GitLab CI/CD → GitHub Actions**:
1. Export GitLab pipeline to YAML
2. Convert script to steps format
3. Convert GitLab variables to GitHub secrets
4. Test on GitHub repository

**Custom CI → GitHub Actions/GitLab CI**:
1. Extract shell commands
2. Port to platform-specific syntax
3. Migrate environment variables
4. Update artifact handling

---

## Platform Maturity

| Platform | Maturity | Activity | Recommendation |
|---|---|---|---|
| GitHub Actions | Stable | Active | ✅ Use for new GitHub projects |
| GitLab CI/CD | Stable | Active | ✅ Use for new GitLab projects |
| Jenkins | Mature | Active | ✅ Use if already deployed |
| Woodpecker | Stable | Growing | ✅ Modern alternative to Jenkins |
| CircleCI | Mature | Active | ✅ Good general-purpose option |
| Travis CI | Declining | Limited | ⚠️ Archive - migrate away |

---

## Performance Benchmarks

Time to generate documentation (Anodyse only, not including setup):

| Repository Size | Time | CI Overhead |
|---|---|---|
| Small (20-50 files) | 1-2 min | 1-2 min |
| Medium (100-200 files) | 3-5 min | 1-2 min |
| Large (500+ files) | 10-15 min | 2-3 min |

**Total job time** = CI overhead + Anodyse execution

**Optimization Tip**: Use container caching to reduce CI overhead:
- Cache pip packages
- Cache Python virtual environment
- Reuse Docker images

---

## Troubleshooting by Platform

| Issue | GitHub | GitLab | Jenkins | Others |
|---|---|---|---|---|
| Python not found | Setup action | image: directive | Groovy config | Specify in config |
| Artifacts missing | upload-artifact action | artifacts: directive | archiveArtifacts | Platform-specific |
| Permissions denied | Secrets context | Protected variables | Jenkins credentials | Platform secrets |
| Timeout | Job timeout in UI | timeout: directive | executors timeout | Platform-specific |

---

## Supported Versions

| Platform | Minimum | Current | Tested |
|---|---|---|---|
| **Python** | 3.11 | 3.12 | 3.11, 3.12 |
| **GitHub Actions** | 2021 | 2024+ | Latest |
| **GitLab CI/CD** | 12.0 | 16.0+ | Latest |
| **Jenkins** | 2.150+ | 2.400+ | 2.300+ |
| **Woodpecker** | 0.15+ | 2.0+ | Latest |
| **CircleCI** | 2.0 | 2.1+ | Latest |

---

## See Also

- [CI Integration Guide](./CI_INTEGRATION.md) - Setup for major platforms
- [Generic CI Integration](./GENERIC_CI_INTEGRATION.md) - Custom platform patterns
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Solutions by platform
- [Platform Comparison](./PLATFORM_COMPARISON.md) - GitHub Actions vs GitLab
- [Contributing Guide](./CI_EXAMPLES_CONTRIBUTING.md) - Add new platforms

---

**Last Updated**: March 2026
**Anodyse Version**: 1.0+
