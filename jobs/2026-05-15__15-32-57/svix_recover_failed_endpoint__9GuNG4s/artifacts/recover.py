#!/usr/bin/env python3
"""
Recover a Failed Webhook Endpoint with Svix

This script demonstrates:
1. Creating a new application
2. Creating a disabled endpoint (simulating a failed state)
3. Updating the endpoint to a working URL
4. Recovering failed messages for the endpoint
"""

import os
from datetime import datetime, timezone, timedelta

try:
    from svix.api import (
        Svix,
        ApplicationIn,
        EndpointIn,
        EndpointUpdate,
        RecoverIn,
    )
except ImportError:
    print("Installing svix package...")
    import subprocess
    subprocess.check_call(["pip", "install", "svix"])
    from svix.api import (
        Svix,
        ApplicationIn,
        EndpointIn,
        EndpointUpdate,
        RecoverIn,
    )


def main():
    # Initialize the Svix client using the SVIX_AUTH_TOKEN environment variable
    auth_token = os.environ.get("SVIX_AUTH_TOKEN")
    if not auth_token:
        raise ValueError("SVIX_AUTH_TOKEN environment variable is not set")
    
    svix_client = Svix(auth_token)
    
    # Create a new application named "RecoverApp"
    print("Creating application 'RecoverApp'...")
    app = svix_client.application.create(ApplicationIn(name="RecoverApp"))
    app_id = app.id
    print(f"Application created with ID: {app_id}")
    
    # Create a new endpoint for this application with the failing URL and disabled status
    print("Creating disabled endpoint with failing URL...")
    endpoint = svix_client.endpoint.create(
        app_id,
        EndpointIn(
            url="http://failing-endpoint.local/webhook",
            disabled=True
        )
    )
    endpoint_id = endpoint.id
    print(f"Endpoint created with ID: {endpoint_id}")
    
    # Update the endpoint to use the working URL and re-enable it
    print("Updating endpoint to working URL and re-enabling...")
    updated_endpoint = svix_client.endpoint.update(
        app_id,
        endpoint_id,
        EndpointUpdate(
            url="http://working-endpoint.local/webhook",
            disabled=False
        )
    )
    print(f"Endpoint updated: URL={updated_endpoint.url}, disabled={updated_endpoint.disabled}")
    
    # Recover failed messages for this endpoint since 24 hours ago
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    print(f"Recovering failed messages since {since.isoformat()}...")
    
    recover_result = svix_client.endpoint.recover(
        app_id,
        endpoint_id,
        RecoverIn(since=since)
    )
    print(f"Recovery completed successfully")
    print(f"Result: {recover_result}")
    
    print("\n=== Recovery completed successfully! ===")
    print(f"Application ID: {app_id}")
    print(f"Endpoint ID: {endpoint_id}")
    print(f"New URL: {updated_endpoint.url}")
    print(f"Endpoint enabled: {not updated_endpoint.disabled}")


if __name__ == "__main__":
    main()