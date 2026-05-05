import os
import shutil
import pytest

def test_python_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."

def test_pip_available():
    assert shutil.which("pip3") is not None, "pip3 binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir("/home/user/myproject"), "Project directory /home/user/myproject does not exist."
