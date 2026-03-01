# Quickstart Guide: Core Parse-Extract-Render Pipeline

**Date**: 2026-03-01  
**Feature**: 001-core-pipeline  
**Branch**: `001-core-pipeline`

---

## Overview

This guide walks through implementing the Anodyse MVP from scratch. Follow the stages in order — each stage depends on the previous one.

**Estimated Total Time**: 3-5 days for experienced Python developer

---

## Prerequisites

### Environment Setup

```bash
# Clone repository and checkout feature branch
git clone https://github.com/risadams/anodyse.git
cd anodyse
git checkout 001-core-pipeline

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install development dependencies
pip install --upgrade pip
pip install click ruamel.yaml jinja2 pytest pytest-cov ruff
```

### Repository Structure

```text
anodyse/
├── anodyse/              # Main package (create this)
│   ├── __init__.py
│   ├── cli.py
│   ├── discovery.py
│   ├── parser.py
│   ├── extractor.py
│   ├── renderer.py
│   ├── output.py
│   ├── models.py
│   ├── exceptions.py
│   └── templates/
│       ├── playbook.md.j2
│       ├── role.md.j2
│       └── index.md.j2
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── pyproject.toml
├── README.md
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Stage 0: Project Scaffold (30 min)

### 1. Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "anodyse"
version = "0.1.0"
description = "Generate user-facing documentation from Ansible playbooks and roles"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.0",
    "ruamel.yaml>=0.18.0",
    "jinja2>=3.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

[project.scripts]
anodyse = "anodyse.cli:main"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"

[tool.coverage.run]
source = ["anodyse"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

### 2. Create Package Structure

```bash
# Create package directories
mkdir -p anodyse/templates
mkdir -p tests/{unit,integration,fixtures}

# Create __init__.py files
touch anodyse/__init__.py tests/__init__.py
touch tests/unit/__init__.py tests/integration/__init__.py

# Create module stubs
touch anodyse/{cli,discovery,parser,extractor,renderer,output,models,exceptions}.py
```

### 3. Create GitHub Actions CI

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, '0*-*']
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check anodyse/

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov=anodyse --cov-report=term-missing
```

---

## Stage 1: Data Models (1 hour)

**File**: `anodyse/models.py`

**Implementation**: Copy dataclass definitions from [data-model.md](data-model.md)

**Key Points**:
- Use Python stdlib `dataclasses` (no Pydantic)
- All fields fully type-hinted
- Use `field(default_factory=list)` for mutable defaults
- Add docstrings to each dataclass

**Test**: Create `tests/unit/test_models.py`

```python
from anodyse.models import TaskData, PlaybookData, RoleData, IndexEntry
from pathlib import Path

def test_task_data_creation():
    task = TaskData(name="Test Task", module="debug", args={"msg": "hello"})
    assert task.name == "Test Task"
    assert task.module == "debug"
    assert task.description is None  # Default

def test_playbook_data_defaults():
    playbook = PlaybookData(
        source_path=Path("test.yml"),
        title="Test",
        description=None,
        hosts="localhost"
    )
    assert playbook.tasks == []  # Default factory
    assert playbook.params == []
```

**Run Tests**:
```bash
pytest tests/unit/test_models.py -v
```

---

## Stage 2: Exceptions (15 min)

**File**: `anodyse/exceptions.py`

```python
"""Custom exceptions for Anodyse."""

class ParseError(Exception):
    """Raised when YAML parsing fails or structure is invalid."""
    pass

class AnnotationWarning(Warning):
    """Emitted when mandatory annotations are missing."""
    pass

class ManifestError(Exception):
    """Raised when .anodyse.yml manifest is invalid."""
    pass
```

**Test**: Create `tests/unit/test_exceptions.py`

```python
from anodyse.exceptions import ParseError, AnnotationWarning, ManifestError

def test_parse_error():
    with pytest.raises(ParseError, match="test error"):
        raise ParseError("test error")

def test_annotation_warning():
    with pytest.warns(AnnotationWarning):
        warnings.warn("missing @title", AnnotationWarning)
```

---

## Stage 3: Discovery Module (2 hours)

**File**: `anodyse/discovery.py`

**Key Functions**:
1. `discover(target: Path, config_path: Path | None) -> list[Path]`
2. `load_manifest(manifest_path: Path) -> dict`
3. `discover_playbooks(target: Path) -> list[Path]`
4. `discover_roles(target: Path) -> list[Path]`

**Implementation Notes**:
- Use `pathlib.Path.rglob()` for recursive search
- Check for `.anodyse.yml` in order: `--config` → target dir → repo root
- Emit warnings for non-existent manifest paths

**Test**: Create `tests/unit/test_discovery.py` + fixtures

```python
def test_discover_playbooks(tmp_path):
    # Create test fixture
    playbook = tmp_path / "test.yml"
    playbook.write_text("---\nhosts: localhost\ntasks: []")
    
    result = discover_playbooks(tmp_path)
    assert len(result) == 1
    assert result[0] == playbook
```

---

## Stage 4: YAML Parser (3 hours)

**File**: `anodyse/parser.py`

**Key Functions**:
1. `parse_playbook(path: Path) -> PlaybookData`
2. `parse_role(path: Path) -> RoleData`
3. `detect_type(path: Path) -> str`  # "playbook", "role", or "unknown"

**Implementation Notes**:
- Use `ruamel.yaml.YAML()` with round-trip mode
- Preserve comments for extractor
- Raise `ParseError` with line number on malformed YAML
- Return **dataclasses**, never raw dicts

**Test**: Create `tests/unit/test_parser.py` + fixtures

```bash
# Create fixture playbook
mkdir -p tests/fixtures
cat > tests/fixtures/playbook_simple.yml << 'EOF'
---
# @title Deploy Application
# @description Deploys the web application to production
hosts: webservers
tasks:
  - name: Install nginx
    apt:
      name: nginx
      state: present
EOF
```

```python
def test_parse_playbook_simple():
    path = Path("tests/fixtures/playbook_simple.yml")
    playbook = parse_playbook(path)
    
    assert playbook.hosts == "webservers"
    assert len(playbook.tasks) == 1
    assert playbook.tasks[0].name == "Install nginx"
    assert playbook.tasks[0].module == "apt"
```

---

## Stage 5: Annotation Extractor (3 hours)

**File**: `anodyse/extractor.py`

**Key Functions**:
1. `extract(data: PlaybookData | RoleData, source_text: str) -> PlaybookData | RoleData`
2. `extract_annotations(comment_lines: list[str]) -> dict`
3. `parse_param_annotation(value: str) -> dict`  # "var_name: description"

**Implementation Notes**:
- Regex pattern: `r'#\s*@(?P<tag>\w+)\s+(?P<value>.+)'`
- Scan playbook-level, task-level, and role var comments
- Emit `AnnotationWarning` for missing @title/@description
- Do not infer or generate missing values (set to None)

**Test**: Create `tests/unit/test_extractor.py`

```python
def test_extract_title_description():
    playbook = PlaybookData(
        source_path=Path("test.yml"),
        title=None,
        description=None,
        hosts="localhost"
    )
    
    source_text = """
    # @title My Playbook
    # @description A test playbook
    ---
    hosts: localhost
    """
    
    result = extract(playbook, source_text)
    assert result.title == "My Playbook"
    assert result.description == "A test playbook"
```

---

## Stage 6: Markdown Renderer (4 hours)

**File**: `anodyse/renderer.py`

**Key Functions**:
1. `render_playbook(data: PlaybookData, graph: bool) -> str`
2. `render_role(data: RoleData, graph: bool) -> str`
3. `render_index(entries: list[IndexEntry]) -> str`

**Implementation Notes**:
- Use Jinja2 `Environment` with `FileSystemLoader`
- Template lookup order: `.anodyse/templates/` → `anodyse/templates/`
- Validate user templates on startup (test render with sample data)
- See [template-variables.md](contracts/template-variables.md) for contract

**Templates**: Copy examples from [template-variables.md](contracts/template-variables.md) to `anodyse/templates/`

**Test**: Create `tests/unit/test_renderer.py`

```python
def test_render_playbook_with_description():
    playbook = PlaybookData(
        source_path=Path("test.yml"),
        title="Test Playbook",
        description="A test",
        hosts="localhost",
        tasks=[TaskData(name="Task 1", module="debug", args={})]
    )
    
    result = render_playbook(playbook, graph=False)
    
    assert "# Test Playbook" in result
    assert "A test" in result
    assert "Task 1" in result
```

---

## Stage 7: Output Handler (2 hours)

**File**: `anodyse/output.py`

**Key Functions**:
1. `write_output(content: str, output_path: Path, no_backup: bool) -> None`
2. `slugify(name: str) -> str`
3. `create_output_directory(path: Path) -> None`

**Implementation Notes**:
- Slugification: `re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')`
- Backup: rename existing file to `.bak` before overwrite
- UTF-8 encoding for all files

**Test**: Create `tests/unit/test_output.py`

```python
def test_slugify():
    assert slugify("Deploy App") == "deploy-app"
    assert slugify("role_web-server") == "role-web-server"
    assert slugify("My Playbook!!!") == "my-playbook"

def test_write_output_creates_backup(tmp_path):
    output_file = tmp_path / "test.md"
    output_file.write_text("old content")
    
    write_output("new content", output_file, no_backup=False)
    
    assert output_file.read_text() == "new content"
    assert (tmp_path / "test.md.bak").read_text() == "old content"
```

---

## Stage 8: CLI Entry Point (3 hours)

**File**: `anodyse/cli.py`

**Implementation**:

```python
import click
from pathlib import Path
import sys

@click.command()
@click.argument('target', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), default=Path('./docs'))
@click.option('--graph', is_flag=True, help='Include Mermaid flowchart diagrams')
@click.option('--no-backup', is_flag=True, help='Skip .bak file creation')
@click.option('--verbose', '-v', is_flag=True, help='Print detailed output')
@click.option('--format', type=click.Choice(['markdown']), default='markdown')
@click.option('--config', type=click.Path(exists=True, path_type=Path), default=None)
def main(target, output, graph, no_backup, verbose, format, config):
    """Generate Markdown documentation from Ansible playbooks and roles."""
    try:
        # Delegate to core modules
        items = discover(target, config)
        entries = []
        
        for item in items:
            # Parse →Execute → Render → Write
            ...
        
        # Generate index
        index_content = render_index(entries)
        write_output(index_content, output / "index.md", no_backup)
        
        sys.exit(0)
    
    except ParseError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    
    # Handle warnings → exit 2
```

**Test**: Create `tests/integration/test_cli.py`

```python
from click.testing import CliRunner
from anodyse.cli import main

def test_cli_single_playbook(tmp_path):
    # Create fixture playbook
    playbook = tmp_path / "test.yml"
    playbook.write_text("---\nhosts: localhost\ntasks: []")
    
    runner = CliRunner()
    result = runner.invoke(main, [str(playbook), '--output', str(tmp_path / 'docs')])
    
    assert result.exit_code == 0
    assert (tmp_path / 'docs' / 'index.md').exists()
```

---

## Stage 9: Tests (4 hours)

### Unit Tests (80% coverage minimum)

```bash
# Run unit tests with coverage
pytest tests/unit/ --cov=anodyse --cov-report=term-missing
```

**Required Unit Tests**:
- ✅ `test_models.py` — dataclass creation
- ✅ `test_parser.py` — YAML loading, malformed YAML, role detection
- ✅ `test_extractor.py` — annotation extraction, warnings
- ✅ `test_renderer.py` — template rendering, user template validation
- ✅ `test_discovery.py` — directory scan, manifest loading
- ✅ ` test_output.py` — slugification, backup, UTF-8 encoding

### Integration Tests

**File**: `tests/integration/test_pipeline.py`

```python
def test_full_pipeline_annotated_playbook(tmp_path):
    """End-to-end test: annotated playbook → rendered Markdown."""
    # Create annotated playbook fixture
    playbook = tmp_path / "deploy.yml"
    playbook.write_text("""
    # @title Deploy Application
    # @description Deploys the web app
    # @param app_version: Version to deploy
    ---
    hosts: webservers
    tasks:
      - name: Install nginx
        apt:
          name: nginx
    """)
    
    # Run CLI
    runner = CliRunner()
    result = runner.invoke(main, [str(playbook), '--output', str(tmp_path / 'docs')])
    
    assert result.exit_code == 0
    
    # Verify output
    output_file = tmp_path / 'docs' / 'deploy-application.md'
    assert output_file.exists()
    
    content = output_file.read_text()
    assert "# Deploy Application" in content
    assert "Deploys the web app" in content
    assert "app_version" in content
    assert "Install nginx" in content
```

### Fixtures

Create realistic test fixtures:

```bash
mkdir -p tests/fixtures
# playbook_annotated.yml — fully annotated
# playbook_unannotated.yml — no annotations
# role_sample/ — complete role structure
# manifest_include.yml — manifest with include list
# manifest_exclude.yml — manifest with exclude list
```

---

## Development Workflow

### Daily Development Loop

```bash
# 1. Run linter
ruff check anodyse/

# 2. Run tests
pytest -v

# 3. Check coverage
pytest --cov=anodyse --cov-report=html
open htmlcov/index.html

# 4. Manual CLI testing
pip install -e .
anodyse tests/fixtures/playbook_annotated.yml --output /tmp/test-docs --verbose
```

### Before Committing

```bash
# Format code
ruff format anodyse/ tests/

# Run full test suite
pytest --cov=anodyse --cov-report=term-missing

# Verify coverage ≥80%
coverage report --fail-under=80
```

---

## Troubleshooting

### Import Errors

```bash
# Ensure package installed in editable mode
pip install -e .
```

### Test Failures

```bash
# Run specific test with verbose output
pytest tests/unit/test_parser.py::test_parse_playbook_simple -vv

# Re-run only failed tests
pytest --lf
```

### YAML Comment Preservation Issues

```python
# Ensure using ruamel.yaml, not PyYAML
from ruamel.yaml import YAML
yaml = YAML()
yaml.preserve_quotes = True
```

---

## Milestone Checklist

- [ ] Stage 0: Project scaffold
  - [ ] pyproject.toml created
  - [ ] Package structure created
  - [ ] GitHub Actions CI configured
- [ ] Stage 1: Data models implemented and tested
- [ ] Stage 2: Exceptions defined and tested
- [ ] Stage 3: Discovery module working (directory scan + manifest)
- [ ] Stage 4: Parser extracts playbooks and roles correctly
- [ ] Stage 5: Extractor enriches dataclasses with annotations
- [ ] Stage 6: Renderer produces valid Markdown
- [ ] Stage 7: Output handler writes files with backups
- [ ] Stage 8: CLI accepts all options and delegates correctly
- [ ] Stage 9: All tests pass with ≥80% coverage
- [ ] CI pipeline green on Python 3.11 and 3.12

---

## Next Steps After MVP

Once all stages complete:

1. **Manual Testing**: Test with real Ansible playbooks from open-source projects
2. **Documentation**: Update README.md with usage examples
3. **PR Creation**: Open pull request from `001-core-pipeline` → `main`
4. **Code Review**: Address feedback, ensure constitution compliance
5. **Merge**: Merge to main and tag v0.1.0

---

## Resources

- **Spec**: [spec.md](spec.md)
- **Research**: [research.md](research.md)
- **Data Model**: [data-model.md](data-model.md)
- **Contracts**: [contracts/](contracts/)
- **Constitution**: [.specify/memory/constitution.md](../.specify/memory/constitution.md)

**Questions?** Refer to spec or research docs first. Open GitHub issues for clarifications.

---

**Last Updated**: 2026-03-01
