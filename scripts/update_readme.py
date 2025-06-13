#!/usr/bin/env python3
"""
Update README.md with Latest Release badge and download links.

CLI script for Sprint 6 – T17 that:
1. Inserts/updates a GitHub release badge
2. Adds or updates Downloads section with direct links
3. Is idempotent (running twice makes no duplicate lines)

Usage:
    python scripts/update_readme.py [release_tag]
    GITHUB_REF_NAME=v1.0.0 python scripts/update_readme.py
"""

import sys
import os
from pathlib import Path


def get_release_tag() -> str:
    """Get release tag from environment variable or command line argument."""
    # Try command line argument first
    if len(sys.argv) > 1:
        return sys.argv[1]

    # Try environment variable (GitHub Actions)
    if "GITHUB_REF_NAME" in os.environ:
        return os.environ["GITHUB_REF_NAME"]

    # Default fallback
    return "v1.0.0"


def get_repository_name() -> str:
    """Get repository name from environment or default."""
    if "GITHUB_REPOSITORY" in os.environ:
        return os.environ["GITHUB_REPOSITORY"]
    return "baranozck/sheets-bot"


def create_release_badge(repo_name: str) -> str:
    """Create the Latest Release badge markdown."""
    return f"[![Latest Release](https://img.shields.io/github/v/release/{repo_name})](https://github.com/{repo_name}/releases/latest)"


def create_downloads_section(repo_name: str, release_tag: str) -> str:
    """Create the Downloads section with direct links."""
    base_url = f"https://github.com/{repo_name}/releases/download/{release_tag}"

    return f"""## Downloads

Get the latest desktop application:

- **Windows (signed)**: [{release_tag} SheetsBot-Windows-signed.zip]({base_url}/SheetsBot-Windows-signed.zip)
- **Linux**: [{release_tag} SheetsBot-Linux.zip]({base_url}/SheetsBot-Linux.zip)

> 💡 **No Python installation required** - these are fully self-contained desktop applications.

"""


def update_readme_with_badge(content: str, badge: str) -> str:
    """Update README content with release badge (idempotent)."""
    lines = content.split("\n")

    # Check if badge already exists
    if "[![Latest Release]" in content:
        # Update existing badge
        for i, line in enumerate(lines):
            if "[![Latest Release]" in line:
                lines[i] = badge
                break
    else:
        # Insert badge after title and existing badges
        insert_index = 1  # After title

        # Find the end of existing badges
        for i, line in enumerate(lines[1:], 1):
            if line.strip().startswith("[![") and ")](" in line:
                insert_index = i + 1
            elif (
                line.strip() and not line.startswith("#") and not line.startswith("[![")
            ):
                break

        lines.insert(insert_index, badge)

    return "\n".join(lines)


def update_readme_with_downloads(content: str, downloads_section: str) -> str:
    """Update README content with Downloads section (idempotent)."""
    lines = content.split("\n")

    # Check if Downloads section already exists
    downloads_start = None
    downloads_end = None

    for i, line in enumerate(lines):
        if line.strip() == "## Downloads":
            downloads_start = i
            # Find end of downloads section
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## ") and j > i:
                    downloads_end = j
                    break
            else:
                downloads_end = len(lines)
            break

    if downloads_start is not None:
        # Replace existing Downloads section
        new_lines = (
            lines[:downloads_start]
            + downloads_section.split("\n")
            + lines[downloads_end:]
        )
        return "\n".join(new_lines)
    else:
        # Insert Downloads section after badges/description, before Quick Start
        insert_index = len(lines)  # Default to end

        # Look for Quick Start section to insert before it
        for i, line in enumerate(lines):
            if "## Quick Start" in line or "## Usage" in line or "## Features" in line:
                insert_index = i
                break

        # Insert with proper spacing
        new_lines = (
            lines[:insert_index]
            + [""]
            + downloads_section.split("\n")
            + lines[insert_index:]
        )
        return "\n".join(new_lines)


def main():
    """Main function to update README.md with release badges and download links."""
    # Get parameters
    release_tag = get_release_tag()
    repo_name = get_repository_name()

    print(f"Updating README.md with release {release_tag} for repo {repo_name}")

    # Read current README
    readme_path = Path(__file__).parent.parent / "README.md"
    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        sys.exit(1)

    content = readme_path.read_text(encoding="utf-8")

    # Create badge and downloads section
    badge = create_release_badge(repo_name)
    downloads_section = create_downloads_section(repo_name, release_tag)

    # Update content (idempotent operations)
    content = update_readme_with_badge(content, badge)
    content = update_readme_with_downloads(content, downloads_section)

    # Write back to file
    readme_path.write_text(content, encoding="utf-8")

    print("✅ README.md updated successfully")
    print(f"   - Added/updated Latest Release badge: {repo_name}")
    print(f"   - Added/updated Downloads section for: {release_tag}")
    print("   - Windows: SheetsBot-Windows-signed.zip")
    print("   - Linux: SheetsBot-Linux.zip")


if __name__ == "__main__":
    main()
