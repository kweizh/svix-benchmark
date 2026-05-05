import os
import json
import urllib.request
import urllib.error
import pytest

APP_UID = "routing-app-1"
API_URL = "https://api.svix.com/api/v1"

def get_headers():
    token = os.environ.get("SVIX_AUTH_TOKEN")
    assert token is not None, "SVIX_AUTH_TOKEN environment variable is not set."
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

def test_application_exists():
    req = urllib.request.Request(f"{API_URL}/app/{APP_UID}", headers=get_headers())
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200
    except urllib.error.HTTPError as e:
        pytest.fail(f"Application {APP_UID} not found: {e.code} {e.reason}")

def test_endpoints_configured():
    req = urllib.request.Request(f"{API_URL}/app/{APP_UID}/endpoint", headers=get_headers())
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            endpoints = data.get("data", [])
            assert len(endpoints) == 2, f"Expected exactly 2 endpoints, found {len(endpoints)}"
            
            e1 = next((e for e in endpoints if e["url"] == "https://endpoint1.example.com"), None)
            assert e1 is not None, "Endpoint 1 not found"
            assert "invoice.paid" in e1.get("filterTypes", []), "Endpoint 1 filter is incorrect"
            
            e2 = next((e for e in endpoints if e["url"] == "https://endpoint2.example.com"), None)
            assert e2 is not None, "Endpoint 2 not found"
            assert "user.signup" in e2.get("filterTypes", []), "Endpoint 2 filter is incorrect"
            
    except urllib.error.HTTPError as e:
        pytest.fail(f"Failed to list endpoints: {e.code} {e.reason}")

def test_messages_sent():
    req = urllib.request.Request(f"{API_URL}/app/{APP_UID}/msg", headers=get_headers())
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            messages = data.get("data", [])
            
            m1 = next((m for m in messages if m["eventType"] == "invoice.paid"), None)
            assert m1 is not None, "Message of type invoice.paid not found"
            assert m1.get("payload", {}).get("id") == "inv_123", "Payload for invoice.paid is incorrect"
            
            m2 = next((m for m in messages if m["eventType"] == "user.signup"), None)
            assert m2 is not None, "Message of type user.signup not found"
            assert m2.get("payload", {}).get("id") == "usr_456", "Payload for user.signup is incorrect"
            
    except urllib.error.HTTPError as e:
        pytest.fail(f"Failed to list messages: {e.code} {e.reason}")
