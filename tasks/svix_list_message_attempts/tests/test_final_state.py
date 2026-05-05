import os
import subprocess
import json
import pytest
from svix.api import Svix
from svix.models import ApplicationIn, EndpointIn, MessageIn

PROJECT_DIR = "/home/user/myproject"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "attempts.json")

@pytest.fixture(scope="module")
def setup_svix():
    token = os.environ.get("SVIX_AUTH_TOKEN")
    if not token:
        pytest.fail("SVIX_AUTH_TOKEN environment variable is not set.")
    
    svix = Svix(token)
    
    # Create application
    app_in = ApplicationIn(name="Test App")
    app = svix.application.create(app_in)
    
    # Create endpoint
    ep_in = EndpointIn(url="https://example.com/webhook", version=1)
    ep = svix.endpoint.create(app.id, ep_in)
    
    # Create message
    msg_in = MessageIn(event_type="test.event", payload={"data": "test"})
    msg = svix.message.create(app.id, msg_in)
    
    yield app.id, msg.id
    
    # Cleanup
    try:
        svix.application.delete(app.id)
    except Exception:
        pass

def test_script_execution(setup_svix):
    app_id, msg_id = setup_svix
    
    # Wait for the webhook to be attempted
    import time
    time.sleep(3)
    
    # Run the user's script
    result = subprocess.run(
        ["node", "index.js", app_id, msg_id],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Node script failed: {result.stderr}"

def test_output_file_exists_and_valid(setup_svix):
    app_id, msg_id = setup_svix
    
    assert os.path.isfile(OUTPUT_FILE), f"Output file {OUTPUT_FILE} does not exist."
    
    with open(OUTPUT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            pytest.fail("Output file does not contain valid JSON.")
    
    assert isinstance(data, list), "Output should be a JSON array."
    assert len(data) >= 1, "Expected at least one message attempt."
    assert "id" in data[0], "Attempt object should have an 'id' field."
    assert "status" in data[0], "Attempt object should have a 'status' field."
