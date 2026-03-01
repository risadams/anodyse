# Data Model: Core Parse-Extract-Render Pipeline

**Date**: 2026-03-01  
**Feature**: 001-core-pipeline  
**Purpose**: Define all Python dataclasses for the MVP pipeline

---

## Overview

The data model consists of four primary dataclasses representing parsed and enriched Ansible content:

1. **TaskData** — Individual task representation
2. **PlaybookData** — Complete playbook with annotations
3. **RoleData** — Complete role with annotations
4. **IndexEntry** — Summary entry for index.md generation

All dataclasses follow Python stdlib `dataclasses` module (no Pydantic dependency per constitution).

---

## Core Dataclasses

### TaskData

Represents a single Ansible task with optional task-level annotations.

```python
from dataclasses import dataclass, field

@dataclass
class TaskData:
    """Single task within a playbook or role."""
    
    name: str
    """Task name (from 'name:' key in YAML)."""
    
    module: str
    """Ansible module name (e.g., 'apt', 'copy', 'shell')."""
    
    args: dict[str, Any]
    """Module arguments as key-value pairs."""
    
    description: str | None = None
    """Task-level @description annotation (None if absent)."""
    
    when: str | None = None
    """Conditional clause (from 'when:' key), used for Mermaid diagram branching."""
    
    loop: str | None = None
    """Loop clause (from 'loop:' or 'with_*' keys), used for diagram loop nodes."""
    
    tags: list[str] = field(default_factory=list)
    """Ansible tags applied to this task."""
```

**Usage**:
- Extracted by parser from `tasks`, `pre_tasks`, `post_tasks` lists
- Enriched by extractor with task-level `@description` from YAML comments
- Rendered in task summary section and Mermaid diagrams

**Validation Rules**:
- `name` and `module` are required (parser raises ParseError if missing)
- `when` and `loop` populated only if present in YAML
- `description` remains None if no `@description` annotation found (annotation-driven principle)

---

### PlaybookData

Represents a complete Ansible playbook with extracted annotations.

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class PlaybookData:
    """Parsed and annotated playbook content."""
    
    source_path: Path
    """Absolute path to source .yml file."""
    
    title: str | None
    """Playbook title from @title annotation or filename fallback."""
    
    description: str | None
    """Playbook description from @description annotation (None if absent)."""
    
    hosts: str
    """Target hosts pattern (from 'hosts:' key)."""
    
    pre_tasks: list[TaskData] = field(default_factory=list)
    """Tasks executed before roles (from 'pre_tasks:' section)."""
    
    tasks: list[TaskData] = field(default_factory=list)
    """Main tasks (from 'tasks:' section)."""
    
    post_tasks: list[TaskData] = field(default_factory=list)
    """Tasks executed after all tasks and roles (from 'post_tasks:' section)."""
    
    handlers: list[TaskData] = field(default_factory=list)
    """Handler tasks (from 'handlers:' section)."""
    
    roles: list[str] = field(default_factory=list)
    """Role names referenced in 'roles:' section (not followed in MVP)."""
    
    params: list[dict[str, str]] = field(default_factory=list)
    """Parameters from @param annotations.
    Format: [{"name": "var_name", "description": "var description"}, ...]
    """
    
    warnings: list[str] = field(default_factory=list)
    """Warning messages from @warning annotations."""
    
    examples: list[str] = field(default_factory=list)
    """Usage examples from @example annotations (code blocks)."""
    
    doc_tags: list[str] = field(default_factory=list)
    """Documentation tags from @tag annotations (used for index categorization)."""
```

**Usage**:
- Created by `parser.parse_playbook(path)` with structural data
- Enriched by `extractor.extract(playbook_data, source_text)` with annotations
- Consumed by `renderer.render_playbook(playbook_data, graph=...)` to produce Markdown

**Field Population Rules**:
- `source_path`: Populated by parser from input file path
- `title`: Populated by extractor from `@title` annotation; falls back to filename if None
- `description`: Populated by extractor; remains None if no `@description` (triggers AnnotationWarning)
- `hosts`: Required YAML field (parser raises ParseError if missing)
- Task lists: Populated by parser; empty lists if sections absent
- `params`, `warnings`, `examples`, `doc_tags`: Populated by extractor from annotations

---

### RoleData

Represents a complete Ansible role with extracted annotations.

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class RoleData:
    """Parsed and annotated role content."""
    
    source_path: Path
    """Absolute path to role directory."""
    
    title: str | None
    """Role title from @title annotation or directory name fallback."""
    
    description: str | None
    """Role description from @description annotation (None if absent)."""
    
    tasks: list[TaskData] = field(default_factory=list)
    """Tasks from tasks/main.yml."""
    
    defaults: dict[str, Any] = field(default_factory=dict)
    """Default variables from defaults/main.yml (full dict for reference)."""
    
    vars: dict[str, Any] = field(default_factory=dict)
    """Role variables from vars/main.yml (full dict for reference)."""
    
    params: list[dict[str, str]] = field(default_factory=list)
    """Parameters with @param annotations ONLY.
    Format: [{"name": "var_name", "description": "var description"}, ...]
    Per FR-011: only annotated params documented, unmarked defaults omitted.
    """
    
    warnings: list[str] = field(default_factory=list)
    """Warning messages from @warning annotations."""
    
    examples: list[str] = field(default_factory=list)
    """Usage examples from @example annotations (code blocks)."""
    
    doc_tags: list[str] = field(default_factory=list)
    """Documentation tags from @tag annotations (used for index categorization)."""
    
    meta: dict[str, Any] = field(default_factory=dict)
    """Role metadata from meta/main.yml (dependencies, galaxy_info, etc.)."""
```

**Usage**:
- Created by `parser.parse_role(path)` with structural data from role directory
- Enriched by `extractor.extract(role_data, source_texts)` with annotations from comments in tasks/, defaults/, vars/
- Consumed by `renderer.render_role(role_data, graph=...)` to produce Markdown

**Field Population Rules**:
- `source_path`: Populated by parser from role directory path
- `title`: Populated by extractor from `@title` annotation; falls back to directory name if None
- `description`: Populated by extractor; remains None if no `@description` (triggers AnnotationWarning)
- `tasks`: Populated by parser from tasks/main.yml
- `defaults`, `vars`: Full dicts loaded by parser for reference (not all documented)
- `params`: **Only variables with `@param` annotations** (extractor scans defaults/vars comments)
- `meta`: Populated by parser from meta/main.yml if present

**Key Difference from PlaybookData**:
- Roles have `defaults`/`vars` dicts but document only `@param`-annotated variables (per constitution annotation-driven principle and spec clarification #3)

---

### IndexEntry

Represents a summary entry for the generated index.md file.

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class IndexEntry:
    """Summary entry for index.md listing."""
    
    title: str
    """Item title (from @title or filename/dirname fallback)."""
    
    source_path: Path
    """Absolute path to source file or directory."""
    
    output_filename: str
    """Slugified output filename (e.g., 'deploy-app.md')."""
    
    description: str | None
    """One-line description from @description annotation (None if absent)."""
    
    doc_tags: list[str]
    """Documentation tags for categorization (from @tag annotations)."""
    
    item_type: str
    """Either 'playbook' or 'role' for index grouping."""
```

**Usage**:
- Created by output handler after processing each playbook/role
- Collected into list and passed to `renderer.render_index(entries)`
- Rendered as table or list in index.md with links to individual docs

**Field Population Rules**:
- `title`: From PlaybookData.title or RoleData.title (with fallback applied)
- `source_path`: Original input path
- `output_filename`: Slugified version of title
- `description`: First line of PlaybookData.description or RoleData.description (truncated if needed)
- `doc_tags`: Full list from PlaybookData.doc_tags or RoleData.doc_tags
- `item_type`: Set by handler based on parse result

---

## Dataclass Relationships

```text
PlaybookData
├── pre_tasks: list[TaskData]
├── tasks: list[TaskData]
├── post_tasks: list[TaskData]
└── handlers: list[TaskData]

RoleData
└── tasks: list[TaskData]

IndexEntry
└── (created from PlaybookData or RoleData after processing)
```

**Flow**:
1. Parser creates PlaybookData or RoleData with TaskData lists
2. Extractor enriches with annotations (modifies in place)
3. Renderer consumes enriched dataclass to produce Markdown
4. Output handler creates IndexEntry for each processed item
5. Renderer generates index.md from IndexEntry list

---

## Type Aliases and Enums

### Type Aliases

```python
from typing import TypeAlias

# Unified type for parser/extractor/renderer input
AnsibleContent: TypeAlias = PlaybookData | RoleData

# Path types for clarity
FilePath: TypeAlias = Path
DirectoryPath: TypeAlias = Path
```

### Enums

```python
from enum import Enum

class ExitCode(Enum):
    """CLI exit codes per FR-018."""
    SUCCESS = 0
    PARSE_ERROR = 1
    WARNING = 2

class ItemType(Enum):
    """Ansible content type."""
    PLAYBOOK = "playbook"
    ROLE = "role"
    UNKNOWN = "unknown"
```

---

## Validation and Constraints

### Required Fields

- **TaskData**: `name`, `module` are required (parser raises ParseError if absent)
- **PlaybookData**: `source_path`, `hosts` are required
- **RoleData**: `source_path`, `tasks` are required (empty list OK if no tasks/main.yml)
- **IndexEntry**: All fields required (fallbacks ensure title is never None)

### Optional Fields

- Annotation fields (`title`, `description`, `params`, `warnings`, `examples`, `doc_tags`) default to None or empty collections
- `when`, `loop` in TaskData default to None

### Immutability

- Dataclasses are mutable (default) to allow extractor enrichment
- After enrichment, dataclasses are read-only (renderer does not modify)

### Serialization

- Not required for MVP (no JSON/YAML output)
- If needed in v2, add `asdict()` method for JSON serialization

---

## Data Flow Summary

```text
Input YAML
    ↓
Parser (parser.py)
    ├── parse_playbook() → PlaybookData (structural only)
    └── parse_role() → RoleData (structural only)
    ↓
Extractor (extractor.py)
    └── extract() → enriched PlaybookData/RoleData (annotations added)
    ↓
Renderer (renderer.py)
    ├── render_playbook() → Markdown string
    ├── render_role() → Markdown string
    └── render_index() → index.md string
    ↓
Output Handler (output.py)
    ├── write_output() → .md files with backup
    └── collect -> list[IndexEntry]
```

---

## Next Steps

✅ Data model complete → proceed to **Phase 1: Contracts Definition**
