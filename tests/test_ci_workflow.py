"""
Test suite for CI workflow configuration.

Following TDD principles - these tests should fail initially,
then pass after implementing the CI workflow.
"""

import pytest
from pathlib import Path
import yaml


class TestCIWorkflow:
    """Test cases for GitHub Actions CI workflow configuration."""

    def test_ci_workflow_file_exists(self):
        """Assert that a YAML file exists at .github/workflows/ci.yml."""
        workflow_file = Path(".github/workflows/ci.yml")
        assert (
            workflow_file.exists()
        ), "CI workflow file must exist at .github/workflows/ci.yml"

    def test_ci_workflow_contains_required_jobs(self):
        """Assert that the workflow file string-matches the required job names."""
        workflow_file = Path(".github/workflows/ci.yml")
        if not workflow_file.exists():
            pytest.fail("CI workflow file does not exist")

        workflow_content = workflow_file.read_text()

        # Required job step names that must be present
        required_jobs = ["ruff", "black-check", "pytest", "docker-build"]

        for job_name in required_jobs:
            assert (
                job_name in workflow_content
            ), f"Job '{job_name}' must be present in CI workflow"

    def test_ci_workflow_uses_python_3_11(self):
        """Assert that the workflow sets python-version: '3.11'."""
        workflow_file = Path(".github/workflows/ci.yml")
        if not workflow_file.exists():
            pytest.fail("CI workflow file does not exist")

        workflow_content = workflow_file.read_text()

        # Check for Python 3.11 version specification
        assert (
            "python-version: '3.11'" in workflow_content
        ), "Workflow must specify python-version: '3.11'"

    def test_ci_workflow_valid_yaml_structure(self):
        """Ensure the CI workflow file is valid YAML and has expected structure."""
        workflow_file = Path(".github/workflows/ci.yml")
        if not workflow_file.exists():
            pytest.fail("CI workflow file does not exist")

        # Parse YAML to ensure it's valid
        with open(workflow_file, "r") as f:
            try:
                workflow_data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"CI workflow file contains invalid YAML: {e}")

        # Check basic GitHub Actions structure
        # Note: PyYAML converts 'on' keyword to True in Python
        triggers_key = "on" if "on" in workflow_data else True
        assert (
            triggers_key in workflow_data
        ), "Workflow must have 'on' trigger configuration"
        assert "jobs" in workflow_data, "Workflow must have 'jobs' section"

        # Check triggers include push and pull_request
        triggers = workflow_data[triggers_key]
        if isinstance(triggers, list):
            assert "push" in triggers, "Workflow must trigger on push"
            assert "pull_request" in triggers, "Workflow must trigger on pull_request"
        elif isinstance(triggers, dict):
            assert (
                "push" in triggers or "pull_request" in triggers
            ), "Workflow must trigger on push and/or pull_request"

    def test_ci_workflow_uses_setup_python_v5(self):
        """Assert that the workflow uses actions/setup-python@v5."""
        workflow_file = Path(".github/workflows/ci.yml")
        if not workflow_file.exists():
            pytest.fail("CI workflow file does not exist")

        workflow_content = workflow_file.read_text()
        assert (
            "actions/setup-python@v5" in workflow_content
        ), "Workflow must use actions/setup-python@v5"

    def test_ci_workflow_includes_coverage_requirement(self):
        """Assert that pytest runs with coverage requirement of 90%."""
        workflow_file = Path(".github/workflows/ci.yml")
        if not workflow_file.exists():
            pytest.fail("CI workflow file does not exist")

        workflow_content = workflow_file.read_text()
        assert (
            "--cov-fail-under=90" in workflow_content
        ), "Workflow must include --cov-fail-under=90 for pytest"

    def test_ci_workflow_includes_full_coverage(self):
        """Assert that pytest runs with full coverage (--cov=.) not just app coverage."""
        workflow_file = Path(".github/workflows/ci.yml")
        if not workflow_file.exists():
            pytest.fail("CI workflow file does not exist")

        workflow_content = workflow_file.read_text()
        assert (
            "--cov=." in workflow_content
        ), "Workflow must include --cov=. for full project coverage"

    def test_docker_build_present(self):
        """Assert that Docker build step exists to verify image builds successfully."""
        workflow_file = Path(".github/workflows/ci.yml")
        if not workflow_file.exists():
            pytest.fail("CI workflow file does not exist")

        workflow_content = workflow_file.read_text()
        assert (
            "sheets-bot:ci" in workflow_content
        ), "Workflow must build Docker image with tag 'sheets-bot:ci'"
        assert (
            "docker build" in workflow_content
        ), "Workflow must include docker build command"
