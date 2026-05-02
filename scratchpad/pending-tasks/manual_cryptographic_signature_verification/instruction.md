A microservice written in an environment where the Svix SDK is strictly unavailable needs to verify incoming webhooks securely.

You need to implement the Svix signature verification logic manually in a Python script (`verify.py`) using the standard `hmac` and `hashlib` libraries. The script must extract the `svix-id`, `svix-timestamp`, and `svix-signature` headers, construct the signed content string (`id.timestamp.body`), base64-decode the endpoint secret, and perform a constant-time HMAC-SHA256 comparison.

**Constraints:**
- Do NOT use the `svix` SDK package or any third-party cryptography libraries.
- Explicitly handle removing the `whsec_` prefix from the secret before base64-decoding it.
- Read the payload from a local `payload.json`, headers from `headers.json`, and the secret from the `WEBHOOK_SECRET` environment variable.