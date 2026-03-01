"""CLI entry point for Anodyse."""

import sys
import warnings
from pathlib import Path
from typing import cast

import click

from .discovery import discover
from .exceptions import AnnotationWarning, ManifestError, ParseError
from .extractor import extract
from .models import IndexEntry, PlaybookData, RoleData
from .output import write_output
from .parser import detect_type, parse_playbook, parse_role
from .renderer import render_index, render_playbook, render_role


def _read_source_file(path: Path) -> str:
    """Read source file content as text."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


@click.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--output", "-o", default="./docs", type=click.Path(), help="Output directory for generated docs")
@click.option("--graph", is_flag=True, default=False, help="Include Mermaid flowchart diagrams")
@click.option("--no-backup", is_flag=True, default=False, help="Skip creating .bak files before overwrite")
@click.option("--config", type=click.Path(exists=True), default=None, help="Path to .anodyse.yml manifest")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Print detailed processing information")
@click.option("--format", "fmt", type=click.Choice(["markdown"]), default="markdown", help="Output format (markdown only)")
def main(
    target: str,
    output: str,
    graph: bool,
    no_backup: bool,
    config: str | None,
    verbose: bool,
    fmt: str,
) -> None:
    """Anodyse — Generate user-facing docs from Ansible playbooks and roles.

    TARGET can be a playbook file (.yml), role directory, or directory containing multiple playbooks/roles.
    """
    exit_code = 0
    has_warnings = False
    index_entries: list[IndexEntry] = []

    try:
        # Discover playbooks and roles
        discovered_paths = discover(target, config)

        if verbose:
            click.echo(f"✓ Discovered {len(discovered_paths)} playbook(s)/role(s)")

        if not discovered_paths:
            click.echo("No playbooks or roles found to document.", err=True)
            sys.exit(1)

        # Process each discovered path
        for path_str in discovered_paths:
            path = Path(path_str)

            if verbose:
                click.echo(f"Processing: {path}")

            try:
                # Detect type
                item_type = detect_type(str(path))

                if item_type == "unknown":
                    click.echo(f"⚠️  Skipping (not a playbook or role): {path}", err=True)
                    continue

                # Parse
                if item_type == "playbook":
                    data = parse_playbook(str(path))
                else:  # role
                    data = parse_role(str(path))

                # Read source file for extraction
                if isinstance(data, PlaybookData):
                    source_text = _read_source_file(Path(str(data.source_path)))
                else:
                    # For roles, read from tasks/main.yml
                    tasks_file = Path(str(data.source_path)) / "tasks" / "main.yml"
                    source_text = _read_source_file(tasks_file)

                # Extract annotations
                # Capture warnings during extraction
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    data = extract(data, source_text)

                    for warning in w:
                        if issubclass(warning.category, AnnotationWarning):
                            has_warnings = True
                            if verbose:
                                click.echo(f"  ⚠️  {warning.message}")

                # Render
                if isinstance(data, PlaybookData):
                    rendered = render_playbook(data, graph=graph)
                else:
                    rendered = render_role(data, graph=graph)

                # Write output
                output_filename = f"{_slugify(data.title or Path(str(data.source_path)).stem)}.md"
                output_path = Path(output) / output_filename

                write_output(rendered, str(output_path), no_backup=no_backup)

                if verbose:
                    click.echo(f"  ✓ Written: {output_filename}")

                # Create index entry
                description = None
                if data.description:
                    # First line only
                    description = data.description.split("\n")[0]

                entry = IndexEntry(
                    title=data.title or Path(str(data.source_path)).stem,
                    source_path=data.source_path,
                    output_filename=output_filename,
                    description=description,
                    doc_tags=data.doc_tags,
                    item_type=item_type,
                )
                index_entries.append(entry)

            except ParseError as e:
                click.echo(f"✗ Parse Error in {path}: {e}", err=True)
                exit_code = 1
                break
            except Exception as e:
                click.echo(f"✗ Unexpected error processing {path}: {e}", err=True)
                exit_code = 1
                break

        # Generate index
        if index_entries and exit_code == 0:
            index_content = render_index(index_entries)
            index_path = Path(output) / "index.md"
            write_output(index_content, str(index_path), no_backup=no_backup)

            if verbose:
                click.echo(f"✓ Generated index: index.md")

    except ManifestError as e:
        click.echo(f"✗ Manifest Error: {e}", err=True)
        sys.exit(1)
    except ParseError as e:
        click.echo(f"✗ Parse Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Unexpected error: {e}", err=True)
        sys.exit(1)

    # Determine final exit code
    if exit_code != 0:
        sys.exit(exit_code)
    elif has_warnings:
        if verbose or sys.stdout.isatty():
            # In interactive mode, show message
            click.echo("⚠️  Generated with warnings (missing mandatory annotations)", err=True)
        # Exit code 2 for warnings
        sys.exit(2)
    else:
        if verbose:
            click.echo(f"✓ Successfully generated documentation for {len(index_entries)} item(s)")
        sys.exit(0)


def _slugify(text: str) -> str:
    """Convert text to a slug suitable for filenames."""
    import re

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


if __name__ == "__main__":
    main()
