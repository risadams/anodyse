"""Output file handler for rendered Markdown content."""

import re
from pathlib import Path


def write_output(
    content: str,
    output_path: str,
    no_backup: bool = False,
) -> None:
    """Write rendered Markdown content to output_path.

    - Slugify the filename: lowercase, hyphens only, no special characters
    - If output_path already exists and no_backup is False,
      back up as <filename>.bak before overwriting
    - Create the output directory if it does not exist
    - Always write UTF-8 encoded content

    Args:
        content: Markdown content to write
        output_path: Full path where file should be written
        no_backup: If True, skip creating .bak backup

    Raises:
        OSError: If file writing or directory creation fails
    """
    path = Path(output_path)

    # Slugify the filename
    stem = _slugify(path.stem)
    slugified_path = path.parent / f"{stem}{path.suffix}"

    # Create output directory if it doesn't exist
    slugified_path.parent.mkdir(parents=True, exist_ok=True)

    # Create backup if file exists and backups are enabled
    if slugified_path.exists() and not no_backup:
        backup_path = slugified_path.with_suffix(f"{slugified_path.suffix}.bak")
        try:
            if backup_path.exists():
                backup_path.unlink()
            slugified_path.rename(backup_path)
        except OSError as e:
            raise OSError(f"Failed to create backup: {e}") from e

    # Write the file with UTF-8 encoding
    try:
        slugified_path.write_text(content, encoding="utf-8")
    except OSError as e:
        raise OSError(f"Failed to write output file: {e}") from e


def _slugify(text: str) -> str:
    """Convert text to a slug suitable for filenames.

    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters (keep only alphanumerics and hyphens)
    - Collapse multiple hyphens into single

    Args:
        text: Text to slugify

    Returns:
        Slugified string
    """
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)

    # Remove all characters except alphanumerics and hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug or "untitled"
