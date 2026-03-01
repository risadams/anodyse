"""YAML parser for Ansible playbooks and roles."""

from typing import Literal

from .models import PlaybookData, RoleData


def detect_type(path: str) -> Literal["playbook", "role", "unknown"]:
    """Detect whether a path is a playbook file, role directory, or unknown.

    Args:
        path: File or directory path to check

    Returns:
        "playbook", "role", or "unknown"
    """
    raise NotImplementedError("detect_type() not yet implemented")


def parse_playbook(path: str) -> PlaybookData:
    """Parse an Ansible playbook YAML file into a PlaybookData dataclass.

    Extracts: name, hosts, tasks (as TaskData), tags, vars, pre_tasks,
    post_tasks, and roles referenced. Annotations are NOT extracted here.

    Args:
        path: Path to playbook .yml file

    Returns:
        PlaybookData instance with structural data

    Raises:
        ParseError: If YAML is malformed or missing required fields
    """
    raise NotImplementedError("parse_playbook() not yet implemented")


def parse_role(path: str) -> RoleData:
    """Parse an Ansible role directory into a RoleData dataclass.

    Loads: tasks/main.yml, defaults/main.yml, vars/main.yml, meta/main.yml.
    Raises ParseError if tasks/main.yml is missing.

    Args:
        path: Path to role directory

    Returns:
        RoleData instance with tasks and variables

    Raises:
        ParseError: If tasks/main.yml is missing or malformed
    """
    raise NotImplementedError("parse_role() not yet implemented")
