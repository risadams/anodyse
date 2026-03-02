"""Output file handler for rendered Markdown content."""

from pathlib import Path

from .utils import slugify


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
    stem = slugify(path.stem)
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
