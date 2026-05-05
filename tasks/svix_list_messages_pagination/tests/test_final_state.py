import os
import json
import subprocess
import pytest
from svix.api import Svix

PROJECT_DIR = "/home/user/project"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "svix_task.py")
OUTPUT_JSON = os.path.join(PROJECT_DIR, "output.json")

def test_script_exists():
    assert os.path.isfile(SCRIPT_PATH), f"Script not found at {SCRIPT_PATH}"

def test_script_execution():
    result = subprocess.run(
        ["python3", "svix_task.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Script execution failed: {result.stderr}\n{result.stdout}"

def test_output_json_exists_and_valid():
    assert os.path.isfile(OUTPUT_JSON), f"Output file not found at {OUTPUT_JSON}"
    with open(OUTPUT_JSON, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            pytest.fail("output.json is not valid JSON.")
    
    assert isinstance(data, list), "output.json must contain a JSON array."
    assert len(data) >= 5, f"Expected at least 5 message IDs in output.json, got {len(data)}."

def test_messages_exist_in_svix():
    with open(OUTPUT_JSON, "r") as f:
        data = json.load(f)
    
    svix_api_key = os.environ.get("SVIX_API_KEY")
    assert svix_api_key, "SVIX_API_KEY is not set."
    
    svix = Svix(svix_api_key)
    
    # Fetch messages from the application to verify the IDs
    try:
        response = svix.message.list("test-app-pagination")
    except Exception as e:
        pytest.fail(f"Failed to list messages for 'test-app-pagination': {e}")
    
    actual_ids = [msg.id for msg in response.data]
    
    # Check if the IDs in output.json are in the actual messages
    for msg_id in data:
        # Note: since pagination might have fetched more than the first page, we should ideally check all pages.
        # But for simplicity, we can just check if we can get the message by ID.
        try:
            msg = svix.message.get("test-app-pagination", msg_id)
            assert msg.id == msg_id
        except Exception as e:
            pytest.fail(f"Message ID {msg_id} from output.json could not be fetched from Svix: {e}")
