#!/bin/bash
#
# Generate Anodyse documentation - Portable CI/CD Script
#
# This script works on any CI system that supports shell execution:
# GitHub Actions, GitLab CI, Jenkins, Woodpecker, CircleCI, Travis CI, and others
#
# Usage:
#   chmod +x generate-docs.sh
#   ./generate-docs.sh
#
# Or with environment variables:
#   INPUT_DIR=./playbooks OUTPUT_DIR=./docs TEMPLATE_DIR=./templates ./generate-docs.sh
#

set -e  # Exit on any error

# ============================================================
# Configuration with defaults
# ============================================================

# Input source (Ansible playbooks/roles)
INPUT_DIR="${INPUT_DIR:=./playbooks}"

# Output destination (generated documentation)
OUTPUT_DIR="${OUTPUT_DIR:=./docs}"

# Custom templates (optional, uses built-in if not specified)
TEMPLATE_DIR="${TEMPLATE_DIR:=}"

# Verbosity
VERBOSE="${VERBOSE:=false}"

# Venv path (where to create Python virtual environment)
VENV_PATH="${VENV_PATH:=/tmp/anodyse_${CI_COMMIT_SHA:-$(date +%s)}}"

# ============================================================
# Helper functions
# ============================================================

log_info() {
    echo "[INFO] $*"
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_debug() {
    if [ "$VERBOSE" = "true" ] || [ "$VERBOSE" = "1" ]; then
        echo "[DEBUG] $*"
    fi
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Required command not found: $1"
        return 1
    fi
    log_debug "Found command: $1 ($(command -v "$1"))"
}

check_directory() {
    if [ ! -d "$1" ]; then
        log_error "Directory not found: $1"
        return 1
    fi
    log_debug "Directory exists: $1"
}

# ============================================================
# Pre-flight checks
# ============================================================

log_info "Anodyse Documentation Generator - CI/CD Integration"
log_info "=================================================="
log_info ""
log_info "Configuration:"
log_info "  INPUT_DIR:      $INPUT_DIR"
log_info "  OUTPUT_DIR:     $OUTPUT_DIR"
log_info "  TEMPLATE_DIR:   ${TEMPLATE_DIR:-(built-in)}"
log_info "  VENV_PATH:      $VENV_PATH"
log_info "  VERBOSE:        $VERBOSE"
log_info ""

# Check required commands
log_info "Verifying prerequisites..."
check_command python3 || exit 1
check_command pip || exit 1

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
log_info "  Python version: $PYTHON_VERSION"

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    log_error "Python 3.11+ required (found $PYTHON_VERSION)"
    exit 1
fi

# Check input directory
check_directory "$INPUT_DIR" || exit 1
FILES_FOUND=$(find "$INPUT_DIR" -name "*.yml" -o -name "*.yaml" | wc -l)
log_info "  Found $FILES_FOUND YAML files in $INPUT_DIR"

if [ "$FILES_FOUND" -eq 0 ]; then
    log_error "No YAML files found in $INPUT_DIR"
    exit 1
fi

# Check template directory if specified
if [ -n "$TEMPLATE_DIR" ]; then
    check_directory "$TEMPLATE_DIR" || exit 1
    TEMPLATE_FILES=$(find "$TEMPLATE_DIR" -name "*.j2" -o -name "*.jinja2" | wc -l)
    log_info "  Found $TEMPLATE_FILES template files in $TEMPLATE_DIR"
fi

# ============================================================
# Setup Python environment
# ============================================================

log_info ""
log_info "Setting up Python environment..."

if [ -d "$VENV_PATH" ]; then
    log_debug "Virtual environment already exists: $VENV_PATH"
    rm -rf "$VENV_PATH"
fi

python3 -m venv "$VENV_PATH"
log_debug "Created virtual environment: $VENV_PATH"

# Activate virtual environment
# shellcheck disable=SC1090
source "$VENV_PATH/bin/activate"
log_debug "Activated virtual environment"

# Upgrade pip, setuptools, wheel
log_info "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel 2>&1 | grep -v "already satisfied" || true

# Install Anodyse
log_info "Installing Anodyse..."
if pip install anodyse; then
    ANODYSE_VERSION=$(python -m anodyse --version 2>/dev/null || echo "unknown")
    log_info "  Anodyse installed: $ANODYSE_VERSION"
else
    log_error "Failed to install Anodyse"
    exit 1
fi

# ============================================================
# Create output directory
# ============================================================

log_info ""
log_info "Preparing output directory..."

if [ -d "$OUTPUT_DIR" ]; then
    log_debug "Output directory exists, clearing files"
    rm -rf "${OUTPUT_DIR:?}"/* || true
else
    log_debug "Creating output directory"
fi

mkdir -p "$OUTPUT_DIR"
log_debug "Output directory ready: $OUTPUT_DIR"

# ============================================================
# Generate documentation
# ============================================================

log_info ""
log_info "Generating documentation..."

ANODYSE_ARGS=("$INPUT_DIR" "--output" "$OUTPUT_DIR")

if [ -n "$TEMPLATE_DIR" ]; then
    log_info "WARNING: TEMPLATE_DIR is set but current Anodyse CLI does not support --template-dir; proceeding without it"
fi

if [ "$VERBOSE" = "true" ] || [ "$VERBOSE" = "1" ]; then
    ANODYSE_ARGS+=("--verbose")
fi

log_debug "Anodyse command: python -m anodyse ${ANODYSE_ARGS[*]}"

if python -m anodyse "${ANODYSE_ARGS[@]}"; then
    log_info "Documentation generation completed successfully"
else
    log_error "Documentation generation failed"
    exit 1
fi

# ============================================================
# Verify output
# ============================================================

log_info ""
log_info "Verifying output..."

if [ ! -f "$OUTPUT_DIR/index.md" ]; then
    log_error "ERROR: Generated documentation missing index.md"
    exit 1
fi

FILES_GENERATED=$(find "$OUTPUT_DIR" -type f -name "*.md" | wc -l)
log_info "  Generated $FILES_GENERATED documentation files"

SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)
log_info "  Total size: $SIZE"

log_debug "Output directory contents:"
ls -la "$OUTPUT_DIR/" | sed 's/^/    /'

# ============================================================
# Cleanup (optional)
# ============================================================

log_info ""
log_info "Cleanup..."

if [ "${CLEANUP_VENV:-false}" = "true" ] || [ "${CLEANUP_VENV:-false}" = "1" ]; then
    log_info "  Removing virtual environment: $VENV_PATH"
    deactivate || true
    rm -rf "$VENV_PATH"
else
    log_debug "Virtual environment preserved at: $VENV_PATH"
fi

# ============================================================
# Summary
# ============================================================

log_info ""
log_info "=================================================="
log_info "✓ Documentation generation completed successfully"
log_info ""
log_info "Output location: $OUTPUT_DIR"
log_info "Ready for:"
log_info "  - Viewing as Markdown files"
log_info "  - Publishing to static site hosting"
log_info "  - Committing to version control"
log_info ""

exit 0
