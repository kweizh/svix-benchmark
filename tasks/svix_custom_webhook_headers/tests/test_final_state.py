import os
import subprocess
import pytest
from svix.api import Svix
from svix.internal.openapi_client.models.endpoint_headers_out import EndpointHeadersOut

PROJECT_DIR = "/home/user/project"
APP_ID_FILE = os.path.join(PROJECT_DIR, "app_id.txt")
ENDPOINT_ID_FILE = os.path.join(PROJECT_DIR, "endpoint_id.txt")

def test_script_ran_and_output_files_exist():
    # Run the setup script
    result = subprocess.run(["python3", "setup_endpoint.py"], cwd=PROJECT_DIR, capture_output=True, text=True)
    assert result.returncode == 0, f"Script failed with output: {result.stderr}"
    
    assert os.path.isfile(APP_ID_FILE), f"Output file {APP_ID_FILE} does not exist."
    assert os.path.isfile(ENDPOINT_ID_FILE), f"Output file {ENDPOINT_ID_FILE} does not exist."

def test_endpoint_configuration():
    # Read IDs
    with open(APP_ID_FILE, "r") as f:
        app_id = f.read().strip()
        
    with open(ENDPOINT_ID_FILE, "r") as f:
        endpoint_id = f.read().strip()
        
    auth_token = os.environ.get("SVIX_AUTH_TOKEN")
    assert auth_token is not None, "SVIX_AUTH_TOKEN environment variable is not set."
    
    svix = Svix(auth_token)
    
    # Get the endpoint
    endpoint = svix.endpoint.get(app_id, endpoint_id)
    assert endpoint.url == "https://example.com/webhook/", f"Expected URL https://example.com/webhook/, got {endpoint.url}"
    
    # Get the endpoint headers
    headers_out = svix.endpoint.get_headers(app_id, endpoint_id)
    headers = headers_out.headers
    
    assert headers is not None, "Headers are missing from endpoint."
    assert "X-Custom-Auth" in headers, "X-Custom-Auth header is not set on the endpoint."
    assert headers["X-Custom-Auth"] == "secret-token-123", f"Expected X-Custom-Auth to be secret-token-123, got {headers['X-Custom-Auth']}"

    # Cleanup (optional but good practice)
    try:
        svix.application.delete(app_id)
    except Exception:
        pass
