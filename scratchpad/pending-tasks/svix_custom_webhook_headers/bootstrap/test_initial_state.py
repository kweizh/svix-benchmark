import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_svix_library_installed():
    try:
        import svix
    except ImportError:
        pytest.fail("svix Python library is not installed.")
