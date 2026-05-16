import os
import subprocess
import time
import socket
import urllib.request
import urllib.error
import hmac
import hashlib
import base64
import pytest

PROJECT_DIR = "/home/user/svix_project"
PORT = 8000
SECRET = "whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

def generate_svix_headers(payload_bytes, secret):
    msg_id = "msg_test123"
    timestamp = str(int(time.time()))
    secret_bytes = base64.b64decode(secret.split("_")[1])
    to_sign = f"{msg_id}.{timestamp}.".encode("utf-8") + payload_bytes
    signature_b64 = base64.b64encode(
        hmac.new(secret_bytes, to_sign, hashlib.sha256).digest()
    ).decode("utf-8")
    return {
        "svix-id": msg_id,
        "svix-timestamp": timestamp,
        "svix-signature": f"v1,{signature_b64}",
        "Content-Type": "application/json",
    }

@pytest.fixture(scope="module")
def start_app():
    # Start the app
    process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(PORT)],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for the app to be ready
    if not wait_for_port(PORT):
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 8000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_valid_signature(start_app):
    url = f"http://localhost:{PORT}/webhook"
    data = b'{"test": 2432232314}'
    headers = generate_svix_headers(data, SECRET)
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 204, f"Expected 204, got {response.status}"
    except urllib.error.HTTPError as e:
        pytest.fail(f"Valid request failed with status {e.code}")

def test_invalid_signature(start_app):
    url = f"http://localhost:{PORT}/webhook"
    data = b'{"test": 2432232314}'
    headers = generate_svix_headers(data, SECRET)
    # Tamper with the signature
    headers["svix-signature"] = "v1,invalid_signature="
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            pytest.fail(f"Expected 400 Bad Request, but got {response.status}")
    except urllib.error.HTTPError as e:
        assert e.code == 400, f"Expected 400, got {e.code}"

def test_missing_headers(start_app):
    url = f"http://localhost:{PORT}/webhook"
    data = b'{"test": 2432232314}'
    headers = {
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            pytest.fail(f"Expected 400 Bad Request, but got {response.status}")
    except urllib.error.HTTPError as e:
        assert e.code == 400, f"Expected 400, got {e.code}"
