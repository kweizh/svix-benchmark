# Svix Idempotency Duplicate Check

## Background
When sending webhooks, network failures can cause retries, which might lead to duplicate messages if not handled correctly. Svix supports idempotency keys to ensure that a message is only processed once even if the request is retried.

## Requirements
Write a Node.js script `send_message.js` that demonstrates Svix's idempotency feature by sending a duplicate message and verifying that only one message is actually created.

## Implementation Guide
1. Initialize a Node.js project in `/home/user/app`.
2. Install the `svix` package.
3. Create `send_message.js` that:
   - Initializes the `Svix` client using the `SVIX_TOKEN` environment variable.
   - Creates a new application with the name `Idempotency Test`.
   - Sends a message to this application with `eventType: "user.signup"` and `payload: { "id": "user_123" }`.
   - Crucially, pass an `idempotencyKey` of `"my-unique-key-123"` in the options object when creating the message.
   - Immediately send the exact same message a second time, using the exact same `idempotencyKey`.
   - Fetch the list of messages for the application and print the total count of messages to a file `output.txt`.

## Constraints
- Project path: `/home/user/app`
- The output file must be `/home/user/app/output.txt` and contain only the number `1` (since the second request should be safely ignored due to the idempotency key).
- Use the `svix` npm package.