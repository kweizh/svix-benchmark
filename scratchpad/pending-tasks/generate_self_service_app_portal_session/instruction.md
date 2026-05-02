Customers need to manage their own webhook endpoints within your application UI securely via an iframe.

You need to write a Node.js script (`portal.js`) that uses the Svix SDK to generate a short-lived App Portal session URL (magic link) for an existing Application with the UID `tenant-456`. Print only the generated URL to standard output.

**Constraints:**
- Use the official `svix` SDK and its specific portal access API methods.
- The script must read `SVIX_AUTH_TOKEN` from the environment and execute successfully using `node portal.js`.