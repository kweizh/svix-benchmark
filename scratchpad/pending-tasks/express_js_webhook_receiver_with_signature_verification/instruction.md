You need to securely receive webhooks from a third-party service via Svix without triggering signature validation errors.

You need to create an Express.js server (`server.js`) with a `/webhook` POST endpoint that accurately verifies the incoming Svix signature by properly extracting the unparsed raw request body. Ensure the endpoint uses the `Webhook` class from the `svix` package with the secret `whsec_testsecret`, returning a `204` status on success or `400` on failure.

**Constraints:**
- Do NOT use standard `express.json()` without preserving the raw body buffer (e.g., use `body-parser` raw or Express's `verify` hook).
- The server must run and listen on port 3000.