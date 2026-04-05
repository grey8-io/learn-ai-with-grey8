#!/usr/bin/env bash
# setup-hooks.sh — Symlinks git hooks from scripts/hooks/ into .git/hooks/.
# Idempotent: safe to run multiple times.
# Works on Linux, macOS, and Git Bash on Windows.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_SOURCE="$REPO_ROOT/scripts/hooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "ERROR: No .git directory found at $REPO_ROOT"
    echo "       Run this script from within a git repository."
    exit 1
fi

mkdir -p "$GIT_HOOKS_DIR"

HOOKS=(pre-commit post-merge post-checkout)

for hook in "${HOOKS[@]}"; do
    SOURCE="$HOOKS_SOURCE/$hook"
    TARGET="$GIT_HOOKS_DIR/$hook"

    if [ ! -f "$SOURCE" ]; then
        echo "WARNING: Source hook not found: $SOURCE"
        continue
    fi

    # Remove existing hook (file, symlink, or broken symlink)
    if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
        rm -f "$TARGET"
    fi

    # Create symlink (use relative path for portability)
    ln -s "../../scripts/hooks/$hook" "$TARGET"

    # Ensure executable
    chmod +x "$SOURCE"

    echo "  Installed: $hook"
done

echo ""
echo "Git hooks installed successfully."
echo "Hooks will auto-sync curriculum context on commit and branch switches."
