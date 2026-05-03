import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_svix_cli_binary_available():
    assert shutil.which("svix") is not None, "svix CLI binary not found in PATH."

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_svix_auth_token_env_var_set():
    assert "SVIX_AUTH_TOKEN" in os.environ, "SVIX_AUTH_TOKEN environment variable is not set."

def test_node_and_npm_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."
    assert shutil.which("npm") is not None, "npm binary not found in PATH."
