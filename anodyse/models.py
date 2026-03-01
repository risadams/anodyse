"""Data models for parsed Ansible content."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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


@dataclass
class PlaybookData:
    """Parsed and annotated playbook content."""

    source_path: Path | str
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
    """Parameters from @param annotations. Format: [{"name": "var_name", "description": "var description"}, ...]"""

    warnings: list[str] = field(default_factory=list)
    """Warning messages from @warning annotations."""

    examples: list[str] = field(default_factory=list)
    """Usage examples from @example annotations (code blocks)."""

    doc_tags: list[str] = field(default_factory=list)
    """Documentation tags from @tag annotations (used for index categorization)."""


@dataclass
class RoleData:
    """Parsed and annotated role content."""

    source_path: Path | str
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
    """Parameters with @param annotations ONLY. Format: [{"name": "var_name", "description": "var description"}, ...]"""

    warnings: list[str] = field(default_factory=list)
    """Warning messages from @warning annotations."""

    examples: list[str] = field(default_factory=list)
    """Usage examples from @example annotations (code blocks)."""

    doc_tags: list[str] = field(default_factory=list)
    """Documentation tags from @tag annotations (used for index categorization)."""

    meta: dict[str, Any] = field(default_factory=dict)
    """Role metadata from meta/main.yml (dependencies, galaxy_info, etc.)."""


@dataclass
class IndexEntry:
    """Summary entry for index.md listing."""

    title: str
    """Item title (from @title or filename/dirname fallback)."""

    source_path: Path | str
    """Absolute path to source file or directory."""

    output_filename: str
    """Slugified output filename (e.g., 'deploy-app.md')."""

    description: str | None
    """One-line description from @description annotation (None if absent)."""

    doc_tags: list[str]
    """Documentation tags for categorization (from @tag annotations)."""

    item_type: str
    """Either 'playbook' or 'role' for index grouping."""
