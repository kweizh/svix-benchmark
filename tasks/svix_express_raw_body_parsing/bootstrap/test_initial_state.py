import os
import shutil
import pytest

PROJECT_DIR = "/home/user/app"

def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_server_js_exists():
    server_path = os.path.join(PROJECT_DIR, "server.js")
    assert os.path.isfile(server_path), f"File {server_path} does not exist."

def test_package_json_exists():
    package_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_path), f"File {package_path} does not exist."

def test_initial_express_json_configured():
    server_path = os.path.join(PROJECT_DIR, "server.js")
    with open(server_path, "r") as f:
        content = f.read()
    assert "app.use(express.json())" in content or "app.use(bodyParser.json())" in content, \
        "Expected express.json() to be configured globally in server.js."
