# Svix Webhook Failure and Manual Retry Simulation

This script demonstrates the Svix webhook failure and manual retry mechanism.

## Overview

The script `/home/user/project/simulate_retry.js`:

1. **Local Server**: Starts an Express server on port 3000 with a `POST /webhook` endpoint that:
   - Returns HTTP 500 for the first 2 requests (simulating failure)
   - Returns HTTP 200 for the 3rd request (success)

2. **Svix CLI Tunnel**: Spawns the `svix listen` command to create a public tunnel to the local server

3. **Svix SDK Setup**: Uses the Svix Node.js SDK to:
   - Create a new Application
   - Create an Endpoint using the public URL from the tunnel
   - Send a Message to the Application

4. **Manual Retry Loop**: Monitors delivery attempts and manually resends failed messages:
   - Detects when the local server responds with 500
   - Uses `svix.messageAttempt.resend()` to immediately retry
   - Continues until the 3rd attempt succeeds with HTTP 200

5. **Output**: Writes the Application ID and Message ID to `/home/user/project/output.json`

## Prerequisites

- Node.js with `express` and `svix` packages installed
- `svix` CLI binary installed
- `SVIX_AUTH_TOKEN` environment variable set

## Running the Script

```bash
cd /home/user/project
node simulate_retry.js
```

## Expected Output

The script will:
1. Start the Express server
2. Launch the svix listen tunnel
3. Create an Application and Endpoint
4. Send a message
5. Monitor the first attempt (fails with 500)
6. Manually resend the message
7. Monitor the second attempt (fails with 500)
8. Manually resend again
9. Monitor the third attempt (succeeds with 200)
10. Write the output to `/home/user/project/output.json`
11. Clean up and terminate both processes

## Output Format

The output file `/home/user/project/output.json` contains:

```json
{
  "appId": "app_123...",
  "msgId": "msg_123..."
}
```

## Key Components

- **Express Server**: Handles incoming webhook requests with failure simulation
- **svix listen**: Creates a public tunnel to the local server
- **Svix SDK**: Interacts with the Svix API for Application, Endpoint, and Message management
- **Manual Retry Logic**: Uses `messageAttempt.listByMsg()` and `messageAttempt.resend()` to manually retry failed messages
- **Cleanup**: Properly terminates both the server and the svix listen process