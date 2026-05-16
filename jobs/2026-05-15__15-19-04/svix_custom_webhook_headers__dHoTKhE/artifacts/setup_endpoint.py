#!/usr/bin/env python3
"""
Sets up a Svix application and endpoint with a custom header.

Creates:
  - A Svix Application named "Custom Header App"
  - An Endpoint at https://example.com/webhook/ with the custom header
    X-Custom-Auth: secret-token-123

Writes the resulting IDs to:
  - /home/user/project/app_id.txt
  - /home/user/project/endpoint_id.txt
"""

import os
from svix import Svix
from svix.models import ApplicationIn, EndpointIn

# ---------------------------------------------------------------------------
# Initialise client
# ---------------------------------------------------------------------------
auth_token = os.environ.get("SVIX_AUTH_TOKEN")
if not auth_token:
    raise EnvironmentError("SVIX_AUTH_TOKEN environment variable is not set.")

svix = Svix(auth_token)

# ---------------------------------------------------------------------------
# 1. Create the application
# ---------------------------------------------------------------------------
app_out = svix.application.create(ApplicationIn(name="Custom Header App"))
app_id = app_out.id
print(f"Created application: {app_id}")

# ---------------------------------------------------------------------------
# 2. Create the endpoint with the custom header embedded in EndpointIn
# ---------------------------------------------------------------------------
endpoint_out = svix.endpoint.create(
    app_id,
    EndpointIn(
        url="https://example.com/webhook/",
        headers={"X-Custom-Auth": "secret-token-123"},
        filter_types=["event.created"],
    ),
)
endpoint_id = endpoint_out.id
print(f"Created endpoint: {endpoint_id}")

# ---------------------------------------------------------------------------
# 3. Persist IDs to output files
# ---------------------------------------------------------------------------
output_dir = "/home/user/project"

app_id_path = os.path.join(output_dir, "app_id.txt")
with open(app_id_path, "w") as fh:
    fh.write(app_id)
print(f"Saved application ID to {app_id_path}")

endpoint_id_path = os.path.join(output_dir, "endpoint_id.txt")
with open(endpoint_id_path, "w") as fh:
    fh.write(endpoint_id)
print(f"Saved endpoint ID to {endpoint_id_path}")
