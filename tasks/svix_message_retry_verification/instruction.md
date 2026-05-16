# Svix Message Retry Verification

## Background
Svix handles sending webhooks and automatically retries failed deliveries. You need to write a Node.js script that uses the Svix SDK to create an application, an endpoint that points to a non-existent server, send a message, and verify that the delivery attempt failed and is queued for retry.

## Requirements
- Initialize a Node.js project in `/home/user/svix-task`.
- Install the `svix` package.
- Write a script `index.js` that:
  1. Initializes the Svix client using the `SVIX_AUTH_TOKEN` environment variable.
  2. Creates a new Application with a unique name and UID.
  3. Creates an Endpoint for that application pointing to `http://localhost:9999/webhook` (this server does not exist).
  4. Sends a message with `eventType: "user.signup"` and a payload of your choice.
  5. Waits a few seconds, then fetches the message attempts for the sent message.
  6. Writes the application UID, message ID, and the status of the first attempt to `/home/user/svix-task/output.json`. The file MUST be a JSON object with exactly these keys: `"app_uid"`, `"msg_id"`, `"status"`.

## Implementation Guide
1. `cd /home/user/svix-task` and `npm init -y`.
2. `npm install svix`.
3. Create `index.js` following the requirements.
4. Run the script with `node index.js`.

## Constraints
- Project path: /home/user/svix-task
- Output file: /home/user/svix-task/output.json
- The script must read `SVIX_AUTH_TOKEN` from the environment.