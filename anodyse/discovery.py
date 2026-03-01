"""Playbook and role discovery from directories and manifest files."""

import warnings
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from .exceptions import ManifestError


def discover(target: str, config_path: str | None = None) -> list[str]:
    """Discover playbook and role paths from a target directory or manifest.

    Mode 1 (directory scan): recursively walks target, identifies:
      - Playbooks: .yml/.yaml files with a top-level `hosts:` key
      - Roles: directories containing tasks/main.yml
    Mode 2 (manifest): reads .anodyse.yml config, applies include/exclude.
      Manifest takes precedence over directory scan when present.
      Raises ManifestError on invalid schema.
      Emits a warning (not an error) for declared paths that do not exist.

    Args:
        target: Directory path to scan or playbook file path
        config_path: Optional explicit path to .anodyse.yml manifest

    Returns:
        List of resolved absolute paths to process.

    Raises:
        ManifestError: If manifest schema is invalid or malformed
    """
    target_path = Path(target).resolve()

    # Discover playbooks and roles via directory scan
    discovered = _scan_directory(target_path)

    # Check for manifest file (in priority order)
    manifest_path = _locate_manifest(target_path, config_path)

    if manifest_path:
        # Load and validate manifest
        manifest_data = _load_manifest(manifest_path)
        # Apply include/exclude filters
        discovered = _apply_manifest_filters(discovered, manifest_data, manifest_path.parent)

    return [str(p) for p in discovered]


def _scan_directory(target: Path) -> list[Path]:
    """Recursively scan directory for playbooks and roles.

    Returns:
        List of Path objects pointing to playbooks and role directories
    """
    results: list[Path] = []

    if target.is_file() and target.suffix in {".yml", ".yaml"}:
        # Single playbook file
        if _is_playbook(target):
            results.append(target)
        return results

    # Directory scan
    if not target.is_dir():
        return results

    for item in target.rglob("*"):
        # Skip hidden files/dirs
        if any(part.startswith(".") for part in item.parts):
            continue

        # Skip cache directories
        if "__pycache__" in item.parts:
            continue

        # Check for playbook files
        if item.is_file() and item.suffix in {".yml", ".yaml"}:
            if _is_playbook(item):
                results.append(item)

        # Check for role directories
        elif item.is_dir():
            if _is_role(item):
                results.append(item)

    return results


def _is_playbook(path: Path) -> bool:
    """Check if a YAML file is an Ansible playbook.

    A playbook must have a top-level `hosts:` key.
    """
    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        with open(path) as f:
            content = yaml.load(f)

        # Playbook is typically a list with dict entries that have 'hosts' key
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and "hosts" in item:
                    return True
        elif isinstance(content, dict) and "hosts" in content:
            return True
    except Exception:
        pass

    return False


def _is_role(path: Path) -> bool:
    """Check if a directory is an Ansible role.

    A role must contain tasks/main.yml.
    """
    return (path / "tasks" / "main.yml").exists()


def _locate_manifest(target: Path, config_path: str | None) -> Path | None:
    """Locate .anodyse.yml manifest file.

    Priority order:
        1. config_path (explicit path)
        2. target/.anodyse.yml
        3. Repository root/.anodyse.yml

    Returns:
        Path to manifest file, or None if not found
    """
    # Priority 1: explicit config path
    if config_path:
        return Path(config_path)

    # Priority 2: .anodyse.yml in target directory
    if target.is_dir():
        target_manifest = target / ".anodyse.yml"
        if target_manifest.exists():
            return target_manifest
    else:
        # If target is a file, check its parent directory
        target_manifest = target.parent / ".anodyse.yml"
        if target_manifest.exists():
            return target_manifest

    # Priority 3: .anodyse.yml in repo root (find .git directory)
    current = target if target.is_dir() else target.parent
    for parent in current.parents:
        if (parent / ".git").exists():
            repo_manifest = parent / ".anodyse.yml"
            if repo_manifest.exists():
                return repo_manifest

    return None


def _load_manifest(path: Path) -> dict[str, Any]:
    """Load and validate manifest schema.

    Expected schema:
        include: list[str] (optional)
        exclude: list[str] (optional)

    Returns:
        Parsed manifest dictionary

    Raises:
        ManifestError: If schema is invalid or YAML is malformed
    """
    try:
        yaml = YAML()
        with open(path) as f:
            data = yaml.load(f)

        if not isinstance(data, dict):
            raise ManifestError(f"Manifest must be a dictionary, got {type(data).__name__}")

        # Validate include/exclude fields if present
        if "include" in data and not isinstance(data["include"], list):
            raise ManifestError(f"'include' must be a list, got {type(data['include']).__name__}")

        if "exclude" in data and not isinstance(data["exclude"], list):
            raise ManifestError(f"'exclude' must be a list, got {type(data['exclude']).__name__}")

        return data
    except ManifestError:
        raise
    except Exception as e:
        raise ManifestError(f"Failed to parse manifest: {e}") from e


def _apply_manifest_filters(
    discovered: list[Path],
    manifest: dict[str, Any],
    manifest_dir: Path,
) -> list[Path]:
    """Apply include/exclude filters from manifest.

    Args:
        discovered: List of discovered Path objects
        manifest: Parsed manifest dictionary
        manifest_dir: Directory containing the manifest (for relative path resolution)

    Returns:
        Filtered list of Path objects
    """
    include_paths = manifest.get("include", [])
    exclude_paths = manifest.get("exclude", [])

    # If 'include' is specified, use only those paths
    if include_paths:
        result = []
        for include_path in include_paths:
            resolved = (manifest_dir / include_path).resolve()
            if resolved.exists():
                result.append(resolved)
            else:
                warnings.warn(
                    f"Declared path in include list does not exist: {include_path}",
                    UserWarning,
                )
        return result

    # If 'exclude' is specified, filter out those paths
    if exclude_paths:
        exclude_set = {(manifest_dir / p).resolve() for p in exclude_paths}
        result = [p for p in discovered if p not in exclude_set]

        # Warn for exclude paths that don't exist in discovered set
        for exclude_path in exclude_paths:
            resolved = (manifest_dir / exclude_path).resolve()
            if not resolved.exists():
                warnings.warn(
                    f"Declared path in exclude list does not exist: {exclude_path}",
                    UserWarning,
                )

        return result

    # No filters, return all discovered
    return discovered
