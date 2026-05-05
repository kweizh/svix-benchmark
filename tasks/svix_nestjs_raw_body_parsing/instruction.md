# Svix Webhook Verification in NestJS

## Background
Svix is an enterprise-grade webhooks-as-a-service platform. To verify incoming webhooks securely, the Svix SDK requires the original, unparsed raw body of the HTTP request along with the headers. However, web frameworks like NestJS automatically parse JSON bodies, making it difficult to retrieve the raw body needed for cryptographic signature verification.

## Requirements
- You have a basic NestJS project at `/home/user/svix-nestjs-app`.
- Create a POST endpoint `/webhook`.
- The endpoint must use the `svix` Node.js SDK to verify incoming webhook payloads.
- The endpoint must correctly handle raw body parsing to allow `Webhook.verify(payload, headers)` to succeed.
- The endpoint secret is `whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ`.
- If the signature is valid, return an HTTP 200 OK.
- If the signature is invalid, return an HTTP 400 Bad Request.

## Implementation Guide
1. Go to `/home/user/svix-nestjs-app`.
2. Install the `svix` SDK.
3. Configure NestJS to preserve the raw body for the `/webhook` route (e.g., using middleware or modifying the main bootstrap configuration to store the raw body).
4. Implement the `/webhook` endpoint in the controller.
5. Use the `svix` SDK's `Webhook` class with the secret `whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ` to verify the `svix-id`, `svix-timestamp`, and `svix-signature` headers against the raw body.

## Constraints
- Project path: `/home/user/svix-nestjs-app`
- Start command: `npm run start`
- Port: 3000
- The endpoint must be accessible at `POST http://localhost:3000/webhook`.