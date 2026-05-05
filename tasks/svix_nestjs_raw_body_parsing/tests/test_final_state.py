import os
import subprocess
import time
import socket
import pytest
import urllib.request
import urllib.error
import json
import hmac
import hashlib
import base64

PROJECT_DIR = "/home/user/svix-nestjs-app"
SECRET = "whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(5)
    return False

def generate_svix_headers(payload_str, secret):
    msg_id = "msg_test123"
    timestamp = str(int(time.time()))
    
    # Secret is base64 encoded after "whsec_"
    secret_bytes = base64.b64decode(secret.split("_")[1])
    
    to_sign = f"{msg_id}.{timestamp}.{payload_str}".encode('utf-8')
    signature = hmac.new(secret_bytes, to_sign, hashlib.sha256).digest()
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    
    return {
        "svix-id": msg_id,
        "svix-timestamp": timestamp,
        "svix-signature": f"v1,{signature_b64}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="module")
def start_app():
    # Start the app
    process = subprocess.Popen(
        ["npm", "run", "start"],
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
    process.wait(timeout=30)

def test_valid_webhook_signature(start_app):
    payload_str = json.dumps({"test": "data"})
    headers = generate_svix_headers(payload_str, SECRET)
    
    req = urllib.request.Request(
        "http://localhost:3000/webhook",
        data=payload_str.encode('utf-8'),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200 or response.status == 201, "Expected HTTP 200 or 201 OK for valid signature."
    except urllib.error.HTTPError as e:
        pytest.fail(f"Valid signature request failed with HTTP {e.code}: {e.read().decode('utf-8')}")

def test_invalid_webhook_signature(start_app):
    payload_str = json.dumps({"test": "data"})
    headers = generate_svix_headers(payload_str, SECRET)
    # Tamper with the signature
    headers["svix-signature"] = "v1,invalid_signature_here"
    
    req = urllib.request.Request(
        "http://localhost:3000/webhook",
        data=payload_str.encode('utf-8'),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            pytest.fail(f"Expected HTTP 400 Bad Request, but got {response.status}")
    except urllib.error.HTTPError as e:
        assert e.code == 400, f"Expected HTTP 400 Bad Request, got {e.code}"
