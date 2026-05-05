# Svix Endpoint Secret Rotation

## Background
Svix is an enterprise-grade webhooks-as-a-service platform. When managing webhooks, rotating endpoint secrets is a critical security operation. You need to write a script that rotates the secret of a specific Svix endpoint using the official `svix` Node.js SDK.

## Requirements
- Create a Node.js script named `rotate.js` in `/home/user/project`.
- The script should use the `svix` npm package.
- The script must read the Svix authentication token from the `SVIX_AUTH_TOKEN` environment variable.
- The script must accept exactly three command-line arguments in this order: `appId`, `endpointId`, and `newSecret`.
- It should rotate the endpoint's secret to the provided `newSecret`.

## Implementation Guide
1. Initialize a Node.js project in `/home/user/project` and install `svix`.
2. Create `rotate.js`.
3. Instantiate the `Svix` client using `process.env.SVIX_AUTH_TOKEN`.
4. Read the command-line arguments: `process.argv[2]` (appId), `process.argv[3]` (endpointId), and `process.argv[4]` (newSecret).
5. Call the appropriate method on `svix.endpoint` to rotate the secret, passing `{ key: newSecret }` as the payload.

## Constraints
- Project path: `/home/user/project`
- The script must be executable via `node rotate.js <appId> <endpointId> <newSecret>`.
- Do not hardcode the auth token or the IDs.