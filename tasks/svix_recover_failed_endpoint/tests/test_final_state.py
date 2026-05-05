import os
import pytest
from svix.api import Svix

@pytest.fixture
def svix_client():
    token = os.environ.get("SVIX_AUTH_TOKEN")
    assert token is not None, "SVIX_AUTH_TOKEN environment variable is required."
    return Svix(token)

def test_recover_app_and_endpoint_updated(svix_client):
    # 1. Retrieve the RecoverApp application
    apps_response = svix_client.application.list()
    recover_app = None
    for app in apps_response.data:
        if app.name == "RecoverApp":
            recover_app = app
            break
            
    assert recover_app is not None, "Application 'RecoverApp' was not found."
    
    # 2. Retrieve the endpoints for RecoverApp
    endpoints_response = svix_client.endpoint.list(recover_app.id)
    
    # 3. Verify that an endpoint exists with the URL http://working-endpoint.local/webhook
    working_endpoint = None
    for ep in endpoints_response.data:
        if ep.url == "http://working-endpoint.local/webhook":
            working_endpoint = ep
            break
            
    assert working_endpoint is not None, "Endpoint with URL 'http://working-endpoint.local/webhook' was not found."
    
    # 4. Verify that this endpoint is not disabled
    assert working_endpoint.disabled is False, "The endpoint is still disabled."
