"""Markdown renderer for Ansible playbooks and roles using Jinja2."""

from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    PackageLoader,
    select_autoescape,
)

from .models import IndexEntry, PlaybookData, RoleData

# Cache for Jinja2 environment
_jinja_env: Environment | None = None


def _get_jinja_env() -> Environment:
    """Get or create Jinja2 environment with cascading template paths.

    Template lookup order:
        1. {cwd}/.anodyse/templates/
        2. anodyse/templates/ (package default)
    """
    global _jinja_env

    if _jinja_env is not None:
        return _jinja_env

    # Try to create loaders for custom and default templates
    loaders = []

    # Custom templates in .anodyse/templates/ (relative to cwd)
    custom_path = Path.cwd() / ".anodyse" / "templates"
    if custom_path.exists():
        loaders.append(FileSystemLoader(str(custom_path)))

    # Default templates from package
    loaders.append(PackageLoader("anodyse", "templates"))

    from jinja2 import ChoiceLoader

    loader = ChoiceLoader(loaders)

    _jinja_env = Environment(
        loader=loader,
        autoescape=select_autoescape(enabled_extensions=("html", "xml", "md")),
        keep_trailing_newline=True,
    )

    return _jinja_env


def render_playbook(data: PlaybookData, graph: bool = False) -> str:
    """Render a PlaybookData instance to a Markdown string.

    Required output sections (in order):
      1. Title
      2. Description (or undocumented notice)
      3. Parameters table
      4. Warnings section
      5. Usage Examples
      6. Task Summary
      7. Mermaid diagram (if graph=True)

    Args:
        data: PlaybookData instance with all fields populated
        graph: If True, include Mermaid flowchart diagram

    Returns:
        Rendered Markdown string (UTF-8)
    """
    env = _get_jinja_env()
    template = env.get_template("playbook.md.j2")

    context = {
        "title": data.title or Path(str(data.source_path)).stem,
        "description": data.description,
        "hosts": data.hosts,
        "params": data.params,
        "warnings": data.warnings,
        "examples": data.examples,
        "tasks": data.tasks,
        "pre_tasks": data.pre_tasks,
        "post_tasks": data.post_tasks,
        "handlers": data.handlers,
        "doc_tags": data.doc_tags,
        "graph": graph,
    }

    return template.render(context)


def render_role(data: RoleData, graph: bool = False) -> str:
    """Render a RoleData instance to a Markdown string.

    Same output sections as render_playbook.

    Args:
        data: RoleData instance with all fields populated
        graph: If True, include Mermaid flowchart diagram

    Returns:
        Rendered Markdown string (UTF-8)
    """
    env = _get_jinja_env()
    template = env.get_template("role.md.j2")

    context = {
        "title": data.title or Path(str(data.source_path)).name,
        "description": data.description,
        "params": data.params,
        "warnings": data.warnings,
        "examples": data.examples,
        "tasks": data.tasks,
        "defaults": data.defaults,
        "vars": data.vars,
        "doc_tags": data.doc_tags,
        "graph": graph,
    }

    return template.render(context)


def render_index(entries: list[IndexEntry]) -> str:
    """Render an index page listing all parsed playbooks and roles.

    Output: Markdown table with columns: Title | Tags | Description | Link

    Args:
        entries: List of IndexEntry instances

    Returns:
        Rendered Markdown string (UTF-8) containing index table
    """
    env = _get_jinja_env()
    template = env.get_template("index.md.j2")

    context = {
        "entries": entries,
    }

    return template.render(context)
