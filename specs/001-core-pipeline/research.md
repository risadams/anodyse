# Research: Core Parse-Extract-Render Pipeline

**Date**: 2026-03-01  
**Feature**: 001-core-pipeline  
**Purpose**: Technical research and decision rationale for MVP implementation

---

## Technology Choices

### 1. CLI Framework: Click vs Typer

**Decision**: Use **Click**

**Rationale**:
- Mature, stable library (v8.x) with extensive documentation
- Native support for exit codes, subcommands, and option validation
- Minimal dependencies (zero beyond Python stdlib)
- Typer adds type-first API but depends on Click internally + adds pydantic dependency
- Constitution mandates minimal dependencies — Click alone is sufficient

**Alternatives Considered**:
- Typer: Rejected due to additional pydantic dependency; Click's decorator API is sufficient for our single-command CLI
- argparse: Rejected due to verbose syntax and poor UX for help text formatting
- docopt: Rejected due to string-based command definition (less maintainable)

**Implementation Notes**:
- Use `@click.command()` with `@click.option()` and `@click.argument()`
- Exit codes via `sys.exit(0|1|2)` after command execution
- Verbose mode controlled by `click.echo()` with conditional logging

---

### 2. YAML Parsing: ruamel.yaml Comment Preservation

**Decision**: Use **ruamel.yaml** with round-trip mode

**Rationale**:
- Only Python YAML library that preserves comments during parsing
- Round-trip mode retains comment positions mapped to line numbers
- Enables annotation extraction without regex on raw file text
- Comments accessible via `.ca` (comment attribute) on YAML nodes

**Best Practices**:
```python
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True
data = yaml.load(Path("playbook.yml"))

# Access comments:
for key, value in data.items():
    if hasattr(value, "ca"):
        comment = value.ca.comment  # line comment
```

**Alternatives Considered**:
- PyYAML: Rejected — discards comments entirely (cannot extract annotations)
- pyyaml-include: Rejected — adds complexity for include handling we don't need in MVP

**Implementation Notes**:
- Parse YAML once; extract both structure and comments in single pass
- Pass comment strings to extractor module alongside dataclass
- Handle malformed YAML with Try/Except → raise ParseError with line number

---

### 3. Annotation Extraction: Regex Pattern Matching

**Decision**: Use compiled regex with named capture groups

**Rationale**:
- Annotation format is simple: `# @<tag> <value>`
- Regex pattern: `r'#\s*@(?P<tag>\w+)\s+(?P<value>.+)'`
- Compiled regex avoids re-compilation on every comment line
- Named groups improve readability over positional indexing

**Pattern Details**:
```python
import re

ANNOTATION_PATTERN = re.compile(
    r'#\s*@(?P<tag>title|description|param|warning|example|tag)\s+(?P<value>.+)',
    re.IGNORECASE
)

# For @param with name:description format
PARAM_PATTERN = re.compile(r'(?P<name>\w+):\s*(?P<desc>.+)')
```

**Edge Cases**:
- Multi-line annotations: Split on `\n`, match each line separately
- Special characters in values: Capture `.+` includes all characters; escape HTML/Markdown during rendering
- Missing values: If `.match()` fails, log warning and skip line

**Implementation Notes**:
- Scan comments at playbook level, task level, and within role var files
- Emit `AnnotationWarning` for missing mandatory tags (@title, @description)
- Store extracted annotations in dataclass fields (lists for repeatable tags)

---

### 4. Directory Discovery: os.walk vs pathlib.rglob

**Decision**: Use **pathlib.Path.rglob()**

**Rationale**:
- Modern, Pythonic API with better type safety
- `rglob('*.yml')` recursively matches YAML files
- `.is_file()` and `.is_dir()` methods cleaner than os.path checks
- Better cross-platform path handling (mitigates Windows path issues for future)

**Discovery Algorithm**:
```python
from pathlib import Path

def discover_playbooks(target: Path) -> list[Path]:
    """Find all .yml files with 'hosts:' key."""
    playbooks = []
    for yml_file in target.rglob('*.yml'):
        if yml_file.is_file():
            data = yaml.load(yml_file)
            if 'hosts' in data:
                playbooks.append(yml_file)
    return playbooks

def discover_roles(target: Path) -> list[Path]:
    """Find all directories with tasks/main.yml."""
    roles = []
    for tasks_file in target.rglob('tasks/main.yml'):
        role_dir = tasks_file.parent.parent  # tasks/main.yml -> role_dir
        if role_dir.is_dir():
            roles.append(role_dir)
    return roles
```

**Alternatives Considered**:
- os.walk: Rejected — less readable, requires manual path joining
- glob.glob: Rejected — limited pattern matching, no recursive flag in older Python

**Implementation Notes**:
- Check for `.anodyse.yml` manifest at target directory and repo root before discovery
- If manifest exists, use include/exclude lists instead of recursive scan
- Emit warning for each non-existent path in manifest

---

### 5. Filename Slugification: unicode-slug vs Custom

**Decision**: Use **custom slugification** (no external dependency)

**Rationale**:
- Requirement: lowercase, hyphens only, no special characters
- Simple transformation: `re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')`
- Avoids adding dependency for single function
- Handles edge cases: consecutive hyphens, leading/trailing hyphens

**Algorithm**:
```python
import re

def slugify(name: str) -> str:
    """Convert name to lowercase-hyphenated format."""
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
    return slug.strip('-')

# Examples:
# "Deploy App" -> "deploy-app"
# "role_web-server" -> "role-web-server"
# "My Playbook!!!" -> "my-playbook"
```

**Edge Cases**:
- Empty string after slugification: Use "unnamed-{hash}" fallback
- Duplicate slugs: Append `-1`, `-2`, etc. suffix
- Very long names: Truncate to 100 characters, ensure valid slug remains

**Implementation Notes**:
- Apply slugification in output handler before writing files
- Maintain mapping of original name → slug for index generation
- Include slug in dataclass or pass separately to renderer

---

### 6. Mermaid Flowchart Generation

**Decision**: Generate **simple sequence diagrams** for MVP

**Rationale**:
- Mermaid syntax: `graph TD` (top-down flowchart)
- Represent pre_tasks → tasks → post_tasks → handlers as linear sequence
- Conditionals shown as decision nodes: `{when: condition}`
- Loops shown as labeled subgraphs

**Mermaid Template Snippet**:
```jinja2
{% if graph %}
```mermaid
graph TD
    Start([Start])
    {% for task in pre_tasks %}
    PreTask{{ loop.index }}["{{ task.name }}"]
    {% endfor %}
    {% for task in tasks %}
    Task{{ loop.index }}["{{ task.name }}"]
    {% if task.when %}
    Task{{ loop.index }}_cond{{"{{ task.when }}"}}
    Task{{ loop.index }}_cond -->|yes| Task{{ loop.index }}
    {% endif %}
    {% endfor %}
    End([End])
    
    Start --> PreTask1
    {% for i in range(1, pre_tasks|length) %}
    PreTask{{ i }} --> PreTask{{ i+1 }}
    {% endfor %}
    PreTask{{ pre_tasks|length }} --> Task1
    {% for i in range(1, tasks|length) %}
    Task{{ i }} --> Task{{ i+1 }}
    {% endfor %}
    Task{{ tasks|length }} --> End
```
{% endif %}
```

**Alternatives Considered**:
- Full DAG with role dependencies: Deferred to v2 (Out of Scope per spec)
- Complex nested conditionals: Simplified to single-level conditional branches
- PlantUML: Rejected — less common, requires external renderer

**Implementation Notes**:
- Only generate when `--graph` flag is passed
- Conditionals extracted from `when` key in task dict
- Loops extracted from `loop` key; show as `[Loop: {{ loop }}]` label
- Handlers shown as separate subgraph at end

---

### 7. Template Validation Strategy

**Decision**: **Render test pass** with known dataclass

**Rationale**:
- No standard Jinja2 variable schema exists
- Validate by attempting render with sample dataclass
- If render succeeds → template compatible
- If TemplateError raised → template incompatible, emit warning (exit 2)

**Validation Algorithm**:
```python
from jinja2 import Template, TemplateError

def validate_template(template_path: Path, dataclass_type: type) -> bool:
    """Validate template by rendering with sample data."""
    try:
        template = Template(template_path.read_text())
        sample_data = create_sample_dataclass(dataclass_type)
        template.render(data=sample_data)
        return True
    except TemplateError as e:
        warnings.warn(f"Template {template_path} incompatible: {e}")
        return False

def create_sample_dataclass(dataclass_type):
    """Create minimal dataclass instance for validation."""
    # Populate all required fields with dummy values
    # PlaybookData: title="Test", description="Test", tasks=[], etc.
```

**Alternatives Considered**:
- Static AST analysis: Rejected — overly complex for MVP, no standard tool
- Require explicit variable declaration: Rejected — too rigid, breaks user flexibility

**Implementation Notes**:
- Validate user templates on CLI startup before processing
- If validation fails, fall back to default templates (graceful degradation)
- Log warning message with specific TemplateError details
- Exit code 2 if any template validation fails

---

### 8. Manifest Schema: YAML Structure for .anodyse.yml

**Decision**: Simple include/exclude lists

**Rationale**:
- Minimal config for MVP
- Two modes: include whitelist OR exclude blacklist (not both)
- Paths relative to manifest file location

**Schema**:
```yaml
# .anodyse.yml
include:
  - playbooks/deploy.yml
  - roles/webserver
  # Only these paths are processed

# OR

exclude:
  - playbooks/scratch.yml
  - playbooks/old/
  # All discovered items except these
```

**Validation Rules**:
- If both `include` and `exclude` present → error (mutually exclusive)
- If path does not exist → warning (not error, continue processing)
- If invalid YAML syntax → error (exit 1)
- Relative paths resolved relative to manifest file directory

**Implementation Notes**:
- Check for `.anodyse.yml` in target directory first, then repo root
- Use `Path.resolve()` to convert relative paths to absolute
- Emit warning for non-existent paths but continue discovery
- Manifest lookup order: `--config` flag → target dir → repo root

---

## Research Findings Summary

| Decision Area | Technology/Pattern | Rationale |
|---------------|-------------------|-----------|
| CLI Framework | Click | Minimal deps, stable, sufficient for single command |
| YAML Parsing | ruamel.yaml round-trip | Only library preserving comments for annotation extraction |
| Annotation Extraction | Compiled regex with named groups | Simple pattern, efficient, handles repeatable tags |
| Directory Discovery | pathlib.Path.rglob() | Modern API, clean syntax, better type safety |
| Filename Slugification | Custom function | No dependency needed, simple regex transform |
| Mermaid Diagrams | Simple sequence flowchart | MVP-scoped, linear flow with conditional branches |
| Template Validation | Render test with sample data | No standard schema, graceful degradation on failure |
| Manifest Structure | include/exclude lists | Zero-config default, opt-in control when needed |

**No unresolved NEEDS CLARIFICATION items remain.** All technical decisions documented with alternatives considered.

---

## Next Steps

✅ All research complete → proceed to **Phase 1: Data Model Design**
