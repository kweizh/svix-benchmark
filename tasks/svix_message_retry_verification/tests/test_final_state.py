import os
import json
import subprocess
import time
import pytest

OUTPUT_FILE = "/home/user/svix-task/output.json"

def test_output_file_exists_and_valid():
    assert os.path.isfile(OUTPUT_FILE), f"Output file {OUTPUT_FILE} does not exist."
    with open(OUTPUT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            pytest.fail(f"Output file {OUTPUT_FILE} is not valid JSON.")

    assert "app_uid" in data, "Output JSON must contain key 'app_uid' (see instruction.md)."
    assert "msg_id" in data, "Output JSON must contain key 'msg_id' (see instruction.md)."
    assert "status" in data, "Output JSON must contain key 'status' (see instruction.md)."

def test_message_attempt_failed_via_api():
    assert os.path.isfile(OUTPUT_FILE), f"Output file {OUTPUT_FILE} does not exist."
    with open(OUTPUT_FILE, "r") as f:
        data = json.load(f)

    app_id = data["app_uid"]
    msg_id = data["msg_id"]

    token = os.environ.get("SVIX_AUTH_TOKEN")
    assert token is not None, "SVIX_AUTH_TOKEN environment variable is missing"

    # Poll the Svix API until the first delivery attempt transitions out of
    # Pending (status=1). Svix's delivery pipeline can take 30-60s to mark an
    # attempt as failed when the target server is unreachable.
    # Svix MessageStatus enum: 0=Success, 1=Pending, 2=Fail, 3=Sending.
    url = f"https://api.us.svix.com/api/v1/app/{app_id}/msg/{msg_id}/attempt/"
    deadline = time.time() + 90
    attempts = []
    first_attempt = None
    while time.time() < deadline:
        result = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: Bearer {token}", url],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"curl command failed: {result.stderr}"
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Failed to parse Svix API response as JSON: {result.stdout}")
        assert "data" in response, f"Unexpected API response, missing 'data' field: {response}"
        attempts = response["data"]
        if attempts and attempts[0].get("status") not in (1, 3):
            first_attempt = attempts[0]
            break
        time.sleep(5)

    assert attempts, "No delivery attempts found for the message within timeout."
    assert first_attempt is not None, (
        f"Attempt remained Pending/Sending for 90s. Latest: {attempts[0] if attempts else None}"
    )
    status = first_attempt.get("status")
    # In Svix, status 2 means Fail, 0 means Success, 1 means Pending, 3 means Sending
    assert status == 2 or str(status).lower() == "fail", f"Expected attempt status to be failed (2), but got {status}"
