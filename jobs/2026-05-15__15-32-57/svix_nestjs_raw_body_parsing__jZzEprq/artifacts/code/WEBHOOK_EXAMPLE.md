# Svix Webhook Verification Implementation

This document describes how to use the Svix webhook verification endpoint.

## Endpoint

**POST** `http://localhost:3000/webhook`

## Headers

The following headers are required for Svix webhook verification:

- `svix-id`: The unique webhook ID
- `svix-timestamp`: Unix timestamp when the webhook was sent
- `svix-signature`: The cryptographic signature of the webhook payload
- `Content-Type`: Should be `application/json`

## Behavior

- **Valid Signature**: Returns HTTP 200 OK with `{ "success": true }`
- **Invalid Signature**: Returns HTTP 400 Bad Request
- **Missing Headers**: Returns HTTP 400 Bad Request

## Example Usage with Svix SDK

To test the webhook endpoint, you can use the Svix SDK to create a test webhook:

```javascript
import { Webhook } from 'svix';

const webhookSecret = 'whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ';
const wh = new Webhook(webhookSecret);

// Create a test payload
const payload = {
  event: 'user.created',
  data: {
    id: 'user_123',
    email: 'test@example.com',
  },
};

// Sign the payload
const { svixId, svixTimestamp, svixSignature } = wh.sign(JSON.stringify(payload));

// Send the webhook
const response = await fetch('http://localhost:3000/webhook', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'svix-id': svixId,
    'svix-timestamp': svixTimestamp,
    'svix-signature': svixSignature,
  },
  body: JSON.stringify(payload),
});

console.log(response.status); // 200 for valid signature, 400 for invalid
```

## Testing with curl

You can test the endpoint using curl (note: you'll need valid Svix headers):

```bash
curl -X POST http://localhost:3000/webhook \
  -H "Content-Type: application/json" \
  -H "svix-id: your_svix_id" \
  -H "svix-timestamp: your_timestamp" \
  -H "svix-signature: your_signature" \
  -d '{"event":"test","data":{}}'
```

## Implementation Details

The implementation uses a custom middleware (`RawBodyMiddleware`) to capture the raw request body before NestJS parses it as JSON. This is necessary because the Svix SDK requires the original, unparsed body for cryptographic signature verification.

The middleware only applies to the `/webhook` POST endpoint to avoid performance impact on other routes.

## Security Notes

- The webhook secret is hardcoded in this example. In production, you should store it in environment variables.
- Always verify webhook signatures before processing the payload.
- The timestamp header helps prevent replay attacks.