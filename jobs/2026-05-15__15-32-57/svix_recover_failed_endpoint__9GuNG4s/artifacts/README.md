# Recover Failed Webhook Endpoint with Svix

This script demonstrates how to recover a failed webhook endpoint using the Svix SDK.

## Requirements

- Python 3.6 or higher
- Svix authentication token (set as `SVIX_AUTH_TOKEN` environment variable)

## Installation

The script will automatically install the `svix` package if it's not already installed.

## Usage

1. Set the `SVIX_AUTH_TOKEN` environment variable:
   ```bash
   export SVIX_AUTH_TOKEN="your_svix_auth_token_here"
   ```

2. Run the script:
   ```bash
   python recover.py
   ```

   Or execute it directly:
   ```bash
   ./recover.py
   ```

## What the Script Does

1. **Initializes the Svix client** using the `SVIX_AUTH_TOKEN` environment variable
2. **Creates a new application** named `RecoverApp`
3. **Creates a disabled endpoint** with the URL `http://failing-endpoint.local/webhook` (simulating a failed state)
4. **Updates the endpoint** to:
   - Change its URL to `http://working-endpoint.local/webhook`
   - Re-enable it (`disabled=False`)
5. **Recovers failed messages** for this endpoint since 24 hours ago

## Output

The script will output progress messages and display:
- Application ID
- Endpoint ID
- New URL
- Recovery status

## Notes

- The script requires a valid Svix authentication token
- The endpoint URLs in this example use `.local` domains for demonstration purposes
- The recovery window is set to 24 hours, but can be adjusted by modifying the `timedelta` parameter