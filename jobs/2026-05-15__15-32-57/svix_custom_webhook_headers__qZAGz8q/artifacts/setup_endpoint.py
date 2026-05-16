#!/usr/bin/env python3
"""
Svix Custom Webhook Headers Setup Script

This script creates a Svix application and endpoint with custom HTTP headers
for authentication or routing purposes.
"""

import os
import sys

try:
    from svix.api import Svix, ApplicationIn, EndpointIn, EndpointHeadersIn
except ImportError:
    print("Error: svix library not installed. Please run: pip install svix")
    sys.exit(1)


def main():
    """Main function to create Svix application and endpoint with custom headers."""
    
    # Get the auth token from environment variable
    auth_token = os.getenv("SVIX_AUTH_TOKEN")
    if not auth_token:
        print("Error: SVIX_AUTH_TOKEN environment variable not set")
        sys.exit(1)
    
    # Initialize the Svix client
    client = Svix(auth_token=auth_token)
    
    # Create a new application
    print("Creating application 'Custom Header App'...")
    app = client.application.create(
        ApplicationIn(name="Custom Header App")
    )
    print(f"Application created with ID: {app.id}")
    
    # Create endpoint with custom headers
    print(f"Creating endpoint with URL: https://example.com/webhook/")
    endpoint = client.endpoint.create(
        app.id,
        EndpointIn(
            url="https://example.com/webhook/",
            headers=EndpointHeadersIn(
                http_headers={"X-Custom-Auth": "secret-token-123"}
            )
        )
    )
    print(f"Endpoint created with ID: {endpoint.id}")
    
    # Save application ID to file
    app_id_path = "/home/user/project/app_id.txt"
    with open(app_id_path, "w") as f:
        f.write(app.id)
    print(f"Application ID saved to: {app_id_path}")
    
    # Save endpoint ID to file
    endpoint_id_path = "/home/user/project/endpoint_id.txt"
    with open(endpoint_id_path, "w") as f:
        f.write(endpoint.id)
    print(f"Endpoint ID saved to: {endpoint_id_path}")
    
    print("\nSetup completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())