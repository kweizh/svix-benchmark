# Svix Message Cancellation Transformation

## Background
Svix Transformations allow you to modify webhook properties in-flight by writing JavaScript code that runs on the endpoint. One advanced use case is canceling the dispatch of a webhook based on the payload content.

## Requirements
Write a Node.js script that uses the `svix` SDK to do the following:
1. Create a new Svix Application named `Transformation App`.
2. Create an Endpoint for this Application with the URL `https://example.com/webhook`.
3. Apply a Transformation to the Endpoint. The Transformation must be enabled and contain JavaScript code (`handler` function) that cancels the webhook dispatch (by setting `webhook.cancel = true`) ONLY if the payload contains a property `cancel_me` with the value `true`. If this property is not `true`, it should return the webhook unmodified.
4. Output the created Application ID and Endpoint ID to a JSON file `output.json`.

## Implementation Guide
1. Navigate to `/home/user/svix-project`.
2. Create a script named `setup.js`.
3. Initialize the Svix client using the `SVIX_AUTH_TOKEN` environment variable.
4. Use `svix.application.create()` to create the app.
5. Use `svix.endpoint.create()` to create the endpoint.
6. Use `svix.endpoint.patchTransformation()` to apply the transformation code and enable it.
7. Write the `app_id` and `endpoint_id` to `output.json` using `fs.writeFileSync`.
8. Run your script with `node setup.js`.

## Constraints
- Project path: `/home/user/svix-project`
- Log file: `/home/user/svix-project/output.json`
- Use the `svix` package installed in the project.
- The `output.json` must be valid JSON with keys `app_id` and `endpoint_id`.

## Integrations
- Svix (requires SVIX_AUTH_TOKEN environment variable)