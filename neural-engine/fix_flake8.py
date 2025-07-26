#!/usr/bin/env python3
"""Script to fix common flake8 issues."""

import re
import os
from pathlib import Path


def fix_file(filepath) -> None:
    """Fix common flake8 issues in a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix f-string without placeholders - convert to regular string
        content = re.sub(r'f"([^{]*)"', r'"\1"', content)
        content = re.sub(r"f'([^{]*)'", r"'\1'", content)

        # Fix arithmetic operator spacing issues
        content = re.sub(r"(\d+)\*(\d+)", r"\1 * \2", content)
        content = re.sub(r"(\w+)\*(\w+)", r"\1 * \2", content)

        # Fix unused variables by prefixing with underscore
        lines = content.split("\n")
        for i, line in enumerate(lines):
            # Look for variable assignments that are never used
            if "=" in line and not line.strip().startswith("#"):
                # Extract variable name from assignment
                match = re.match(r"(\s+)(\w+)\s*=", line)
                if match and "local variable" in str(line):
                    indent, var_name = match.groups()
                    if not var_name.startswith("_"):
                        lines[i] = line.replace(f"{var_name} =", f"_{var_name} =")

        content = "\n".join(lines)

        # Only write if changes were made
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed {filepath}")

    except Exception as e:
        print(f"Error fixing {filepath}: {e}")


def main() -> None:
    """Fix all Python files in common problematic directories."""
    base_dir = Path(".")

    # Directories to fix
    dirs_to_fix = [
        "neural-engine/security",
        "neural-engine/examples",
        "tests/test_ledger",
        "scripts",
    ]

    for dir_path in dirs_to_fix:
        full_dir = base_dir / dir_path
        if full_dir.exists():
            for py_file in full_dir.glob("*.py"):
                fix_file(py_file)


if __name__ == "__main__":
    main()
