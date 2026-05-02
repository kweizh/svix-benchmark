You need an automated way to detect when customer webhook endpoints in your Svix environment are continuously failing or being deleted.

You need to write a Node.js script (`monitor.js`) using the Svix SDK that sets up an Operational Webhook. The script must create an endpoint strictly dedicated to listening to the `endpoint.disabled` and `endpoint.deleted` operational event types, directing these operational webhooks to `https://monitor.example.com/alerts`.

**Constraints:**
- Ensure the endpoint is created as an Operational Webhook using the correct operational API namespace, NOT as a standard application webhook.
- Read the Svix Auth Token from the `SVIX_AUTH_TOKEN` environment variable.