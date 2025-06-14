#!/usr/bin/env python3
"""Release management script for SheetsBot.

This script handles version bumping, changelog updates, and GitHub release creation.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


def get_current_version() -> str:
    """Get current version from setup.py."""
    setup_py = Path("setup.py")
    if not setup_py.exists():
        raise FileNotFoundError("setup.py not found")
    
    content = setup_py.read_text()
    match = re.search(r'version="([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in setup.py")
    
    return match.group(1)


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version according to semantic versioning."""
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_version_in_files(new_version: str) -> None:
    """Update version in all relevant files."""
    files_to_update = [
        ("setup.py", r'version="[^"]+"', f'version="{new_version}"'),
        ("app/gui/main_window.py", r'setApplicationVersion\("[^"]+"\)', 
         f'setApplicationVersion("{new_version}")'),
    ]
    
    for file_path, pattern, replacement in files_to_update:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()
            new_content = re.sub(pattern, replacement, content)
            path.write_text(new_content)
            print(f"✅ Updated version in {file_path}")


def update_changelog(new_version: str, changes: Optional[str] = None) -> None:
    """Update CHANGELOG.md with new version."""
    changelog = Path("CHANGELOG.md")
    if not changelog.exists():
        print("⚠️  CHANGELOG.md not found, skipping changelog update")
        return
    
    content = changelog.read_text()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Replace [Unreleased] with new version
    unreleased_pattern = r"## \[Unreleased\]"
    new_section = f"## [Unreleased]\n\n### Added\n### Changed\n### Fixed\n\n## [{new_version}] - {today}"
    
    if changes:
        # Add custom changes to the release section
        new_section = new_section.replace(f"## [{new_version}] - {today}", 
                                        f"## [{new_version}] - {today}\n\n{changes}")
    
    new_content = re.sub(unreleased_pattern, new_section, content)
    
    # Update the links at the bottom
    links_pattern = r"\[Unreleased\]: https://github\.com/boadamm/demoproject/compare/v([^.]+\.[^.]+\.[^.]+)\.\.\.HEAD"
    links_replacement = f"[Unreleased]: https://github.com/boadamm/demoproject/compare/v{new_version}...HEAD\n[{new_version}]: https://github.com/boadamm/demoproject/compare/v\\1...v{new_version}"
    
    new_content = re.sub(links_pattern, links_replacement, new_content)
    
    changelog.write_text(new_content)
    print(f"✅ Updated CHANGELOG.md for version {new_version}")


def run_tests() -> bool:
    """Run the test suite."""
    print("🧪 Running tests...")
    try:
        result = subprocess.run(["pytest", "-q"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print(f"❌ Tests failed:\n{result.stdout}\n{result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠️  pytest not found, skipping tests")
        return True


def run_quality_checks() -> bool:
    """Run code quality checks."""
    print("🔍 Running quality checks...")
    
    checks = [
        (["ruff", "check", "."], "Ruff linting"),
        (["black", "--check", "."], "Black formatting"),
    ]
    
    for cmd, name in checks:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name} passed")
            else:
                print(f"❌ {name} failed:\n{result.stdout}\n{result.stderr}")
                return False
        except FileNotFoundError:
            print(f"⚠️  {name} tool not found, skipping")
    
    return True


def create_git_tag(version: str) -> None:
    """Create and push git tag."""
    tag_name = f"v{version}"
    print(f"🏷️  Creating git tag {tag_name}...")
    
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"chore: bump version to {version}"], check=True)
    subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"], check=True)
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["git", "push", "--tags"], check=True)
    
    print(f"✅ Created and pushed tag {tag_name}")


def main():
    """Main release function."""
    parser = argparse.ArgumentParser(description="Release management for SheetsBot")
    parser.add_argument(
        "bump_type", 
        choices=["major", "minor", "patch"], 
        help="Type of version bump"
    )
    parser.add_argument(
        "--skip-tests", 
        action="store_true", 
        help="Skip running tests"
    )
    parser.add_argument(
        "--skip-quality", 
        action="store_true", 
        help="Skip quality checks"
    )
    parser.add_argument(
        "--changes", 
        help="Custom changes description for this release"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    try:
        current_version = get_current_version()
        new_version = bump_version(current_version, args.bump_type)
        
        print(f"🚀 Preparing release: {current_version} → {new_version}")
        
        if args.dry_run:
            print("🔍 DRY RUN - No changes will be made")
            print(f"   - Would update version to {new_version}")
            print(f"   - Would update CHANGELOG.md")
            print(f"   - Would create git tag v{new_version}")
            return
        
        # Run quality checks
        if not args.skip_quality and not run_quality_checks():
            print("❌ Quality checks failed. Fix issues before releasing.")
            sys.exit(1)
        
        # Run tests
        if not args.skip_tests and not run_tests():
            print("❌ Tests failed. Fix issues before releasing.")
            sys.exit(1)
        
        # Update version in files
        update_version_in_files(new_version)
        
        # Update changelog
        update_changelog(new_version, args.changes)
        
        # Create git tag
        create_git_tag(new_version)
        
        print(f"🎉 Release {new_version} created successfully!")
        print(f"   GitHub Actions will now build and publish the release.")
        print(f"   Visit: https://github.com/boadamm/demoproject/releases")
        
    except Exception as e:
        print(f"❌ Release failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 