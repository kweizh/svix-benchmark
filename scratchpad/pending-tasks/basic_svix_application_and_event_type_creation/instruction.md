You are setting up Svix to manage webhooks for a new SaaS platform.

You need to initialize the Svix Node.js SDK, create a new Application with the UID `customer-789`, and create a new Event Type named `user.signup` in a Node.js script (`setup.js`). Output the resulting Application ID and Event Type name to a `result.json` file.

**Constraints:**
- Do NOT hardcode the auth token; read it from the `SVIX_AUTH_TOKEN` environment variable.
- Use the official `svix` npm package.