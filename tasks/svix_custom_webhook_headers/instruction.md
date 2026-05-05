# Svix Custom Webhook Headers

## Background
Svix is an enterprise-grade webhooks-as-a-service platform. When sending webhooks to endpoints, you may need to include custom HTTP headers for authentication or routing purposes.

## Requirements
- Write a Python script `/home/user/project/setup_endpoint.py` that uses the `svix` Python library to:
  1. Create a new Svix Application named "Custom Header App".
  2. Create an Endpoint for this application with the URL `https://example.com/webhook/`.
  3. Configure the endpoint to include a custom header `X-Custom-Auth` with the value `secret-token-123`.
  4. Save the created application ID to `/home/user/project/app_id.txt` and the endpoint ID to `/home/user/project/endpoint_id.txt`.

## Implementation Guide
1. Ensure you have `svix` installed (`pip install svix`).
2. Use the `SVIX_AUTH_TOKEN` environment variable to initialize the Svix client.
3. Create the application and then the endpoint, passing the headers in the endpoint configuration.
4. Write the application ID and endpoint ID to the output files.

## Constraints
- Project path: `/home/user/project`
- The script must be runnable via `python3 /home/user/project/setup_endpoint.py`.
- Output files: `/home/user/project/app_id.txt` and `/home/user/project/endpoint_id.txt`

## Integrations
- None