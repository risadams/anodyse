# Data Model: CI Workflow Integration for Anodyse

**Feature**: CI Workflow Integration Guide for Anodyse Users  
**Generated**: March 4, 2026  
**Context**: Anodyse is a Python CLI tool for generating Markdown documentation from Ansible playbooks/roles with structured annotations.

## Core Entities

### 1. Workflow/Pipeline Configuration

The declarative file that orchestrates CI/CD execution of Anodyse for documentation generation.

**GitHub Actions Variant** (`.github/workflows/*.yml`)
```yaml
Fields:
  - name: string                      # Descriptive workflow name
  - on: [push, pull_request, schedule, workflow_dispatch]  # Triggers
  - env: dict[string, string]         # Workflow-level environment variables
  - jobs: dict[string, Job]           # Jobs to execute
  
  Job:
    - runs-on: string                 # Runner type (ubuntu-latest, self-hosted)
    - steps: Step[]                   # Steps to execute
    - env: dict[string, string]       # Job-level environment variables
    - with: dict[string, string]      # Step inputs
    - outputs: dict[string, string]   # Job output values
    - artifacts: Upload[]             # Generated artifacts to preserve
    
  Step:
    - name: string                    # Step description
    - run: string or uses: string      # Inline script or action reference
    - env: dict[string, string]       # Step-level environment variables
    - if: string                      # Conditional execution
```

**GitLab CI Variant** (`.gitlab-ci.yml`)
```yaml
Fields:
  - variables: dict[string, string]   # Pipeline-level variables
  - stages: string[]                  # Execution stages
  - jobs: dict[string, Job]           # Jobs to execute
  
  Job:
    - stage: string                   # Which stage (build, test, deploy)
    - image: string                   # Docker image (if using Docker runner)
    - script: string[]                # Commands to execute
    - variables: dict[string, string] # Job-level environment variables
    - artifacts: Artifact             # Generated files to preserve
    - only/when: [push, merge_request, schedule]  # Triggers
    - timeout: string                 # Job timeout (e.g., "10 minutes")
    
  Artifact:
    - paths: string[]                 # File paths to preserve
    - expire_in: string               # How long to keep (e.g., "1 week")
    - reports: dict                   # Special artifact types (junit, etc.)
```

### 2. Anodyse CLI Invocation

Standard command-line interface contract for invoking Anodyse within CI/CD.

```
anodyse [GLOBAL_OPTIONS] <command> [COMMAND_OPTIONS]

Commands:
  - discover: Analyze playbooks/roles
  - parse: Extract Ansible definitions and annotations
  - render: Generate Markdown documentation

Global Options:
  --config FILE               # Configuration file path
  --verbose / --quiet         # Logging level
  --profile                   # Performance profiling output
  
Command Options (render):
  --input DIR / -i DIR        # Input playbooks/roles directory
  --output DIR / -o DIR       # Output documentation directory
  --template DIR / -t DIR     # Custom template directory (optional)
  --recursive / -r            # Recursively process subdirectories
  --fail-on-error             # Exit with code 1 on errors (default)
  --continue-on-error         # Exit with code 0 even on errors
  --parallel N                # Parallel processing threads (default: auto)
  --index                     # Generate index.md file (default: true)

Exit Codes:
  0: Success
  1: Critical error (missing input, parsing failure)
  2: Warning-level issues (undocumented items found)
```

### 3. Configuration Parameters (User-Configurable)

Variables that users provide via environment variables or workflow inputs.

```
ANODYSE_INPUT_DIR
  - Type: string (path)
  - Purpose: Directory containing Ansible playbooks/roles
  - Example: "./playbooks" or "./roles"
  - Default: "./" (current directory)
  - Platform variations: 
    - GitHub Actions: workflow input or environment variable
    - GitLab CI: CI/CD variable or .gitlab-ci.yml

ANODYSE_OUTPUT_DIR
  - Type: string (path)
  - Purpose: Directory where documentation will be written
  - Example: "./docs" or "./build/docs"
  - Default: "./docs"
  - Platform notes: Must exist or be created by workflow
  - Constraint: Should not be .gitignore'd if docs are version-controlled

ANODYSE_TEMPLATE_DIR
  - Type: string (path, optional)
  - Purpose: Directory containing custom Jinja2 templates
  - Example: "./templates/custom" or "https://github.com/org/templates"
  - Default: null (use built-in templates)
  - When provided: Overrides built-in templates
  - Platform notes: For mounted templates, ensure path is accessible in CI environment

PUBLISH_DOCS
  - Type: boolean
  - Purpose: Whether to publish generated docs after generation
  - Default: false
  - When true: Trigger platform-specific publication (GitHub Pages deploy, etc.)

DOCS_PUBLISH_TARGET
  - Type: string (enum)
  - Values: "github-pages" | "gitlab-pages" | "artifact-only" | "none"
  - Purpose: Where to publish documentation
  - Default: "artifact-only" (store as CI artifact)

CI_SCHEDULE
  - Type: string (cron expression)
  - Purpose: Periodic regeneration schedule
  - Example: "0 2 * * *" (daily at 2 AM UTC)
  - Used by: GitLab schedule triggers, GitHub schedule triggers
  
NOTIFY_ON_CHANGES
  - Type: boolean
  - Purpose: Whether to create PR/MR when docs change
  - Default: false
  - Use case: Pull docs updates into main branch automatically
```

### 4. Trigger Events

Events that cause the CI/CD workflow to execute.

```
Push Trigger
  - When: Code is pushed to repository
  - Branches: main, develop, or all branches (configurable)
  - Frequency: Per commit
  - Use case: Regenerate docs on every code change
  - GitHub: on: push: branches: [main]
  - GitLab: when: push

Pull Request / Merge Request Trigger
  - When: PR/MR is created or updated
  - Use case: Validate docs can be generated before merge
  - Frequency: Per PR/MR update
  - GitHub: on: pull_request: branches: [main]
  - GitLab: when: merge_request

Scheduled Trigger
  - When: Scheduled time/date is reached
  - Frequency: User-configurable (daily, weekly, monthly)
  - Use case: Periodic regeneration without commits
  - GitHub: on: schedule: - cron: '0 2 * * *'
  - GitLab: rules: - if: '$CI_PIPELINE_SOURCE == "schedule"'

Manual Trigger
  - When: User manually triggers via UI or API
  - Use case: On-demand regeneration
  - GitHub: on: workflow_dispatch
  - GitLab: when: manual
```

### 5. Error Handling Strategy

Response to errors during Anodyse invocation within CI/CD.

```
Critical Errors (exit code 1, workflow MUST fail)
  - Unparseable YAML (syntax errors in playbooks/roles)
  - Missing required input directory
  - Anodyse crashes or uncaught exception
  - Critical template rendering failure
  - Action: Fail the CI job, block merge, alert user

Warning Errors (exit code 2, workflow behavior configurable)
  - Undocumented plays or roles (missing @description annotations)
  - Incomplete metadata (missing tags, role titles)
  - Non-critical template warnings
  - Action: Generate docs with embedded error sections, optional job failure

Implementation:
  - Use `set -e` (shell) or GitHub Actions step failure conditions
  - Capture anodyse exit code
  - Emit structured error messages
  - Provide troubleshooting guidance in logs
```

### 6. Artifact Handling

Files generated and preserved by CI/CD system.

```
Primary Artifacts
  - Generated markdown files (*.md)
    - Ownership: Transferred to CI/CD system for publication/storage
    - Retention: Per platform (GitHub: 90 days default; GitLab: 30 days default)
    - Format: UTF-8 Markdown with Mermaid diagrams (if --graph flag used)

Optional Artifacts
  - index.md (always generated if --index flag used)
  - Build logs (for troubleshooting)
  - Performance profiling output (if --profile used)
  - Coverage reports (if supported)

Artifact Publication (platform-specific)
  - GitHub: Upload to gh-pages branch or use actions/deploy-pages
  - GitLab: Store in public_dir for gitlab pages job
  - Generic CI: Available for download from CI interface
```

### 7. Template Configuration

How custom Jinja2 templates are provided and mounted in CI environment.

```
Built-in Templates (Default)
  - Location: Anodyse package installation (/templates)
  - Use: No user action required
  - Behavior: Automatic

Custom Template from Repository
  - Location: ./templates/custom/ or /docs/templates
  - Mounting: Copy into workflow environment (GitHub: checkout step; GitLab: git clone)
  - Environment variable: ANODYSE_TEMPLATE_DIR=./templates/custom
  - Workflow handling:
    GitHub Actions:
      - Step 1: actions/checkout (brings repo into workspace)
      - Step 2: Run anodyse with --template ./templates/custom
      
    GitLab CI:
      - script: anodyse --template ./templates/custom (templates already available)

Custom Template from External Source
  - Location: GitHub repo, GitLab repo, or HTTP URL
  - Mounting: Clone/download in workflow before invoking anodyse
  - Implementation:
    GitHub Actions:
      - uses: actions/checkout (with repository parameter for template repo)
      - or: Run git clone https://... followed by anodyse invocation
    GitLab CI:
      - script: git clone https://... then anodyse --template
```

### 8. Publication Targets

Where generated documentation is published after generation.

```
GitHub Pages
  - Trigger: GitHub Actions workflow with GitHub token
  - Setup: Enable Pages in repo settings
  - Branch: Publish from "GitHub Actions" deployment
  - Action: uses: actions/deploy-pages@v2
  - URL: https://<org>.github.io/<repo>/
  - Deployment: Atomic (entire docs/ replaced on each run)

GitLab Pages
  - Trigger: GitLab CI job with pages: keyword
  - Setup: Enable Pages in project settings
  - Dir: public_dir must contain HTML/Markdown files
  - Job:
    pages:
      stage: deploy
      script: mkdir -p public && cp docs/*.md public/
      artifacts:
        paths:
          - public
  - URL: https://<group>.<org>.io/<project>/

Read the Docs
  - Trigger: Webhook on push to main branch
  - Setup: Connect project to Read the Docs
  - Source: GitHub or GitLab repository
  - Build: Read the Docs builds Sphinx/MkDocs from repo
  - Note: Requires source control integration, best for Python projects

Static Hosting (Netlify, Vercel, S3)
  - Trigger: Manual upload or CI integration
  - Upload: From CI artifact storage to hosting service
  - Authentication: API token/key in CI secrets
  - Deployment: Via CI action (e.g., deploy-netlify-action)
```

## Entity Relationships

```
Workflow ← schedules → Triggers (push, PR, schedule)
         ← configures → Anodyse CLI invocation
         ← receives → Configuration parameters (env vars)
         ← produces → Artifacts
         ← publishes → Publication targets

Anodyse CLI ← processes → Input (playbooks/roles)
            ← uses → Templates (built-in or custom)
            ← signals → Exit codes & errors
            ← outputs → Generated Markdown + metadata

Templates ← customizes → Output formatting
          ← mounted via → Volume mounts or file copies
          ← located in → Repository or external source

Artifacts ← stored in → CI artifact storage
          ← published to → GitHub Pages / GitLab Pages / hosting

Errors ← trigger → Job failure/success decision
       ← logged in → CI logs
       ← visible to → Developers (PR/MR UI)
```

## Validation Rules

```
Configuration Validation
  - ANODYSE_INPUT_DIR must exist and be readable
  - ANODYSE_OUTPUT_DIR must be writable
  - ANODYSE_TEMPLATE_DIR, if provided, must exist and contain *.j2 files
  - Triggers must be valid YAML (GitHub Actions / GitLab CI syntax)

Execution Validation
  - Anodyse exit code must be 0 (success) or optionally allow 2 (warnings)
  - Generated files must be valid UTF-8 Markdown
  - index.md must be generated if --index flag used
  - Artifacts must be accessible for download/publication

Error Handling Validation
  - Critical errors must cause job failure
  - Warnings must not cause job failure (unless --strict flag set)
  - Error messages must be actionable (include troubleshooting steps)
```

## Constraints & Assumptions

```
Assumptions
  - Anodyse CLI is installed or available in CI environment (via package manager or Docker image)
  - Git repository contains Ansible playbooks/roles at known paths
  - Users have write access to repository (for push and publication steps)
  - Sufficient CI/CD quota available for regular execution

Constraints
  - Fail-fast on critical errors (no partial documentation published)
  - No external network calls required (Anodyse runs fully offline)
  - Template customization does not allow arbitrary Python code execution
  - Documentation output size should not exceed CI artifact storage limits
  - Processing time should complete within CI job timeout (recommend 10-30 minutes)
```

---

**Status**: Data Model COMPLETE ✅  
**Dependencies**: Research (CI/CD patterns) ✅ Complete  
**Feeds into**: Contracts, Quickstart, Task Decomposition
