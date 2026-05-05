# Recover a Failed Webhook Endpoint with Svix

## Background
You are managing webhooks for a service using Svix. You need to write a script that sets up a new application, provisions an endpoint that is initially disabled (simulating a failed state), updates it to a working URL, and triggers a recovery.

## Requirements
Write a Python script `recover.py` that uses the `svix` SDK to:
1. Initialize the Svix client using the `SVIX_AUTH_TOKEN` environment variable.
2. Create a new application named `RecoverApp`.
3. Create a new endpoint for this application with the URL `http://failing-endpoint.local/webhook` and set it to be disabled (`disabled=True`).
4. Update this endpoint to:
   - Change its URL to `http://working-endpoint.local/webhook`.
   - Re-enable it (`disabled=False`).
5. Recover the failed messages for this endpoint since 24 hours ago (you can use `datetime.now(timezone.utc) - timedelta(hours=24)` for the `since` parameter in the recover request).

## Implementation Guide
1. Install the `svix` package if it's not already installed.
2. Create `/home/user/myproject/recover.py`.
3. Use `svix_client.application.create(ApplicationIn(name="RecoverApp"))` to create the app.
4. Use `svix_client.endpoint.create(app_id, EndpointIn(url="http://failing-endpoint.local/webhook", disabled=True))`.
5. Use `svix_client.endpoint.update(app_id, endpoint_id, EndpointUpdate(url="http://working-endpoint.local/webhook", disabled=False))` to update the URL and `disabled` status.
6. Use `svix_client.endpoint.recover(app_id, endpoint_id, RecoverIn(since=...))` to recover messages.

## Constraints
- Project path: `/home/user/myproject`
- The script must be executable by running `python recover.py`.
- You must use the `svix` Python library.

## Integrations
- Svix