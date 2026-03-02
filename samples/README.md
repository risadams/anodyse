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
- Basic playbook structure with annotations
- Task-level documentation
- Parameters and warnings
- Handler configuration
- Conditional execution

Deploy an NGINX web server with SSL support:
```bash
anodyse samples/web-server/deploy-nginx.yml --output docs/
```

### 2. Database (`database/`)
**File:** `deploy-postgresql.yml`

Demonstrates:
- Database installation and configuration
- Security considerations
- User and database creation
- Password management warnings
- Tags for categorization

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
- Security best practices
- Multiple security domains
- Critical system modifications
- Compliance-oriented documentation
- Extensive parameter usage

Generate security hardening documentation:
```bash
anodyse samples/security-hardening/ --output docs/
```

### 5. Multi-Tier Application (`multi-tier/`)
**File:** `deploy-app-stack.yml`

Demonstrates:
- Multi-play playbooks
- Host group targeting
- Inter-play dependencies
- Complex deployment workflows
- Load balancer + app servers + database

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

- **@title**: Playbook and task titles
- **@description**: Detailed descriptions
- **@param**: Parameter documentation
- **@warning**: Important warnings and caveats
- **@example**: Usage examples
- **@tag**: Categorization tags

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
