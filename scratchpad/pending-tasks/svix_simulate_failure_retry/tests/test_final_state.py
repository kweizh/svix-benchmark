import os
import json
import pytest
from svix.api import Svix

PROJECT_DIR = "/home/user/project"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "output.json")

def test_output_file_exists_and_valid():
    assert os.path.isfile(OUTPUT_FILE), f"Output file {OUTPUT_FILE} does not exist."
    with open(OUTPUT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            pytest.fail("Output file is not valid JSON.")
    
    assert "appId" in data, "Output JSON is missing 'appId' field."
    assert "msgId" in data, "Output JSON is missing 'msgId' field."

def test_svix_message_attempts():
    assert "SVIX_AUTH_TOKEN" in os.environ, "SVIX_AUTH_TOKEN environment variable is missing in the verifier environment."
    
    with open(OUTPUT_FILE, "r") as f:
        data = json.load(f)
        
    app_id = data["appId"]
    msg_id = data["msgId"]
    
    svix = Svix(os.environ["SVIX_AUTH_TOKEN"])
    
    # Fetch message attempts
    try:
        attempts_response = svix.message_attempt.list_by_msg(app_id, msg_id)
    except Exception as e:
        pytest.fail(f"Failed to fetch message attempts from Svix API: {e}")
        
    attempts = attempts_response.data
    
    assert len(attempts) >= 3, f"Expected at least 3 delivery attempts, but found {len(attempts)}."
    
    # Attempts are usually returned in descending order (newest first). Let's sort by timestamp ascending to be safe.
    attempts.sort(key=lambda a: a.timestamp)
    
    first_attempt = attempts[0]
    second_attempt = attempts[1]
    final_attempt = attempts[-1]
    
    assert first_attempt.status != 0, f"Expected 1st attempt to be a failure (status != 0), but got {first_attempt.status}."
    assert second_attempt.status != 0, f"Expected 2nd attempt to be a failure (status != 0), but got {second_attempt.status}."
    assert final_attempt.status == 0, f"Expected final attempt to be a success (status 0), but got {final_attempt.status}."
