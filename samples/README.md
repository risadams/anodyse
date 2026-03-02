# Anodyse Sample Playbooks

This directory contains representative Ansible playbooks for demonstration and testing of the Anodyse documentation generator.

## Directory Structure

```
samples/
├── anodyse-template-overrides/ # Custom Anodyse output templates
├── missing-comments/     # Playbook without Anodyse annotations
├── web-server/          # NGINX web server deployment
├── database/            # PostgreSQL database setup
├── docker-app/          # Docker container deployment
├── security-hardening/  # System security hardening
└── multi-tier/          # Complete 3-tier application stack
```

## Sample Playbooks

### 1. Web Server (`web-server/`)
**File:** `deploy-nginx.yml`

Demonstrates:
- Task-level annotations (@task.description, @task.note, @task.warning, @task.tag)
- File-level and task-level TODO/FIXME tracking with author attribution
- Block prose comments for task context
- Inline prose comments on task definitions
- Handler configuration with annotations
- Conditional execution with security tags

Deploy an NGINX web server with SSL support:
```bash
anodyse samples/web-server/deploy-nginx.yml --output docs/
```

### 2. Database (`database/`)
**File:** `deploy-postgresql.yml`

Demonstrates:
- Comprehensive task-level documentation
- Security-focused warnings and notes
- TODO markers for planned improvements
- Database installation and configuration
- User and database creation
- Password management warnings with @task.warning
- Multiple categorization tags per task

Generate PostgreSQL deployment docs:
```bash
anodyse samples/database/ --output docs/
```

### 3. Docker Application (`docker-app/`)
**File:** `deploy-containers.yml`

Demonstrates:
- Container orchestration
- Docker Compose integration
- Network configuration
- Multi-container applications
- Monitoring stack deployment

Document container deployment:
```bash
anodyse samples/docker-app/deploy-containers.yml --output docs/ --graph
```

### 4. Security Hardening (`security-hardening/`)
**File:** `harden-system.yml`

Demonstrates:
- Security-focused task annotations with multiple warnings
- Compliance and audit categorization tags
- TODO/FIXME markers for security improvements
- Block prose explaining complex security controls
- Critical system modifications documentation
- CIS benchmark implementation notes
- Extensive parameter usage with security context

Generate security hardening documentation:
```bash
anodyse samples/security-hardening/ --output docs/
```

### 5. Multi-Tier Application (`multi-tier/`)
**File:** `deploy-app-stack.yml`

Demonstrates:
- Multi-play playbooks with task annotations
- TODO markers for deployment enhancements
- Inline comments on complex configurations
- Host group targeting with security notes
- Inter-play dependencies documentation
- Complex deployment workflows with warnings
- Load balancer + app servers + database stack
- Task categorization with multiple tags

Create comprehensive stack documentation:
```bash
anodyse samples/multi-tier/deploy-app-stack.yml --output docs/ --graph
```

### 6. Template Overrides (`anodyse-template-overrides/`)
**Files:** `templates/playbook.md.j2`, `templates/role.md.j2`, `templates/index.md.j2`

Demonstrates:
- Overriding built-in markdown templates with `/.anodyse/templates/`
- Keeping only the templates you want to customize
- Falling back to package defaults when a file is not overridden

Use custom templates:
```bash
mkdir -p .anodyse/templates
cp samples/anodyse-template-overrides/templates/*.j2 .anodyse/templates/
anodyse samples/web-server/deploy-nginx.yml --output docs/custom-templates --verbose
```

PowerShell (Windows):
```powershell
New-Item -ItemType Directory -Path .anodyse/templates -Force | Out-Null
Copy-Item samples/anodyse-template-overrides/templates/*.j2 .anodyse/templates/
anodyse samples/web-server/deploy-nginx.yml --output docs/custom-templates --verbose
```

### 7. Missing Required Comments (`missing-comments/`)
**File:** `deploy-unannotated.yml`

Demonstrates:
- A playbook that intentionally omits Anodyse `@` annotation comments
- Fallback markdown rendering behavior when metadata is missing

Generate docs from unannotated sample:
```bash
anodyse samples/missing-comments/deploy-unannotated.yml --output docs/samples --verbose
```

PowerShell (Windows):
```powershell
anodyse samples/missing-comments/deploy-unannotated.yml --output docs/samples --verbose
```

## Using These Samples

### Generate Documentation for All Samples

```bash
# Generate docs for all sample playbooks
anodyse samples/ --output docs/samples/

# With Mermaid diagrams
anodyse samples/ --output docs/samples/ --graph

# Verbose output
anodyse samples/ --output docs/samples/ --verbose
```

### Test Individual Samples

```bash
# Test NGINX deployment
cd samples/web-server
anodyse deploy-nginx.yml -o docs/

# Test with diagrams and verbose output
anodyse deploy-nginx.yml -o docs/ --graph --verbose
```

### Run Tests Against Samples

```bash
# Run test suite (includes CLI/integration coverage)
pytest tests/ -v
```

## Annotation Examples

These playbooks demonstrate all supported Anodyse annotations:

**Playbook-Level Annotations:**
- **@title**: Playbook title
- **@description**: Playbook description
- **@param**: Parameter documentation with defaults
- **@warning**: Important warnings and caveats
- **@example**: Usage examples with command-line syntax
- **@tag**: Categorization tags for playbook classification

**Task-Level Annotations (Feature 002):**
- **@task.description**: Task-specific description (replaces generic name)
- **@task.note**: Repeatable implementation notes and context
- **@task.warning**: Repeatable warnings for task execution
- **@task.tag**: Repeatable categorization tags for tasks

**Plain Prose Comments (Feature 002):**
- **Block comments**: Multi-line prose before task definition (fallback description)
- **Inline comments**: Comments on first-key line (rendered beneath task row)

**TODO/FIXME Tracking (Feature 002):**
- **File-level**: `# TODO: description` or `# FIXME: description` in playbook header
- **Task-level**: `# TODO: description` or `# FIXME: description` in task block comments
- **Author attribution**: `# TODO(username): description` or `# FIXME(username): description`

### Annotation Syntax Examples

```yaml
# Playbook-level annotations
# @title NGINX Web Server Deployment
# @description Deploy and configure NGINX with SSL/TLS support
# @param site_name Domain name for the website
# @warning SSL certificates must be provided separately
# @example ansible-playbook deploy-nginx.yml -e "site_name=example.com"
# @tag web-server
# @tag ssl
# TODO: Add Let's Encrypt certificate automation
# TODO(ops): Implement rate limiting configuration

---
- name: Deploy NGINX
  hosts: webservers
  tasks:
    # Block prose comment explaining the task context.
    # This fallback description is used when no @task.description exists.
    # @task.description: Install NGINX web server from distribution repositories
    # @task.note: Uses distro's default version for stability
    # @task.warning: Package repository must be configured first
    # @task.tag: install
    # @task.tag: web-server
    # TODO(devops): Consider using official NGINX repository
    - name: Install nginx  # inline comment appears beneath task row
      package:
        name: nginx
        state: present
```

## Feature Showcase

### Task Summary Tables
When tasks include @task.* annotations, Anodyse generates a comprehensive task summary table with columns:
- **Task** (name/module)
- **Description** (@task.description or block prose fallback)
- **Notes** (all @task.note entries)
- **Warnings** (all @task.warning entries)
- **Tags** (all @task.tag entries)

Inline prose comments appear beneath their corresponding task row.

### TODO/FIXME Section
When TODO or FIXME markers are detected, Anodyse generates a dedicated section with:
- **Location** (File or Task name)
- **Author** (from parenthetical attribution or "—")
- **TODO** (the marker text)

File-level TODOs appear at the top, followed by task-level TODOs.

### Index TODO Indicators
The generated index.md shows:
- ⚠️ prefix for playbooks/roles with TODOs
- TODO count in dedicated column
- Link to TODO section anchor in documentation

## Best Practices Demonstrated

1. **Comprehensive Documentation**: Every playbook and critical task is documented
2. **Parameter Documentation**: All variables are explained with @param
3. **Security Warnings**: Sensitive operations include @warning annotations
4. **Usage Examples**: Each playbook includes @example showing typical usage
5. **Idempotency**: All playbooks follow Ansible best practices
6. **Error Handling**: Proper use of conditionals and handlers

## Customization

Feel free to modify these samples for your own testing:

1. Copy a sample directory
2. Modify the playbook
3. Add/update annotations
4. Generate new documentation
5. Compare outputs

## Requirements

These samples assume:
- Target systems run Ubuntu/Debian (most checks use `ansible_os_family == "Debian"`)
- Ansible 2.9+ installed
- Appropriate inventory files configured
- Required privileges (become/sudo) available

## Contributing

To add new sample playbooks:

1. Create a new subdirectory under `samples/`
2. Add one or more annotated playbooks
3. Update this README with description
4. Ensure playbooks follow annotation standards
5. Test documentation generation

## License

These samples are provided as examples for the Anodyse project and follow the same license as the main project.
