"""Markdown renderer for Ansible playbooks and roles using Jinja2."""

from .models import IndexEntry, PlaybookData, RoleData


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
    raise NotImplementedError("render_playbook() not yet implemented")


def render_role(data: RoleData, graph: bool = False) -> str:
    """Render a RoleData instance to a Markdown string.

    Same output sections as render_playbook.

    Args:
        data: RoleData instance with all fields populated
        graph: If True, include Mermaid flowchart diagram

    Returns:
        Rendered Markdown string (UTF-8)
    """
    raise NotImplementedError("render_role() not yet implemented")


def render_index(entries: list[IndexEntry]) -> str:
    """Render an index page listing all parsed playbooks and roles.

    Output: Markdown table with columns: Title | Tags | Description | Link

    Args:
        entries: List of IndexEntry instances

    Returns:
        Rendered Markdown string (UTF-8) containing index table
    """
    raise NotImplementedError("render_index() not yet implemented")
