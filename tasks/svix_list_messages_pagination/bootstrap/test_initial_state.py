import os
import pytest

PROJECT_DIR = "/home/user/project"

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_svix_api_key_set():
    assert "SVIX_API_KEY" in os.environ, "SVIX_API_KEY environment variable is not set."

def test_svix_python_library_installed():
    try:
        import svix
    except ImportError:
        pytest.fail("svix python library is not installed.")