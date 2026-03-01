"""Output file handler for rendered Markdown content."""


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
    raise NotImplementedError("write_output() not yet implemented")
