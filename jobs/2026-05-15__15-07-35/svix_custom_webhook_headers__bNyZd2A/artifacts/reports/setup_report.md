# Svix Custom Webhook Headers Setup

## Overview
This task involved creating a Python script to automate the setup of a Svix application and an endpoint with custom HTTP headers.

## Implementation Details
- **Script Path**: `/home/user/project/setup_endpoint.py`
- **Library**: `svix` Python SDK
- **Application Name**: "Custom Header App"
- **Endpoint URL**: `https://example.com/webhook/`
- **Custom Header**: `X-Custom-Auth: secret-token-123`
- **Output Files**:
    - `/home/user/project/app_id.txt`
    - `/home/user/project/endpoint_id.txt`

## Script Logic
1. The script retrieves the `SVIX_AUTH_TOKEN` from environment variables.
2. It initializes the `Svix` client.
3. It creates the application using `svix.application.create`.
4. It creates the endpoint with the specified URL and custom headers using `svix.endpoint.create` and the `EndpointIn` model.
5. It saves the resulting IDs to the specified text files.

## Files Created
- `/home/user/project/setup_endpoint.py`
- `/logs/artifacts/code/setup_endpoint.py`
- `/logs/artifacts/reports/setup_report.md`
