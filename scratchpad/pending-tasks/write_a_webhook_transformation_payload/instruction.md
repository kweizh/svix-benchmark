You need to modify an incoming 3rd party webhook payload before it reaches your destination endpoint, or drop it entirely based on a specific boolean flag.

You need to write a JavaScript Transformation snippet (`transform.js`) compatible with Svix's transformation engine. The script must inspect an incoming payload; if `payload.is_test` is strictly `true`, it must cancel the webhook dispatch. Otherwise, it must map the value of `payload.customer_id` to a new `payload.uid` field and delete the original `customer_id` field.

**Constraints:**
- Must conform to the standard Svix transformation environment API (e.g., using `webhook.cancel = true` for dropping events).
- Do NOT use `require` or any external Node.js modules in the script.