"""Playbook and role discovery from directories and manifest files."""


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
    """
    raise NotImplementedError("discover() not yet implemented")
