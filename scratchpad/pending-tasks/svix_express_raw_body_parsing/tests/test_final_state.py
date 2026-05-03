import os
import subprocess
import time
import socket
import json
import pytest

PROJECT_DIR = "/home/user/app"

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module")
def start_app():
    # Start the app
    process = subprocess.Popen(
        ["npm", "start"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for the app to be ready
    if not wait_for_port(3000):
        # Kill the process group before failing
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_webhook_verification_valid_signature(start_app):
    payload = '{"test": "data"}'
    timestamp = int(time.time())
    
    # Generate signature using node and svix library
    script = f"""
    const {{ Webhook }} = require('svix');
    const wh = new Webhook('whsec_testsecret');
    const ts = new Date({timestamp} * 1000);
    const signature = wh.sign('msg_12345', ts, '{payload}');
    console.log(signature);
    """
    
    script_path = os.path.join(PROJECT_DIR, "generate_sig.js")
    with open(script_path, "w") as f:
        f.write(script)
        
    result = subprocess.run(
        ["node", "generate_sig.js"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Failed to generate signature: {result.stderr}"
    signature = result.stdout.strip()
    
    # Send request with valid signature
    curl_result = subprocess.run(
        [
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            "-X", "POST", "http://localhost:3000/webhook",
            "-H", "Content-Type: application/json",
            "-H", "svix-id: msg_12345",
            "-H", f"svix-timestamp: {timestamp}",
            "-H", f"svix-signature: {signature}",
            "-d", payload
        ],
        capture_output=True,
        text=True
    )
    
    status_code = curl_result.stdout.strip()
    assert status_code in ["200", "204"], \
        f"Expected 200 or 204 for valid webhook signature, got {status_code}"

def test_webhook_verification_invalid_signature(start_app):
    payload = '{"test": "data"}'
    timestamp = int(time.time())
    
    # Send request with invalid signature
    curl_result = subprocess.run(
        [
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            "-X", "POST", "http://localhost:3000/webhook",
            "-H", "Content-Type: application/json",
            "-H", "svix-id: msg_12345",
            "-H", f"svix-timestamp: {timestamp}",
            "-H", "svix-signature: v1,invalid_signature",
            "-d", payload
        ],
        capture_output=True,
        text=True
    )
    
    status_code = curl_result.stdout.strip()
    assert status_code == "400", \
        f"Expected 400 for invalid webhook signature, got {status_code}"

def test_other_endpoints_json_parsing(start_app):
    payload = '{"hello": "world"}'
    
    # Send request to /api/data
    curl_result = subprocess.run(
        [
            "curl", "-s", "-X", "POST", "http://localhost:3000/api/data",
            "-H", "Content-Type: application/json",
            "-d", payload
        ],
        capture_output=True,
        text=True
    )
    
    try:
        response_json = json.loads(curl_result.stdout)
        assert response_json == {"hello": "world"}, \
            f"Expected response to echo JSON, got {response_json}"
    except json.JSONDecodeError:
        pytest.fail(f"Failed to parse response as JSON. Output was: {curl_result.stdout}")
