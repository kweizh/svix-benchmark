import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/svix_project"

def test_node_installed():
    assert shutil.which("node") is not None, "node binary not found in PATH."

def test_npm_installed():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_svix_cli_installed():
    assert shutil.which("svix") is not None, "svix binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."
