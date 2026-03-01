"""CLI entry point for Anodyse."""

import sys

import click


@click.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--output", "-o", default="./docs", type=click.Path(), help="Output directory for generated docs")
@click.option("--graph", is_flag=True, default=False, help="Include Mermaid flowchart diagrams")
@click.option("--no-backup", is_flag=True, default=False, help="Skip creating .bak files before overwrite")
@click.option("--config", type=click.Path(exists=True), default=None, help="Path to .anodyse.yml manifest")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Print detailed processing information")
@click.option("--format", "fmt", type=click.Choice(["markdown"]), default="markdown", help="Output format (markdown only)")
def main(target: str, output: str, graph: bool, no_backup: bool, config: str | None, verbose: bool, fmt: str) -> None:
    """Anodyse — Generate user-facing docs from Ansible playbooks and roles.

    TARGET can be a playbook file (.yml), role directory, or directory containing multiple playbooks/roles.
    """
    click.echo("Anodyse v0.1.0 - Not yet implemented", err=True)
    sys.exit(1)


if __name__ == "__main__":
    main()
