"""Tests for Windows code signing in GitHub Actions release workflow.

Following TDD principles, these tests verify that:
1. The release workflow YAML file contains a codesign step
2. The codesign step runs only on Windows (matrix.os == 'windows-latest')
3. The codesign step has proper conditional logic for handling missing secrets
4. The docs/status.md includes the Sprint 6 – T16 completion entry
"""

import yaml
from pathlib import Path


def test_release_workflow_has_codesign_step():
    """Test that the release workflow contains a codesign step."""
    workflow_path = Path(".github/workflows/release.yml")
    assert workflow_path.exists(), "Release workflow file must exist"

    with open(workflow_path, "r") as file:
        workflow_content = file.read()

    # Look for codesign step in the workflow
    assert (
        "codesign" in workflow_content.lower()
    ), "Workflow must contain a codesign step"


def test_codesign_step_windows_only():
    """Test that codesign step runs only on Windows."""
    workflow_path = Path(".github/workflows/release.yml")

    with open(workflow_path, "r") as file:
        workflow_config = yaml.safe_load(file)

    build_job = workflow_config["jobs"]["build-release"]
    steps = build_job["steps"]

    # Find codesign-related steps
    codesign_steps = [
        step
        for step in steps
        if "codesign" in step.get("name", "").lower()
        or "sign" in step.get("name", "").lower()
        or "cert" in step.get("name", "").lower()
    ]

    assert len(codesign_steps) > 0, "Must have at least one codesign-related step"

    for step in codesign_steps:
        assert (
            "if" in step
        ), f"Codesign step '{step.get('name')}' must have conditional execution"
        condition = step["if"]
        assert (
            "windows" in condition.lower()
        ), f"Codesign step must be Windows-specific: {condition}"


def test_codesign_step_handles_missing_secrets():
    """Test that codesign step gracefully handles missing secrets for forks."""
    workflow_path = Path(".github/workflows/release.yml")

    with open(workflow_path, "r") as file:
        workflow_config = yaml.safe_load(file)

    build_job = workflow_config["jobs"]["build-release"]
    steps = build_job["steps"]

    # Find codesign-related steps
    codesign_steps = [
        step
        for step in steps
        if "codesign" in step.get("name", "").lower()
        or "sign" in step.get("name", "").lower()
        or "cert" in step.get("name", "").lower()
    ]

    assert len(codesign_steps) > 0, "Must have at least one codesign-related step"

    # At least one step should check for secret availability
    secret_check_found = False
    for step in codesign_steps:
        condition = step.get("if", "")
        if "WIN_CERT_BASE64" in condition or "secrets" in condition:
            secret_check_found = True
            break

    assert (
        secret_check_found
    ), "At least one codesign step must check for WIN_CERT_BASE64 secret availability"


def test_codesign_workflow_creates_signed_zip():
    """Test that the workflow creates a signed ZIP file."""
    workflow_path = Path(".github/workflows/release.yml")

    with open(workflow_path, "r") as file:
        workflow_content = file.read()

    # Look for signed ZIP creation
    assert (
        "signed" in workflow_content.lower()
    ), "Workflow must create a signed ZIP file"
    assert (
        "SheetsBot-Windows-signed.zip" in workflow_content
    ), "Must create SheetsBot-Windows-signed.zip"


def test_codesign_uses_signtool():
    """Test that the workflow uses signtool for code signing."""
    workflow_path = Path(".github/workflows/release.yml")

    with open(workflow_path, "r") as file:
        workflow_content = file.read()

    assert "signtool" in workflow_content, "Workflow must use signtool for code signing"
    assert (
        "certutil" in workflow_content
    ), "Workflow must use certutil for certificate handling"


def test_docs_status_updated_t16():
    """Test that docs/status.md includes the Sprint 6 – T16 completion entry."""
    status_path = Path("docs/status.md")

    with open(status_path, "r") as file:
        status_content = file.read()

    assert (
        "Sprint 6 – T16 Windows code-signing added" in status_content
    ), "docs/status.md must include 'Sprint 6 – T16 Windows code-signing added' entry"
