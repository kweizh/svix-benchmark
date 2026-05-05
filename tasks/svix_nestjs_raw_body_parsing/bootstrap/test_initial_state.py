import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/svix-nestjs-app"

def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."

def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_package_json_exists():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), f"{package_json_path} does not exist."

def test_nestjs_cli_available():
    # nest might be installed globally or locally, but let's just check if package.json has @nestjs/core
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json_path) as f:
        content = f.read()
    assert "@nestjs/core" in content, "Expected @nestjs/core in package.json."
