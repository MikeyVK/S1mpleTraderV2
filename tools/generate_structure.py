# tools/generate_structure.py
"""
Generates a text file representing the project's directory and file structure.

This script scans the project from the root directory, respects the rules
in the .gitignore file, and outputs a clean, indented tree structure to a
specified text file.

@layer: Tool
"""

# 1. Standard Library Imports
import os
import fnmatch
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "docs" / "folder_file_structure.txt"
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"

# Default patterns to always ignore, even if not in .gitignore
DEFAULT_IGNORE = {".git", ".vscode", "*.pyc", "*__pycache__*", ".DS_Store"}


def read_gitignore() -> set:
    """
    Reads and parses the .gitignore file.

    Returns:
        set: A set of patterns to be ignored.
    """
    if not GITIGNORE_PATH.is_file():
        print("Warning: .gitignore file not found at project root.")
        return set()

    with open(GITIGNORE_PATH, 'r', encoding='utf-8') as f:
        patterns = {
            line.strip() for line in f
            if line.strip() and not line.startswith('#')
        }
    return patterns


def should_ignore(path: Path, ignore_patterns: set) -> bool:
    """
    Checks if a path should be ignored using a simplified interpretation
    of .gitignore-style patterns.

    @inputs:
        path (Path): The path object relative to the project root.
        ignore_patterns (set): A set of patterns from .gitignore and defaults.

    @outputs:
        bool: True if the path should be ignored, False otherwise.
    """
    for pattern in ignore_patterns:
        # Handle directory-only patterns (e.g., 'build/', '__pycache__/')
        if pattern.endswith('/'):
            if pattern.rstrip('/') in path.parts:
                return True
        # Handle file/general patterns (e.g., '*.pyc', '.DS_Store')
        elif fnmatch.fnmatch(path.name, pattern):
            return True
    return False


def generate_structure(directory: Path, ignore_patterns: set, prefix: str = "") -> str:
    """
    Recursively generates the directory structure string.
    """
    structure = ""
    # Create a sorted list of items to process
    try:
        items = sorted(list(directory.iterdir()), key=lambda p: (p.is_file(), p.name.lower()))
    except FileNotFoundError:
        return "" # Directory might have been deleted mid-run

    # Create a list of non-ignored items to correctly determine the last element
    valid_items = [p for p in items if not should_ignore(p.relative_to(PROJECT_ROOT), ignore_patterns)]

    for i, path in enumerate(valid_items):
        is_last = (i == len(valid_items) - 1)
        connector = "└── " if is_last else "├── "
        structure += f"{prefix}{connector}{path.name}\n"

        if path.is_dir():
            extension = "    " if is_last else "│   "
            structure += generate_structure(
                path, ignore_patterns, prefix + extension
            )

    return structure


def main():
    """Main function to generate and save the structure file."""
    print("Generating project structure...")

    ignore_patterns = DEFAULT_IGNORE.union(read_gitignore())
    project_name = PROJECT_ROOT.name
    tree_string = generate_structure(PROJECT_ROOT, ignore_patterns)
    full_output = f"{project_name}/\n{tree_string}"

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(full_output)

    print(f"✅ Project structure saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()