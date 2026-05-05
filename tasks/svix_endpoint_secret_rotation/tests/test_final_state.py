import os
import subprocess
import json
import urllib.request
import urllib.error
import secrets
import pytest

PROJECT_DIR = "/home/user/project"
API_BASE = "https://api.svix.com/api/v1"

@pytest.fixture(scope="module")
def svix_setup():
    token = os.environ.get("SVIX_AUTH_TOKEN")
    if not token:
        pytest.skip("SVIX_AUTH_TOKEN environment variable not set")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Create App
    req = urllib.request.Request(
        f"{API_BASE}/app",
        data=json.dumps({"name": "Test App for Rotation"}).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req) as response:
        app_data = json.loads(response.read().decode())
        app_id = app_data["id"]
        
    # Create Endpoint
    req = urllib.request.Request(
        f"{API_BASE}/app/{app_id}/endpoint",
        data=json.dumps({"url": "https://example.com/webhook"}).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req) as response:
        ep_data = json.loads(response.read().decode())
        endpoint_id = ep_data["id"]
        
    yield {
        "app_id": app_id,
        "endpoint_id": endpoint_id,
        "token": token,
        "headers": headers
    }
    
    # Cleanup App
    req = urllib.request.Request(
        f"{API_BASE}/app/{app_id}",
        headers=headers,
        method="DELETE"
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.URLError:
        pass

def test_rotate_script_exists():
    assert os.path.isfile(os.path.join(PROJECT_DIR, "rotate.js")), "rotate.js not found in /home/user/project"

def test_secret_rotation(svix_setup):
    app_id = svix_setup["app_id"]
    endpoint_id = svix_setup["endpoint_id"]
    headers = svix_setup["headers"]
    
    # Generate a new random secret (Svix requires secrets to be base64 strings starting with whsec_, or it handles it? Let's use a standard format or just let Svix generate one? Wait, the script takes newSecret as argument. Svix accepts any string and base64 encodes it, or requires a specific format? Let's check.)
    # Actually, Svix endpoint secrets usually start with whsec_ and are base64 encoded.
    # To be safe, we can just pass a simple string and let the SDK handle it, or pass a valid base64 string.
    # Let's use a 32-byte base64 string prefixed with whsec_
    import base64
    raw_secret = secrets.token_bytes(32)
    new_secret = "whsec_" + base64.b64encode(raw_secret).decode('utf-8')
    
    # Run the user's script
    result = subprocess.run(
        ["node", "rotate.js", app_id, endpoint_id, new_secret],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"rotate.js failed with error:\n{result.stderr}\nOutput:\n{result.stdout}"
    
    # Verify the secret via API
    req = urllib.request.Request(
        f"{API_BASE}/app/{app_id}/endpoint/{endpoint_id}/secret",
        headers=headers,
        method="GET"
    )
    with urllib.request.urlopen(req) as response:
        secret_data = json.loads(response.read().decode())
        actual_secret = secret_data["key"]
        
    assert actual_secret == new_secret, f"Expected endpoint secret to be {new_secret}, but got {actual_secret}"
