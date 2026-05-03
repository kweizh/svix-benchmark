import os
import json
import subprocess
import pytest

OUTPUT_FILE = "/home/user/svix-task/output.json"

def test_output_file_exists_and_valid():
    assert os.path.isfile(OUTPUT_FILE), f"Output file {OUTPUT_FILE} does not exist."
    with open(OUTPUT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            pytest.fail(f"Output file {OUTPUT_FILE} is not valid JSON.")
    
    # Check for application ID (allow various common naming conventions)
    app_keys = ["app_uid", "application_uid", "applicationId", "appId", "app_id"]
    has_app_id = any(k in data for k in app_keys)
    assert has_app_id, f"Application UID not found in output.json. Expected one of {app_keys}"
    
    # Check for message ID
    msg_keys = ["msg_id", "message_id", "messageId", "msgId"]
    has_msg_id = any(k in data for k in msg_keys)
    assert has_msg_id, f"Message ID not found in output.json. Expected one of {msg_keys}"

def test_message_attempt_failed_via_api():
    assert os.path.isfile(OUTPUT_FILE), f"Output file {OUTPUT_FILE} does not exist."
    with open(OUTPUT_FILE, "r") as f:
        data = json.load(f)
    
    app_id = next((data[k] for k in ["app_uid", "application_uid", "applicationId", "appId", "app_id"] if k in data), None)
    msg_id = next((data[k] for k in ["msg_id", "message_id", "messageId", "msgId"] if k in data), None)
    
    token = os.environ.get("SVIX_AUTH_TOKEN")
    assert token is not None, "SVIX_AUTH_TOKEN environment variable is missing"
    
    # Use curl to fetch message attempts
    cmd = [
        "curl", "-s",
        "-H", f"Authorization: Bearer {token}",
        f"https://api.svix.com/api/v1/app/{app_id}/msg/{msg_id}/attempt/"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"curl command failed: {result.stderr}"
    
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Failed to parse Svix API response as JSON: {result.stdout}")
        
    assert "data" in response, f"Unexpected API response, missing 'data' field: {response}"
    
    attempts = response["data"]
    assert len(attempts) > 0, "No delivery attempts found for the message."
    
    first_attempt = attempts[0]
    status = first_attempt.get("status")
    # In Svix, status 0 means Fail, 1 means Success, 2 means Pending
    assert status == 0 or str(status).lower() == "fail", f"Expected attempt status to be failed (0), but got {status}"
