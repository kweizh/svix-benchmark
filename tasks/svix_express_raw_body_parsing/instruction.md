# Fix Svix Webhook Verification in Express

## Background
Svix requires the raw, unparsed request body to verify webhook signatures. An existing Express.js application has `app.use(express.json())` configured globally, which parses the body into a JSON object and causes the Svix webhook verification to fail.

## Requirements
- Modify the Express server to properly handle Svix webhooks on the `/webhook` endpoint.
- The webhook verification must succeed using the `svix` SDK.
- The server must still be able to parse JSON bodies for other endpoints.

## Implementation Guide
1. The project is located at `/home/user/app`.
2. Review `server.js` which currently fails to verify Svix webhooks.
3. Update the `/webhook` route to use `express.raw({ type: 'application/json' })` or `body-parser.raw` to ensure `req.body` remains a raw string/buffer for this specific route, or use middleware to capture the raw body.
4. Ensure the webhook verification logic in the route works correctly with the raw body.

## Constraints
- Project path: /home/user/app
- Start command: `npm start`
- Port: 3000
- Do not break JSON parsing for other endpoints.

## Integrations
- None