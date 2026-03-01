# CLI Command Contract

**Version**: 1.0.0 (MVP)  
**Feature**: 001-core-pipeline  
**Date**: 2026-03-01

---

## Command Signature

```bash
anodyse [OPTIONS] <target>
```

### Positional Argument

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `target` | Path | Yes | Path to Ansible playbook file (.yml), role directory, or directory containing multiple playbooks/roles |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output` | `-o` | Path | `./docs` | Output directory for generated Markdown files |
| `--graph` | | Flag | False | Include Mermaid flowchart diagrams in output |
| `--no-backup` | | Flag | False | Skip creating .bak files before overwriting existing docs |
| `--verbose` | `-v` | Flag | False | Print detailed processing information to stdout |
| `--format` | | Choice | `markdown` | Output format (only "markdown" supported in MVP) |
| `--config` | | Path | None | Explicit path to .anodyse.yml manifest file (overrides auto-discovery) |
| `--help` | `-h` | Flag | | Show help message and exit |

---

## Exit Codes

| Code | Meaning | Scenario |
|------|---------|----------|
| 0 | Success | All files processed and documentation generated successfully |
| 1 | Parse Error | YAML syntax error, file not found, invalid role structure, or manifest parse error |
| 2 | Warning | Missing mandatory annotations (@title, @description) OR incompatible user template; degraded output produced |

**Exit Code Rules**:
- Exit 1 if any **unrecoverable error** occurs (cannot continue processing)
- Exit 2 if **warnings** emitted but output successfully generated (graceful degradation)
- Exit 0 only if **no errors or warnings** detected

---

## Usage Examples

### Single Playbook

```bash
# Process single playbook with default output directory
anodyse playbooks/deploy.yml

# Process with custom output directory
anodyse playbooks/deploy.yml --output ./documentation

# Include Mermaid diagrams
anodyse playbooks/deploy.yml --graph --output ./docs

# Verbose output for debugging
anodyse playbooks/deploy.yml --verbose
```

### Directory with Multiple Items

```bash
# Auto-discover all playbooks and roles in directory
anodyse ./playbooks --output ./docs

# With explicit manifest
anodyse ./playbooks --config .anodyse.yml --output ./docs

# Suppress backup files
anodyse ./ansible --output ./docs --no-backup
```

### Role Directory

```bash
# Process single role
anodyse roles/webserver --output ./docs

# Role with diagrams
anodyse roles/webserver --graph --output ./docs
```

---

## Output Behavior

### Files Generated

For each playbook/role:
- One Markdown file: `<slugified-name>.md`
- Optional backup: `<slugified-name>.md.bak` (if file exists and `--no-backup` not set)

Always generated:
- `index.md` — listing all processed items with tags and descriptions

### Output Directory Structure

```text
docs/
├── index.md
├── deploy-app.md
├── configure-database.md
├── webserver.md  (role)
└── nginx.md      (role)
```

### File Naming Rules

- Playbook/role names slugified: lowercase, hyphens, no special characters
- Extensions always `.md`
- Collisions resolved with `-1`, `-2`, etc. suffix

---

## Discovery Behavior

### Mode 1: Directory Scan (default)

When `<target>` is a directory and no `.anodyse.yml` manifest exists:

1. Recursively scan for `.yml` and `.yaml` files
2. Check each YAML file for top-level `hosts:` key → playbook
3. Recursively scan for `tasks/main.yml` → parent directory is role
4. Generate docs for all discovered items

**Files/Directories Ignored**:
- Hidden files/directories (starting with `.`)
- `__pycache__`, `*.pyc`, `*.pyo`
- No explicit `.gitignore` parsing (all visible YAML files scanned)

### Mode 2: Manifest Override

When `.anodyse.yml` exists (auto-discovered or via `--config`):

1. Load manifest from:
   - Path specified by `--config` flag (highest priority)
   - `.anodyse.yml` in `<target>` directory
   - `.anodyse.yml` in repository root (lowest priority)

2. Apply `include` or `exclude` list:
   - If `include` present: only explicitly listed paths processed
   - If `exclude` present: all discovered items except listed paths
   - If both present: **error** (mutually exclusive)

3. Emit **warning** (not error) for non-existent paths in manifest

---

## Error Messages

### File Not Found

```text
Error: File not found: playbooks/missing.yml
Exit code: 1
```

### YAML Parse Error

```text
Error: YAML syntax error in playbooks/broken.yml:
  Line 15: expected ':' but found '='
Exit code: 1
```

### No Valid Items Found

```text
Error: No valid playbooks or roles found in ./empty-dir
Searched for:
  - .yml files with 'hosts:' key
  - directories with tasks/main.yml
Exit code: 1
```

### Missing Annotations (Warning)

```text
Warning: Missing @title annotation in playbooks/deploy.yml
Warning: Missing @description annotation in playbooks/deploy.yml
Output generated with 'Undocumented' notices.
Exit code: 2
```

### Incompatible Template (Warning)

```text
Warning: User template .anodyse/templates/playbook.md.j2 incompatible:
  TemplateError: undefined variable 'missing_field'
Falling back to default template.
Exit code: 2
```

### Manifest Error

```text
Error: Invalid .anodyse.yml manifest:
  Cannot specify both 'include' and 'exclude' lists
Exit code: 1
```

---

## Stdout/Stderr Behavior

### Normal Mode (non-verbose)

- Errors → stderr
- Warnings → stderr
- No other output (silent success)

### Verbose Mode (`--verbose`)

Prints to stdout:
```text
Discovering items in ./playbooks...
Found 3 playbooks, 2 roles
Processing playbooks/deploy.yml...
  - Extracted 5 tasks, 12 annotations
  - Rendered to docs/deploy.md
Processing roles/webserver...
  - Extracted 8 tasks, 4 annotations
  - Rendered to docs/webserver.md
Generating index.md...
Done. 5 files written to docs/
```

---

## Versioning and Stability

### MVP (v1.0)

- Command signature stable
- Exit codes guaranteed per contract
- `--format markdown` only option (future: pdf, html)
- All options documented here are supported

### Future Compatibility (v2+)

Planned additions (backward compatible):
- `-w/--watch` flag for file watching mode
- `--template <name>` for built-in template selection
- `--output-format pdf|html|markdown`
- Sub-commands: `anodyse generate`, `anodyse validate`, etc.

**Breaking Changes**: None planned for v1.x series

---

## Contract Guarantees

✅ **Guaranteed Stable**:
- `anodyse <target>` positional argument
- `--output` directory specification
- Exit codes 0, 1, 2 meanings
- `index.md` always generated
- Slugified output filenames

⚠️ **May Change in Minor Version**:
- Exact warning message text
- Mermaid diagram syntax (improvements)
- Discovery heuristics (better playbook detection)

❌ **Experimental (may change in patch)**:
- `--format` validation (only markdown supported; others rejected)
- Verbose output format and level of detail

---

## Testing the Contract

### Integration Test Suite

```bash
# Test 1: Single playbook
anodyse tests/fixtures/playbook.yml --output /tmp/test1
[[ $? -eq 0 ]] && echo "PASS" || echo "FAIL"

# Test 2: Directory discovery
anodyse tests/fixtures/multi/ --output /tmp/test2
[[ $? -eq 0 ]] && echo "PASS" || echo "FAIL"

# Test 3: Missing file (expect exit 1)
anodyse /nonexistent.yml --output /tmp/test3
[[ $? -eq 1 ]] && echo "PASS" || echo "FAIL"

# Test 4: Malformed YAML (expect exit 1)
anodyse tests/fixtures/broken.yml --output /tmp/test4
[[ $? -eq 1 ]] && echo "PASS" || echo "FAIL"

# Test 5: Missing annotations (expect exit 2)
anodyse tests/fixtures/no_annotations.yml --output /tmp/test5
[[ $? -eq 2 ]] && echo "PASS" || echo "FAIL"
```

---

**Contract Status**: ✅ Stable for MVP (v1.0.0)
