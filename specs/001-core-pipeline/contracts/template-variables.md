# Jinja2 Template Contract

**Version**: 1.0.0 (MVP)  
**Feature**: 001-core-pipeline  
**Date**: 2026-03-01

---

## Overview

Anodyse uses Jinja2 templates to render Markdown documentation from dataclass instances. Users can override default templates by placing custom templates in `.anodyse/templates/` at the invocation directory.

This contract defines the **guaranteed template context variables** that all templates can expect.

---

## Template Locations

### Default Templates (built-in)

```text
anodyse/templates/
├── playbook.md.j2    # PlaybookData → Markdown
├── role.md.j2        # RoleData → Markdown
└── index.md.j2       # list[IndexEntry] → index.md
```

### User Templates (overrides)

```text
<invocation-directory>/.anodyse/templates/
├── playbook.md.j2    # Optional override
├── role.md.j2        # Optional override
└── index.md.j2       # Optional override
```

**Lookup Order**:
1. `.anodyse/templates/<template>.md.j2` (if exists)
2. `anodyse/templates/<template>.md.j2` (default fallback)

**Validation**: User templates validated on startup by test-rendering with sample data. If validation fails, warning emitted (exit code 2) and default template used.

---

## Playbook Template Contract: `playbook.md.j2`

### Context Variables

| Variable | Type | Guaranteed? | Description |
|----------|------|-------------|-------------|
| `data` | PlaybookData | ✅ Always | The complete playbook dataclass |
| `graph` | bool | ✅ Always | True if `--graph` flag passed |

### PlaybookData Fields

Access via `data.<field>`:

| Field | Type | Guaranteed? | Default | Description |
|-------|------|-------------|---------|-------------|
| `data.source_path` | Path | ✅ Always | | Absolute path to source .yml |
| `data.title` | str \| None | ⚠️ Maybe None | filename | From @title annotation or fallback |
| `data.description` | str \| None | ⚠️ Maybe None | None | From @description annotation (None if absent) |
| `data.hosts` | str | ✅ Always | | Host pattern (required YAML field) |
| `data.pre_tasks` | list[TaskData] | ✅ Always | `[]` | Pre-tasks (empty if none) |
| `data.tasks` | list[TaskData] | ✅ Always | `[]` | Main tasks (empty if none) |
| `data.post_tasks` | list[TaskData] | ✅ Always | `[]` | Post-tasks (empty if none) |
| `data.handlers` | list[TaskData] | ✅ Always | `[]` | Handlers (empty if none) |
| `data.roles` | list[str] | ✅ Always | `[]` | Role names (not followed in MVP) |
| `data.params` | list[dict] | ✅ Always | `[]` | Parameters from @param annotations |
| `data.warnings` | list[str] | ✅ Always | `[]` | Warnings from @warning annotations |
| `data.examples` | list[str] | ✅ Always | `[]` | Examples from @example annotations |
| `data.doc_tags` | list[str] | ✅ Always | `[]` | Tags from @tag annotations |

### TaskData Fields

Access via `task.<field>` when iterating `data.tasks`:

| Field | Type | Guaranteed? | Default | Description |
|-------|------|-------------|---------|-------------|
| `task.name` | str | ✅ Always | | Task name (required) |
| `task.module` | str | ✅ Always | | Ansible module name (required) |
| `task.args` | dict | ✅ Always | `{}` | Module arguments |
| `task.description` | str \| None | ⚠️ Maybe None | None | Task-level @description |
| `task.when` | str \| None | ⚠️ Maybe None | None | Conditional clause |
| `task.loop` | str \| None | ⚠️ Maybe None | None | Loop clause |
| `task.tags` | list[str] | ✅ Always | `[]` | Ansible tags |

### Template Requirements

**Must Include**:
1. Title section (use `data.title` or fallback to filename)
2. Description section (if None, show "⚠️ This playbook is undocumented.")
3. Parameters table (if `data.params` non-empty)
4. Warnings section (if `data.warnings` non-empty)
5. Examples section (if `data.examples` non-empty)
6. Task summary (iterate `data.tasks`, `data.pre_tasks`, `data.post_tasks`)
7. Mermaid diagram (if `graph == True`)

**Default Template Snippet**:

```jinja2
# {{ data.title or data.source_path.name }}

{% if data.description %}
{{ data.description }}
{% else %}
> ⚠️ **This playbook is undocumented.** Add a `# @description` annotation to document it.
{% endif %}

## Parameters

{% if data.params %}
| Parameter | Description |
|-----------|-------------|
{% for param in data.params %}
| `{{ param.name }}` | {{ param.description }} |
{% endfor %}
{% else %}
_No parameters documented._
{% endif %}

## Warnings

{% if data.warnings %}
{% for warning in data.warnings %}
> ⚠️ {{ warning }}
{% endfor %}
{% endif %}

## Usage Examples

{% if data.examples %}
{% for example in data.examples %}
```yaml
{{ example }}
```
{% endfor %}
{% else %}
_No usage examples provided._
{% endif %}

## Tasks

{% for task in data.tasks %}
{{ loop.index }}. **{{ task.name }}** (`{{ task.module }}`)
   {% if task.description %}{{ task.description }}{% endif %}
{% endfor %}

## Flow Diagram

{% if graph %}
```mermaid
graph TD
    Start([Start])
    {% for task in data.tasks %}
    Task{{ loop.index }}["{{ task.name }}"]
    {% endfor %}
    End([End])
    
    Start --> Task1
    {% for i in range(1, data.tasks|length) %}
    Task{{ i }} --> Task{{ i + 1 }}
    {% endfor %}
    Task{{ data.tasks|length }} --> End
```
{% endif %}
```

---

## Role Template Contract: `role.md.j2`

### Context Variables

| Variable | Type | Guaranteed? | Description |
|----------|------|-------------|-------------|
| `data` | RoleData | ✅ Always | The complete role dataclass |
| `graph` | bool | ✅ Always | True if `--graph` flag passed |

### RoleData Fields

Access via `data.<field>`:

| Field | Type | Guaranteed? | Default | Description |
|-------|------|-------------|---------|-------------|
| `data.source_path` | Path | ✅ Always | | Absolute path to role directory |
| `data.title` | str \| None | ⚠️ Maybe None | dirname | From @title annotation or fallback |
| `data.description` | str \| None | ⚠️ Maybe None | None | From @description annotation (None if absent) |
| `data.tasks` | list[TaskData] | ✅ Always | `[]` | Tasks from tasks/main.yml |
| `data.defaults` | dict | ✅ Always | `{}` | All default variables (for reference) |
| `data.vars` | dict | ✅ Always | `{}` | All role variables (for reference) |
| `data.params` | list[dict] | ✅ Always | `[]` | **Only @param-annotated variables** |
| `data.warnings` | list[str] | ✅ Always | `[]` | Warnings from @warning annotations |
| `data.examples` | list[str] | ✅ Always | `[]` | Examples from @example annotations |
| `data.doc_tags` | list[str] | ✅ Always | `[]` | Tags from @tag annotations |
| `data.meta` | dict | ✅ Always | `{}` | Role metadata from meta/main.yml |

### Template Requirements

**Must Include**:
1. Title section (role name)
2. Description section (with undocumented notice if None)
3. Parameters table (only `data.params` — annotated vars only, per FR-011)
4. Warnings section
5. Examples section
6. Task summary (from `data.tasks`)

**Note**: Unlike playbooks, roles document **only annotated parameters**. Full `defaults` and `vars` dicts available for reference but should not be auto-documented (annotation-driven principle).

---

## Index Template Contract: `index.md.j2`

### Context Variables

| Variable | Type | Guaranteed? | Description |
|----------|------|-------------|-------------|
| `entries` | list[IndexEntry] | ✅ Always | List of all processed items |

### IndexEntry Fields

Access via `entry.<field>` when iterating `entries`:

| Field | Type | Guaranteed? | Description |
|-------|------|-------------|-------------|
| `entry.title` | str | ✅ Always | Item title (never None, fallback applied) |
| `entry.source_path` | Path | ✅ Always | Absolute path to source file/directory |
| `entry.output_filename` | str | ✅ Always | Slugified filename (e.g., "deploy-app.md") |
| `entry.description` | str \| None | ⚠️ Maybe None | One-line description (None if absent) |
| `entry.doc_tags` | list[str] | ✅ Always | Documentation tags for categorization |
| `entry.item_type` | str | ✅ Always | Either "playbook" or "role" |

### Template Requirements

**Must Include**:
1. Title: "Ansible Documentation Index"
2. Table or list of all items with:
   - Link to output file: `[{{ entry.title }}]({{ entry.output_filename }})`
   - Type: playbook or role
   - Description (or "Undocumented" if None)
   - Tags (if non-empty)

**Default Template Snippet**:

```jinja2
# Ansible Documentation Index

## Playbooks

{% for entry in entries if entry.item_type == "playbook" %}
- [**{{ entry.title }}**]({{ entry.output_filename }}) {% if entry.doc_tags %}(Tags: {{ entry.doc_tags|join(", ") }}){% endif %}
  {{ entry.description or "_Undocumented_" }}
{% endfor %}

## Roles

{% for entry in entries if entry.item_type == "role" %}
- [**{{ entry.title }}**]({{ entry.output_filename }}) {% if entry.doc_tags %}(Tags: {{ entry.doc_tags|join(", ") }}){% endif %}
  {{ entry.description or "_Undocumented_" }}
{% endfor %}
```

---

## Template Validation

### Validation Process

1. On CLI startup, check for user templates in `.anodyse/templates/`
2. For each user template found:
   - Create sample dataclass (PlaybookData, RoleData, or IndexEntry list)
   - Attempt render with sample data
   - If `TemplateError` raised → validation fails

3. If validation fails:
   - Emit warning to stderr with specific error message
   - Fall back to default template
   - Set exit code 2 (warning with degraded output)

### Sample Data for Validation

```python
# Playbook validation
sample_playbook = PlaybookData(
    source_path=Path("/sample.yml"),
    title="Sample Playbook",
    description="Sample description",
    hosts="all",
    tasks=[TaskData(name="Sample Task", module="debug", args={})],
    params=[{"name": "var1", "description": "A variable"}],
    warnings=["Sample warning"],
    examples=["ansible-playbook sample.yml"],
    doc_tags=["sample", "test"]
)

# Role validation
sample_role = RoleData(
    source_path=Path("/sample-role"),
    title="Sample Role",
    description="Sample role description",
    tasks=[TaskData(name="Sample Task", module="debug", args={})],
    params=[{"name": "role_var", "description": "A role variable"}],
    warnings=[], examples=[], doc_tags=["sample"]
)

# Index validation
sample_entries = [
    IndexEntry(
        title="Sample Item",
        source_path=Path("/sample.yml"),
        output_filename="sample-item.md",
        description="Sample description",
        doc_tags=["sample"],
        item_type="playbook"
    )
]
```

---

## Common Template Patterns

### Safe Title Fallback

```jinja2
{{ data.title or data.source_path.stem }}
```

### Conditional Section

```jinja2
{% if data.warnings %}
## Warnings
{% for warning in data.warnings %}
> ⚠️ {{ warning }}
{% endfor %}
{% endif %}
```

### Task List with Optional Descriptions

```jinja2
{% for task in data.tasks %}
{{ loop.index }}. **{{ task.name }}** (`{{ task.module }}`)
   {% if task.description %}
   _{{ task.description }}_
   {% endif %}
{% endfor %}
```

### Tag List

```jinja2
{% if data.doc_tags %}
**Tags**: {{ data.doc_tags|join(", ") }}
{% endif %}
```

---

## Contract Guarantees

✅ **Guaranteed Stable**:
- All `✅ Always` fields in tables above
- `data` and `entries` variable names
- `graph` boolean flag
- Field types (str, list, dict, Path)

⚠️ **May Add (backward compatible)**:
- Additional optional fields in dataclasses
- New template context variables (e.g., `render_timestamp`)

❌ **Will Not Break**:
- Existing field names
- Existing field types
- Template variable names

---

## Template Testing

### Unit Test Example

```python
from jinja2 import Template
from anodyse.models import PlaybookData, TaskData
from pathlib import Path

def test_custom_template():
    template = Template(Path(".anodyse/templates/playbook.md.j2").read_text())
    
    data = PlaybookData(
        source_path=Path("test.yml"),
        title="Test",
        description="Test playbook",
        hosts="localhost",
        tasks=[TaskData(name="Test Task", module="debug", args={})]
    )
    
    result = template.render(data=data, graph=False)
    
    assert "# Test" in result
    assert "Test playbook" in result
    assert "Test Task" in result
```

---

**Contract Status**: ✅ Stable for MVP (v1.0.0)
