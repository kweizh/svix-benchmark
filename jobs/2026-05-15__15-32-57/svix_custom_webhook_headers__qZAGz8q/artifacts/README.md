# Svix Custom Webhook Headers Setup

This script sets up a Svix application with an endpoint that includes custom HTTP headers.

## Prerequisites

1. Install the Svix Python library:
   ```bash
   pip install svix
   ```

2. Set the `SVIX_AUTH_TOKEN` environment variable with your Svix API token:
   ```bash
   export SVIX_AUTH_TOKEN="your_auth_token_here"
   ```

## Usage

Run the script:
```bash
python3 /home/user/project/setup_endpoint.py
```

## What the script does

1. Creates a new Svix Application named "Custom Header App"
2. Creates an Endpoint for this application with URL `https://example.com/webhook/`
3. Configures the endpoint to include a custom header:
   - Header: `X-Custom-Auth`
   - Value: `secret-token-123`
4. Saves the application ID to `app_id.txt`
5. Saves the endpoint ID to `endpoint_id.txt`

## Output Files

- `app_id.txt` - Contains the ID of the created application
- `endpoint_id.txt` - Contains the ID of the created endpoint

## Notes

- The script requires a valid `SVIX_AUTH_TOKEN` to authenticate with the Svix API
- Custom headers can be modified in the script to suit your authentication or routing needs
- The endpoint URL can be changed to your actual webhook endpoint