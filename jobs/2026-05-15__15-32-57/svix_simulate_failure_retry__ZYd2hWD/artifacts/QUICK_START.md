# Quick Start Guide

## Prerequisites Check

Before running the script, verify:

1. ✅ Node.js installed
2. ✅ `express` and `svix` npm packages installed
3. ✅ `svix` CLI binary installed
4. ❌ `SVIX_AUTH_TOKEN` environment variable set

## Running the Script

```bash
# Set your Svix auth token (replace with your actual token)
export SVIX_AUTH_TOKEN="your_auth_token_here"

# Navigate to the project directory
cd /home/user/project

# Run the script
node simulate_retry.js
```

## Expected Console Output

```
Express server started on port 3000
Starting svix listen process...
[svix listen] Listening on https://play.svix.com/in/abc123/
Found public URL: https://play.svix.com/in/abc123
Creating Application...
Application created: app_xxxxx
Creating Endpoint...
Endpoint created: ep_xxxxx
Sending Message...
Message sent: msg_xxxxx
Waiting for request #1...
[2025-05-15T22:33:59.000Z] Received request #1
[2025-05-15T22:33:59.000Z] Request #1 - Responding with 500
Latest attempt status: Failure, responseStatusCode: 500
Attempt failed as expected. Manually resending...
Message resent successfully
Waiting for request #2...
[2025-05-15T22:34:00.000Z] Received request #2
[2025-05-15T22:34:00.000Z] Request #2 - Responding with 500
Latest attempt status: Failure, responseStatusCode: 500
Attempt failed as expected. Manually resending...
Message resent successfully
Waiting for request #3...
[2025-05-15T22:34:01.000Z] Received request #3
[2025-05-15T22:34:01.000Z] Request #3 - Responding with 200
Latest attempt status: Success, responseStatusCode: 200
Attempt succeeded!
Writing output to output.json...
Output written to /home/user/project/output.json
Cleaning up...
Express server closed
svix listen process terminated
Done!
```

## Output File

After successful execution, check `/home/user/project/output.json`:

```json
{
  "appId": "app_xxxxxxxxxxxxx",
  "msgId": "msg_xxxxxxxxxxxxx"
}
```

## Troubleshooting

### "SVIX_AUTH_TOKEN environment variable is not set"
Set the environment variable before running:
```bash
export SVIX_AUTH_TOKEN="your_token_here"
```

### "Timeout: Could not extract public URL from svix listen"
- Ensure the `svix` CLI is installed and accessible
- Check network connectivity
- Verify the svix CLI can authenticate with your token

### "Failed to start svix listen"
- Ensure port 3000 is available
- Check that the svix CLI is properly installed
- Verify your SVIX_AUTH_TOKEN is valid

## Notes

- The script automatically cleans up by terminating both the Express server and the svix listen process
- The script will exit with code 1 if any error occurs
- All logs are printed to console for debugging