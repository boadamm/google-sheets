"""Global pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path


# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    """Cleanup test files at the start and end of test session."""
    # Clean up at start
    test_script = Path("test_script.py")
    if test_script.exists():
        test_script.unlink()

    yield

    # Clean up at end
    if test_script.exists():
        test_script.unlink()


@pytest.fixture(autouse=True)
def clean_test_files():
    """Clean up test files before and after each test."""
    test_script = Path("test_script.py")
    if test_script.exists():
        test_script.unlink()

    yield

    if test_script.exists():
        test_script.unlink()
