import os
import shutil
import pytest

PROJECT_DIR = "/home/user/svix-project"

def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."

def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_svix_package_installed():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), f"package.json not found in {PROJECT_DIR}."
    
    with open(package_json_path) as f:
        content = f.read()
    assert "svix" in content, "svix package is not listed in package.json."
    
    node_modules_svix = os.path.join(PROJECT_DIR, "node_modules", "svix")
    assert os.path.isdir(node_modules_svix), "svix package is not installed in node_modules."