# Configuration Templates Sample

This sample demonstrates comprehensive use of Jinja2 templates for application configuration management with Ansible.

## Overview

This sample shows how to:
- Use Jinja2 templates to generate configuration files
- Apply environment-specific settings
- Manage sensitive data (passwords, secrets)
- Deploy complex multi-format configurations (YAML, JSON, XML, INI, Properties)
- Generate email templates
- Configure web servers and proxies

## Directory Structure

```
config-templates/
├── configure-app.yml              # Main playbook with template tasks
├── templates/                     # All Jinja2 template files
│   ├── application.yml.j2         # Main app configuration (YAML)
│   ├── database.ini.j2            # Database config (INI)
│   ├── log4j2.xml.j2             # Logging config (XML)
│   ├── redis.conf.j2             # Cache config (Redis format)
│   ├── feature-flags.json.j2     # Feature flags (JSON)
│   ├── security.properties.j2    # Security settings (Java Properties)
│   ├── nginx-proxy.conf.j2       # NGINX config
│   ├── env.j2                    # Environment variables
│   ├── metrics.yml.j2            # Prometheus metrics (YAML)
│   └── emails/
│       ├── welcome.html.j2       # Welcome email template
│       └── password-reset.html.j2 # Password reset email
└── README.md
```

## Features Demonstrated

### Template Formats
- **YAML**: Application configuration with nested structures
- **XML**: Log4j2 logging configuration
- **JSON**: Feature flags with complex nesting
- **INI**: Database configuration
- **Properties**: Java-style security properties
- **Conf**: NGINX and Redis configuration
- **HTML**: Email templates with styling
- **Env**: Environment variable files

### Jinja2 Features Used

1. **Variable Substitution**
   ```jinja2
   port: {{ app_port }}
   host: {{ db_host }}
   ```

2. **Conditional Blocks**
   ```jinja2
   {% if environment == 'production' %}
   secure_mode: true
   {% else %}
   secure_mode: false
   {% endif %}
   ```

3. **Loops**
   ```jinja2
   {% for origin in cors_allowed_origins %}
   - {{ origin }}
   {% endfor %}
   ```

4. **Filters**
   ```jinja2
   enabled: {{ feature_flags.enable_api | lower }}
   log_level: {{ log_level | upper }}
   ```

5. **Default Values**
   ```jinja2
   db_version: {{ db_version | default('14') }}
   ```

6. **Expressions**
   ```jinja2
   log_level: "{{ 'DEBUG' if enable_debug else 'INFO' }}"
   ```

7. **Comments**
   ```jinja2
   {# This is a Jinja2 comment - won't appear in output #}
   ```

8. **Raw Blocks** (for nested templates)
   ```jinja2
   {% raw %}{{ user_email }}{% endraw %}
   ```

### Environment-Specific Configuration

The playbook demonstrates how different environments get different settings:

- **Production**: Enhanced security, stricter limits, monitoring enabled
- **Staging**: Similar to production but with relaxed security
- **Development**: Debug mode, verbose logging, relaxed security
- **Test**: Test-specific features, isolated data

### Security Best Practices

1. **Sensitive Data**: Uses environment variables for secrets
2. **File Permissions**: Restricts access to configuration files (0600, 0640)
3. **Backups**: Creates backups before modifying configs
4. **Validation**: Validates generated configs before applying
5. **No Logging**: Uses `no_log: true` for sensitive tasks

### Template Variables

The playbook demonstrates various variable types:
- Simple strings and numbers
- Booleans with conditional logic
- Lists and arrays
- Dictionaries/objects
- Ansible facts (ansible_date_time, ansible_host)
- Computed values

## Usage

### Generate Documentation

```bash
# Generate documentation for the configuration management playbook
python -m anodyse samples/config-templates/configure-app.yml

# Output to specific directory
python -m anodyse samples/config-templates/configure-app.yml -o docs/config/
```

### Expected Output

The documentation generator will produce:
- Complete playbook documentation with all tasks
- Parameter documentation for each template
- List of all generated configuration files
- Warning about sensitive data handling
- Usage examples for different environments

### Run the Playbook

```bash
# Development environment
ansible-playbook configure-app.yml -e "environment=development"

# Production with all features
ansible-playbook configure-app.yml \
  -e "environment=production" \
  -e "app_version=2.1.0" \
  -e "enable_monitoring=true" \
  -e "metrics_enabled=true"

# Staging with debug enabled
ansible-playbook configure-app.yml \
  -e "environment=staging" \
  -e "enable_debug=true"
```

## Annotations

This sample extensively uses anodyse annotations to document:
- Each template task with title and description
- Template parameters and their purpose
- File permissions and security warnings
- Configuration validation steps
- Handler behavior

## Template Best Practices Shown

1. **Clear Comments**: Every template includes generation metadata
2. **Conditional Sections**: Environment-specific blocks
3. **Whitespace Control**: Proper indentation and formatting
4. **Variable Documentation**: Comments explaining each variable
5. **Security Notes**: Warnings about sensitive data
6. **Validation**: Generated configs are validated
7. **Idempotency**: Templates generate consistent output
8. **Backup Strategy**: Automatic backups of existing configs

## Testing Templates

The playbook includes validation tasks that:
- Parse YAML files to ensure syntax is correct
- Validate JSON structure
- Check XML well-formedness
- Verify configuration file permissions
- Test generated NGINX config syntax

This ensures templates always produce valid, working configurations.
