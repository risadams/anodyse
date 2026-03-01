# Enterprise Application Stack Sample

This is a comprehensive, production-ready sample demonstrating a complete enterprise application stack deployment using Ansible.

## Architecture

This sample deploys a three-tier application stack with:

- **Database Tier**: PostgreSQL cluster with streaming replication (3 nodes)
- **Application Tier**: Java-based application servers with auto-scaling support
- **Load Balancer Tier**: NGINX reverse proxy with SSL termination
- **Monitoring Tier**: Prometheus and Grafana for observability

## Directory Structure

```
enterprise-stack/
├── site.yml                          # Main orchestration playbook
├── roles/
│   ├── postgresql-cluster/          # Database cluster role
│   ├── app-server/                  # Application server role
│   ├── nginx-lb/                    # Load balancer role
│   └── prometheus-server/           # Monitoring role
└── README.md
```

## Features Demonstrated

### Multi-Playbook Orchestration
- Sequential deployment across multiple server tiers
- Pre-flight validation checks
- Post-deployment verification
- Coordinated service dependencies

### Complex Role Structure
Each role includes:
- `tasks/main.yml` - Main task definitions with comprehensive annotations
- `defaults/main.yml` - Default variables
- `handlers/main.yml` - Service handlers
- `vars/main.yml` - Role-specific variables
- `meta/main.yml` - Role metadata and dependencies

### Advanced Patterns
- Database clustering and replication
- Rolling updates with serialization
- Health checks and smoke tests
- Service discovery
- Log aggregation
- Metrics collection
- SSL/TLS certificate management

## Usage

### Prerequisites
- Ansible 2.10 or higher
- Target hosts with SSH access
- Valid SSL certificates for production deployments

### Generate Documentation

```bash
# Generate documentation for the entire stack
python -m anodyse samples/enterprise-stack/site.yml

# With custom output directory
python -m anodyse samples/enterprise-stack/site.yml -o docs/

# Include all role files
python -m anodyse samples/enterprise-stack/ -o docs/
```

### Expected Output
The documentation generator will produce:
- `index.md` - Overview of all playbooks
- `enterprise-application-stack-orchestrator.md` - Main playbook documentation
- Individual role documentation with task details
- Cross-references between dependent components

## Annotations Used

This sample demonstrates extensive use of anodyse annotations:
- `@title` - Clear, descriptive titles for playbooks and tasks
- `@description` - Detailed descriptions of functionality
- `@param` - Documentation of configurable parameters
- `@warning` - Critical warnings for operators
- `@example` - Usage examples
- `@tag` - Categorization tags

## Testing

Run the documentation generator on this sample to see:
- Multi-level documentation hierarchy
- Role dependency resolution
- Parameter documentation across roles
- Warning aggregation
- Example consolidation
