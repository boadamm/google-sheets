"""Test suite for documentation polish requirements.

Following TDD principles, these tests define the expected behavior
of the documentation before implementation.
"""

from pathlib import Path


class TestDocsPolish:
    """Test cases for documentation polish requirements."""

    def test_docs_readme_exists(self):
        """Test that docs/README.md exists."""
        docs_readme = Path("docs/README.md")
        assert docs_readme.exists(), "docs/README.md should exist"

    def test_docs_readme_contains_required_sections(self):
        """Test that docs/README.md contains required sections."""
        docs_readme = Path("docs/README.md")
        content = docs_readme.read_text()

        # Check for required strings
        assert "Quick Start" in content, "docs/README.md should contain 'Quick Start'"
        assert "Watcher" in content, "docs/README.md should contain 'Watcher'"
        assert "CLI one-shot" in content, "docs/README.md should contain 'CLI one-shot'"

    def test_docs_readme_contains_wsl_miniconda_section(self):
        """Test that docs/README.md contains WSL + Miniconda quick start."""
        docs_readme = Path("docs/README.md")
        content = docs_readme.read_text()

        # Check for WSL/Miniconda specific content
        assert "WSL" in content, "docs/README.md should mention WSL"
        assert "Miniconda" in content, "docs/README.md should mention Miniconda"
        assert "conda env create" in content, "Should contain conda env create command"
        assert "conda activate" in content, "Should contain conda activate command"

    def test_docs_readme_contains_one_shot_demo(self):
        """Test that docs/README.md contains one-shot CLI demo."""
        docs_readme = Path("docs/README.md")
        content = docs_readme.read_text()

        # Check for CLI demo content
        assert (
            "python cli.py --file samples/data.csv --once" in content
        ), "Should contain CLI demo command"
        assert (
            "Sample Output" in content or "output" in content.lower()
        ), "Should show sample output"

    def test_docs_readme_contains_live_watch_demo(self):
        """Test that docs/README.md contains live watch demo."""
        docs_readme = Path("docs/README.md")
        content = docs_readme.read_text()

        # Check for watcher demo content
        assert (
            "python -m app.watcher_demo" in content
        ), "Should contain watcher demo command"
        assert (
            "incoming" in content.lower() or "watch" in content.lower()
        ), "Should mention file watching"

    def test_docs_readme_contains_troubleshooting(self):
        """Test that docs/README.md contains WSL troubleshooting section."""
        docs_readme = Path("docs/README.md")
        content = docs_readme.read_text()

        # Check for troubleshooting content
        assert (
            "Troubleshooting" in content
        ), "docs/README.md should contain 'Troubleshooting'"
        assert "sudo apt" in content, "Should contain apt install commands"
        assert (
            "libxml2-dev" in content or "libxslt1-dev" in content
        ), "Should mention XML/XSLT dependencies"

    def test_top_level_readme_links_to_docs(self):
        """Test that top-level README.md links to docs/README.md."""
        readme = Path("README.md")
        content = readme.read_text()

        # Check for link to docs/README.md
        assert (
            "docs/README.md" in content
        ), "Top-level README should link to docs/README.md"

    def test_status_md_contains_sprint_t5_entry(self):
        """Test that docs/status.md contains Sprint 2 – T5 entry."""
        status_md = Path("docs/status.md")
        content = status_md.read_text()

        # Check for T5 sprint entry
        assert (
            "Sprint 2 – T5 docs & samples finished" in content
        ), "docs/status.md should contain Sprint 2 – T5 entry"

    def test_sample_files_referenced_in_docs(self):
        """Test that sample files are referenced in documentation."""
        docs_readme = Path("docs/README.md")
        content = docs_readme.read_text()

        # Check that sample files are mentioned
        assert (
            "samples/data.csv" in content
        ), "docs/README.md should reference samples/data.csv"
        assert (
            "samples/data.xlsx" in content
        ), "docs/README.md should reference samples/data.xlsx"

    def test_sample_files_exist(self):
        """Test that the sample files actually exist."""
        csv_sample = Path("samples/data.csv")
        xlsx_sample = Path("samples/data.xlsx")

        assert csv_sample.exists(), "samples/data.csv should exist"
        assert xlsx_sample.exists(), "samples/data.xlsx should exist"
