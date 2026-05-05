import os
import subprocess
import time
import socket
import urllib.request
import urllib.error
import pytest

PROJECT_DIR = "/home/user/svix_project"
PORT = 8000

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
    headers = {
        "svix-id": "msg_p5jXN8AQM9LPUauROQsGsCgki",
        "svix-timestamp": "1614265330",
        "svix-signature": "v1,16j35QOozQQhF/Weskj/htVEPiAbTEo1UzMSt7pAORw=",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 204, f"Expected 204, got {response.status}"
    except urllib.error.HTTPError as e:
        pytest.fail(f"Valid request failed with status {e.code}")

def test_invalid_signature(start_app):
    url = f"http://localhost:{PORT}/webhook"
    data = b'{"test": 2432232314}'
    headers = {
        "svix-id": "msg_p5jXN8AQM9LPUauROQsGsCgki",
        "svix-timestamp": "1614265330",
        "svix-signature": "v1,invalid_signature=",
        "Content-Type": "application/json"
    }
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
