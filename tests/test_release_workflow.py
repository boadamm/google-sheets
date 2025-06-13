"""Tests for GitHub Actions release workflow configuration.

Following TDD principles, these tests verify that:
1. The release workflow YAML file exists at .github/workflows/release.yml
2. The workflow contains the required job name "build-release" 
3. The workflow uses the "softprops/action-gh-release" action
4. The docs/status.md includes the Sprint 6 – T15 completion entry
"""

import yaml
from pathlib import Path


def test_release_workflow_file_exists():
    """Test that the release workflow YAML file exists at the expected path."""
    workflow_path = Path(".github/workflows/release.yml")
    assert (
        workflow_path.exists()
    ), "Release workflow file must exist at .github/workflows/release.yml"


def test_release_workflow_has_build_release_job():
    """Test that the release workflow contains the required 'build-release' job."""
    workflow_path = Path(".github/workflows/release.yml")

    with open(workflow_path, "r") as file:
        workflow_config = yaml.safe_load(file)

    assert "jobs" in workflow_config, "Workflow must have 'jobs' section"
    assert (
        "build-release" in workflow_config["jobs"]
    ), "Workflow must contain 'build-release' job"


def test_release_workflow_uses_gh_release_action():
    """Test that the release workflow uses the softprops/action-gh-release action."""
    workflow_path = Path(".github/workflows/release.yml")

    with open(workflow_path, "r") as file:
        workflow_config = yaml.safe_load(file)

    # Check that the workflow uses the required action
    workflow_yaml_str = yaml.dump(workflow_config)
    assert (
        "softprops/action-gh-release" in workflow_yaml_str
    ), "Workflow must use 'softprops/action-gh-release' action"


def test_release_workflow_has_correct_triggers():
    """Test that the release workflow has the correct trigger events."""
    workflow_path = Path(".github/workflows/release.yml")

    with open(workflow_path, "r") as file:
        workflow_config = yaml.safe_load(file)

    # Handle the fact that PyYAML might parse 'on' as boolean True
    triggers = workflow_config.get("on") or workflow_config.get(True)
    assert (
        triggers is not None
    ), "Workflow must have trigger events (check 'on' or True key)"

    # Check for release trigger
    assert "release" in triggers, "Workflow must be triggered on release events"
    assert "types" in triggers["release"], "Release trigger must specify types"
    assert (
        "published" in triggers["release"]["types"]
    ), "Must trigger on 'published' release type"

    # Check for manual trigger
    assert "workflow_dispatch" in triggers, "Workflow must support manual dispatch"


def test_release_workflow_has_matrix_strategy():
    """Test that the build-release job uses matrix strategy for multiple OS."""
    workflow_path = Path(".github/workflows/release.yml")

    with open(workflow_path, "r") as file:
        workflow_config = yaml.safe_load(file)

    build_job = workflow_config["jobs"]["build-release"]
    assert "strategy" in build_job, "build-release job must use strategy"
    assert "matrix" in build_job["strategy"], "Strategy must use matrix"
    assert "os" in build_job["strategy"]["matrix"], "Matrix must specify OS"

    matrix_os = build_job["strategy"]["matrix"]["os"]
    assert "windows-latest" in matrix_os, "Matrix must include windows-latest"
    assert "ubuntu-latest" in matrix_os, "Matrix must include ubuntu-latest"


def test_release_workflow_has_publish_release_job():
    """Test that the workflow has a publish-release step with proper conditions."""
    workflow_path = Path(".github/workflows/release.yml")

    with open(workflow_path, "r") as file:
        workflow_config = yaml.safe_load(file)

    # Look for publish-release step within build-release job
    build_job = workflow_config["jobs"]["build-release"]
    assert "steps" in build_job, "build-release job must have steps"

    # Find the publish step
    publish_step = None
    for step in build_job["steps"]:
        if step.get("name") == "Publish Release" or "action-gh-release" in str(
            step.get("uses", "")
        ):
            publish_step = step
            break

    assert publish_step is not None, "Must have a step that publishes the release"
    assert "if" in publish_step, "Publish step must have conditional execution"
    assert (
        "matrix.os == 'ubuntu-latest'" in publish_step["if"]
    ), "Publish step must only run on ubuntu-latest"


def test_docs_status_updated():
    """Test that docs/status.md includes the Sprint 6 – T15 completion entry."""
    status_path = Path("docs/status.md")

    with open(status_path, "r") as file:
        status_content = file.read()

    assert (
        "Sprint 6 – T15 release build workflow added" in status_content
    ), "docs/status.md must include 'Sprint 6 – T15 release build workflow added' entry"
