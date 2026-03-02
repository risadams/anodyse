"""YAML parser for Ansible playbooks and roles."""

import re
from pathlib import Path
from typing import Any, Literal

from ruamel.yaml import YAML

from .exceptions import ParseError
from .models import PlaybookData, RoleData, TaskData

# Ansible task meta keys that are not actual modules
_TASK_META_KEYS = {
    "name",
    "when",
    "tags",
    "loop",
    "with_items",
    "block",
    "rescue",
    "always",
    "register",
    "failed_when",
    "changed_when",
    "async",
    "poll",
    "throttle",
    "vars",
    "environment",
    "connection",
    "remote_user",
    "become",
    "become_user",
    "no_log",
}

_TASK_HEADER_RE = re.compile(r"^\s*-\s*name\s*:\s*.*$", re.IGNORECASE)
_INLINE_COMMENT_RE = re.compile(r"^\s*-\s*name\s*:\s*.*?#\s*(.+)\s*$", re.IGNORECASE)


def _extract_task_comments_from_text(source_text: str) -> list[tuple[list[str], str | None]]:
    """Extract task block/inline comments from YAML source text in task order."""
    lines = source_text.splitlines()
    extracted: list[tuple[list[str], str | None]] = []

    for index, line in enumerate(lines):
        header_match = _TASK_HEADER_RE.match(line)
        if not header_match:
            continue

        # Inline comment on the task header line.
        inline_match = _INLINE_COMMENT_RE.match(line)
        inline_comment = inline_match.group(1).strip() if inline_match else None

        # Walk upwards collecting attached comment/blank lines.
        block_lines: list[str] = []
        back = index - 1
        while back >= 0:
            candidate = lines[back]
            stripped = candidate.strip()
            if stripped.startswith("#") or stripped == "":
                block_lines.append(candidate)
                back -= 1
                continue
            break

        block_lines.reverse()

        # Filter block_lines to check if there's any actual comment content
        # (not just blank lines). If only blanks, clear the list.
        has_comment = any(line.strip().startswith("#") for line in block_lines)
        if not has_comment:
            block_lines = []

        extracted.append((block_lines, inline_comment))

    return extracted


def _attach_task_comments_from_text(tasks: list[TaskData], source_text: str) -> None:
    """Attach raw block/inline comments to TaskData objects for extractor use."""
    extracted = _extract_task_comments_from_text(source_text)
    for task, (block_comments, inline_comment) in zip(tasks, extracted):
        setattr(task, "_raw_block_comments", block_comments)
        setattr(task, "_raw_inline_comment", inline_comment)


def detect_type(path: str) -> Literal["playbook", "role", "unknown"]:
    """Detect whether a path is a playbook file, role directory, or unknown.

    Args:
        path: File or directory path to check

    Returns:
        "playbook", "role", or "unknown"
    """
    p = Path(path).resolve()

    # Check for playbook file
    if p.is_file() and p.suffix in {".yml", ".yaml"}:
        try:
            if _has_hosts_key(p):
                return "playbook"
        except Exception:
            pass

    # Check for role directory
    if p.is_dir():
        if (p / "tasks" / "main.yml").exists():
            return "role"

    return "unknown"


def _has_hosts_key(path: Path) -> bool:
    """Check if a YAML file has a top-level 'hosts' key."""
    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        with open(path, encoding="utf-8") as f:
            content = yaml.load(f)

        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and "hosts" in item:
                    return True
        elif isinstance(content, dict) and "hosts" in content:
            return True
    except Exception:
        pass

    return False


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
    file_path = Path(path).resolve()

    if not file_path.exists():
        raise ParseError(f"File not found: {path}")

    if not file_path.is_file():
        raise ParseError(f"Path is not a file: {path}")

    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        source_text = file_path.read_text(encoding="utf-8")
        content = yaml.load(source_text)
    except Exception as e:
        raise ParseError(f"Failed to parse YAML file {path}: {e}") from e

    # Playbook is typically a list of play dicts, but single play is also valid
    plays = content if isinstance(content, list) else [content]

    # For MVP, we use the first play
    if not plays or not isinstance(plays[0], dict):
        raise ParseError(f"Invalid playbook format in {path}: expected play dictionary")

    play = plays[0]

    # Validate required 'hosts' key
    if "hosts" not in play:
        raise ParseError(f"Playbook missing required 'hosts' key: {path}")

    # Extract data
    hosts = play.get("hosts", "")

    # Parse task lists
    pre_tasks = _parse_tasks(play.get("pre_tasks", []) or [])
    tasks = _parse_tasks(play.get("tasks", []) or [])
    post_tasks = _parse_tasks(play.get("post_tasks", []) or [])
    handlers = _parse_tasks(play.get("handlers", []) or [])

    # Attach task-comment extraction from YAML source text
    _attach_task_comments_from_text(tasks, source_text)
    _attach_task_comments_from_text(pre_tasks, source_text)
    _attach_task_comments_from_text(post_tasks, source_text)
    _attach_task_comments_from_text(handlers, source_text)

    # Extract roles referenced
    roles_list = []
    if "roles" in play:
        for role in play.get("roles", []) or []:
            if isinstance(role, dict):
                roles_list.append(role.get("role", role.get("name", "")))
            elif isinstance(role, str):
                roles_list.append(role)

    return PlaybookData(
        source_path=file_path,
        title=None,  # Will be set by extractor
        description=None,  # Will be set by extractor
        hosts=hosts,
        pre_tasks=pre_tasks,
        tasks=tasks,
        post_tasks=post_tasks,
        handlers=handlers,
        roles=roles_list,
        params=[],  # Will be set by extractor
        warnings=[],  # Will be set by extractor
        examples=[],  # Will be set by extractor
        doc_tags=[],  # Will be set by extractor
    )


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
    role_path = Path(path).resolve()

    if not role_path.exists():
        raise ParseError(f"Role directory not found: {path}")

    if not role_path.is_dir():
        raise ParseError(f"Path is not a directory: {path}")

    # tasks/main.yml is required
    tasks_file = role_path / "tasks" / "main.yml"
    if not tasks_file.exists():
        raise ParseError(f"Role missing required tasks/main.yml: {path}")

    try:
        yaml = YAML()
        yaml.preserve_quotes = True

        # Load tasks (required)
        tasks_source_text = tasks_file.read_text(encoding="utf-8")
        tasks_content = yaml.load(tasks_source_text)
        tasks = _parse_tasks(tasks_content or [])

        # Attach task-comment extraction from YAML source text
        _attach_task_comments_from_text(tasks, tasks_source_text)

        # Load defaults (optional)
        defaults_file = role_path / "defaults" / "main.yml"
        defaults = {}
        if defaults_file.exists():
            with open(defaults_file, encoding="utf-8") as f:
                defaults = yaml.load(f) or {}

        # Load vars (optional)
        vars_file = role_path / "vars" / "main.yml"
        vars_dict = {}
        if vars_file.exists():
            with open(vars_file, encoding="utf-8") as f:
                vars_dict = yaml.load(f) or {}

        # Load meta (optional)
        meta_file = role_path / "meta" / "main.yml"
        meta = {}
        if meta_file.exists():
            with open(meta_file, encoding="utf-8") as f:
                meta = yaml.load(f) or {}

    except ParseError:
        raise
    except Exception as e:
        raise ParseError(f"Failed to parse role {path}: {e}") from e

    return RoleData(
        source_path=role_path,
        title=None,  # Will be set by extractor
        description=None,  # Will be set by extractor
        tasks=tasks,
        defaults=defaults,
        vars=vars_dict,
        params=[],  # Will be set by extractor
        warnings=[],  # Will be set by extractor
        examples=[],  # Will be set by extractor
        doc_tags=[],  # Will be set by extractor
        meta=meta,
    )


def _parse_tasks(tasks_content: Any) -> list[TaskData]:
    """Parse a list of task dicts into TaskData instances.

    Args:
        tasks_content: List of task dicts from YAML

    Returns:
        List of TaskData instances
    """
    tasks = []

    if not isinstance(tasks_content, list):
        return tasks

    for task_dict in tasks_content:
        if not isinstance(task_dict, dict):
            continue

        task_name = task_dict.get("name", "Unnamed task")

        # Find the module (typically all keys except meta keys)
        module = None
        module_args = {}

        for key, value in task_dict.items():
            if key not in _TASK_META_KEYS:
                module = key
                module_args = value if isinstance(value, dict) else {}
                break

        if not module:
            module = "unknown"

        task = TaskData(
            name=task_name,
            module=module,
            args=module_args,
            description=None,  # Will be set by extractor
            when=task_dict.get("when"),
            loop=task_dict.get("loop") or task_dict.get("with_items"),
            tags=task_dict.get("tags", []) or [],
        )
        tasks.append(task)

    return tasks
