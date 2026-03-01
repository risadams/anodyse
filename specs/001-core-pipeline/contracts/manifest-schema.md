# Manifest Schema Contract: `.anodyse.yml`

**Version**: 1.0.0 (MVP)  
**Feature**: 001-core-pipeline  
**Date**: 2026-03-01

---

## Overview

The `.anodyse.yml` manifest file provides optional **explicit control** over playbook/role discovery. When present, it overrides the default recursive directory scan.

**Discovery Priority**:
1. Path specified via `--config` CLI flag (highest)
2. `.anodyse.yml` in `<target>` directory
3. `.anodyse.yml` in repository root
4. No manifest → default recursive scan (lowest)

**Philosophy**: Zero-config by default, opt-in override when needed (convention over configuration).

---

## Schema Definition

### YAML Structure

```yaml
# .anodyse.yml

# Option 1: Explicit include list (whitelist mode)
include:
  - playbooks/deploy.yml
  - playbooks/maintenance.yml
  - roles/webserver
  - roles/database

# Option 2: Exclusion list (blacklist mode)
exclude:
  - playbooks/scratch.yml
  - playbooks/experiments/
  - roles/deprecated

# Note: 'include' and 'exclude' are MUTUALLY EXCLUSIVE
# Specifying both is an error (exit code 1)
```

### Fields

| Field | Type | Required? | Description |
|-------|------|-----------|-------------|
| `include` | list[str] | No | Explicit list of paths to process (whitelist mode) |
| `exclude` | list[str] | No | List of paths to skip during discovery (blacklist mode) |

**Mutual Exclusivity**: Cannot specify both `include` and `exclude` in the same manifest. Parser raises error if both present.

---

## Include Mode (Whitelist)

### Behavior

When `include` list is present:
1. **Only** explicitly listed paths are processed
2. Paths can be:
   - Playbook files: `playbooks/deploy.yml`
   - Role directories: `roles/webserver`
   - Directories (recursively scanned): `playbooks/production/`

3. Non-existent paths emit **warning** (not error) and are skipped
4. Paths resolved relative to manifest file location

### Example

```yaml
include:
  - playbooks/deploy.yml           # Single playbook
  - playbooks/maintenance.yml      # Another playbook
  - roles/webserver                # Single role
  - playbooks/production/          # Recursively scan this directory
```

**Result**: Only these 3 files + 1 role + all items in `playbooks/production/` are documented. Everything else ignored.

### Use Cases

- Document only production playbooks (exclude experimental/scratch files)
- CI/CD pipelines with specific playbook subsets
- Multi-team repos where teams own specific directories

---

## Exclude Mode (Blacklist)

### Behavior

When `exclude` list is present:
1. Perform default recursive discovery (all `.yml` with `hosts:` key + all `tasks/main.yml` roles)
2. **Remove** any items matching exclude patterns from results
3. Paths can be:
   - Specific files: `playbooks/scratch.yml`
   - Directories: `roles/deprecated/` (excludes entire subtree)

4. Non-existent exclude paths silently ignored (no warning)
5. Paths resolved relative to manifest file location

### Example

```yaml
exclude:
  - playbooks/scratch.yml          # Skip this playbook
  - playbooks/experiments/         # Skip entire directory
  - roles/deprecated               # Skip this role
  - roles/wip/                     # Skip work-in-progress roles
```

**Result**: All discovered playbooks/roles **except** these paths are documented.

### Use Cases

- Exclude scratch files, experiments, or deprecated items
- Temporarily disable specific playbooks without deleting them
- Exclude vendor/third-party roles not needing documentation

---

## Path Resolution Rules

### Relative Paths

All paths in manifest are resolved **relative to the manifest file location**, not the current working directory.

**Example**:

```text
repo/
├── .anodyse.yml        # Manifest at root
├── playbooks/
│   ├── deploy.yml
│   └── scratch.yml
└── roles/
    └── webserver/
```

Manifest content:
```yaml
include:
  - playbooks/deploy.yml    # Resolved as repo/playbooks/deploy.yml
  - roles/webserver         # Resolved as repo/roles/webserver
```

### Absolute Paths

Absolute paths are allowed but **discouraged** (breaks portability):

```yaml
include:
  - /home/user/ansible/playbooks/deploy.yml  # Works but not portable
```

### Glob Patterns

**Not supported in MVP**. Future enhancement:

```yaml
# Future: glob patterns
include:
  - playbooks/prod-*.yml
  - roles/web-*
```

---

## Validation Rules

### Syntax Validation

Manifest must be **valid YAML**:
- Proper indentation (2 or 4 spaces)
- No tabs
- Quoted strings for special characters
- List syntax with `-` prefix

**Invalid Example**:
```yaml
include
  playbooks/deploy.yml  # Missing ':' and '-'
```

### Semantic Validation

1. **Mutual Exclusivity**: Cannot have both `include` and `exclude`
   ```yaml
   # INVALID
   include:
     - playbooks/deploy.yml
   exclude:
     - playbooks/scratch.yml
   ```
   **Error**: `Cannot specify both 'include' and 'exclude' in manifest`

2. **Non-empty Lists**: If `include` or `exclude` specified, must be non-empty list
   ```yaml
   # INVALID
   include: []
   ```
   **Error**: `Manifest 'include' list is empty`

3. **Type Validation**: Values must be strings (paths)
   ```yaml
   # INVALID
   include:
     - 123  # Not a string
   ```
   **Error**: `Manifest 'include' must be list of strings`

---

## Error Handling

### Parse Errors (Exit Code 1)

**Triggers**:
- Invalid YAML syntax
- Both `include` and `exclude` present
- Empty include/exclude lists
- Non-string values in lists

**Example Error Messages**:

```text
Error: Failed to parse .anodyse.yml manifest:
  YAML syntax error at line 5: expected ':' but found '-'
Exit code: 1
```

```text
Error: Invalid .anodyse.yml manifest:
  Cannot specify both 'include' and 'exclude' lists
Exit code: 1
```

### Warnings (Exit Code 2)

**Triggers**:
- Non-existent path in `include` list (skip and continue)

**Example Warning Message**:

```text
Warning: Path 'playbooks/missing.yml' in manifest does not exist (skipped)
Exit code: 2 (if no other errors)
```

### No Errors

If manifest is valid and all paths exist, processing continues normally with exit code 0.

---

## Discovery Algorithm

### With Include List

```python
def discover_with_include(manifest_path: Path, include_list: list[str]) -> list[Path]:
    """Discover only explicitly included paths."""
    items = []
    manifest_dir = manifest_path.parent
    
    for path_str in include_list:
        path = (manifest_dir / path_str).resolve()
        
        if not path.exists():
            warnings.warn(f"Path '{path_str}' in manifest does not exist (skipped)")
            continue
        
        if path.is_file():
            # Check if it's a valid playbook
            if is_playbook(path):
                items.append(path)
        elif path.is_dir():
            # Recursively scan directory
            items.extend(discover_in_directory(path))
    
    return items
```

### With Exclude List

```python
def discover_with_exclude(target_dir: Path, exclude_list: list[str]) -> list[Path]:
    """Discover all items except excluded paths."""
    all_items = discover_in_directory(target_dir)  # Default discovery
    manifest_dir = target_dir  # Or repo root if manifest there
    
    # Resolve exclude patterns
    excluded = set()
    for path_str in exclude_list:
        path = (manifest_dir / path_str).resolve()
        excluded.add(path)
        
        # If path is directory, exclude all children
        if path.is_dir():
            for child in path.rglob('*'):
                excluded.add(child)
    
    # Filter out excluded items
    return [item for item in all_items if item not in excluded]
```

---

## Examples

### Example 1: Production-Only Whitelist

**Scenario**: Large repo with `production/`, `staging/`, and `experiments/` directories. Only document production.

**Manifest** (`.anodyse.yml` at repo root):
```yaml
include:
  - playbooks/production/
  - roles/production/
```

**Command**:
```bash
anodyse . --output ./docs
```

**Result**: Only items in `playbooks/production/` and `roles/production/` documented.

---

### Example 2: Exclude Scratch Files

**Scenario**: Document all playbooks except scratch/experimental files.

**Manifest** (`.anodyse.yml` at repo root):
```yaml
exclude:
  - playbooks/scratch.yml
  - playbooks/test-*.yml   # Note: glob not supported in MVP, treated as literal
  - roles/deprecated/
  - roles/wip/
```

**Command**:
```bash
anodyse ./playbooks --output ./docs
```

**Result**: All playbooks in `./playbooks` except `scratch.yml`, and all roles except those in `deprecated/` and `wip/`.

---

### Example 3: Explicit Manifest Path

**Scenario**: Manifest not in default location, specify explicitly.

**Manifest** (`configs/anodyse-prod.yml`):
```yaml
include:
  - ../playbooks/deploy.yml
  - ../playbooks/rollback.yml
  - ../roles/webserver
```

**Command**:
```bash
anodyse ./playbooks --config configs/anodyse-prod.yml --output ./docs
```

**Result**: Only specified playbooks and role documented, paths resolved relative to `configs/` directory.

---

## Testing the Manifest

### Unit Test Example

```python
from pathlib import Path
from anodyse.discovery import load_manifest, validate_manifest

def test_include_manifest():
    manifest_path = Path("tests/fixtures/manifest_include.yml")
    manifest = load_manifest(manifest_path)
    
    assert "include" in manifest
    assert len(manifest["include"]) == 3
    assert "playbooks/deploy.yml" in manifest["include"]

def test_invalid_manifest_both_include_exclude():
    manifest_path = Path("tests/fixtures/manifest_invalid.yml")
    
    with pytest.raises(ManifestError, match="both 'include' and 'exclude'"):
        validate_manifest(load_manifest(manifest_path))

def test_nonexistent_path_warning():
    manifest = {"include": ["playbooks/missing.yml"]}
    
    with pytest.warns(UserWarning, match="does not exist"):
        items = discover_with_include(Path("."), manifest["include"])
    
    assert len(items) == 0  # Skipped
```

---

## Future Enhancements (v2+)

### Glob Patterns

```yaml
include:
  - playbooks/prod-*.yml
  - roles/web-*
```

### Regex Patterns

```yaml
exclude:
  - pattern: "playbooks/.*-test\\.yml"
    type: regex
```

### Conditional Inclusion

```yaml
include:
  - playbooks/deploy.yml
    if: production  # Only include if --env=production flag passed
```

### Metadata in Manifest

```yaml
project:
  name: "My Ansible Project"
  version: "1.0.0"

include:
  - playbooks/deploy.yml
```

---

## Contract Guarantees

✅ **Guaranteed Stable**:
- `include` and `exclude` list structure
- Mutual exclusivity of `include`/`exclude`
- Relative path resolution from manifest location
- Warning (not error) for non-existent include paths
- YAML format

⚠️ **May Add (backward compatible)**:
- Glob pattern support
- Additional optional fields (metadata, versioning)

❌ **Will Not Break**:
- Existing `include`/`exclude` syntax
- Path resolution rules
- Validation rules

---

**Contract Status**: ✅ Stable for MVP (v1.0.0)
