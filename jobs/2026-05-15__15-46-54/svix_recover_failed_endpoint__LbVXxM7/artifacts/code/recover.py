import os
from datetime import datetime, timezone, timedelta
from svix.api import Svix
from svix.models import ApplicationIn, EndpointIn, EndpointUpdate, RecoverIn

def main():
    token = os.environ.get("SVIX_AUTH_TOKEN")
    if not token:
        print("SVIX_AUTH_TOKEN is not set.")
        return

    svix_client = Svix(token)

    # 2. Create a new application named RecoverApp
    app = svix_client.application.create(ApplicationIn(name="RecoverApp"))
    app_id = app.id
    print(f"Created application with ID: {app_id}")

    # 3. Create a new endpoint for this application with the URL http://failing-endpoint.local/webhook and set it to be disabled (disabled=True).
    endpoint = svix_client.endpoint.create(app_id, EndpointIn(url="http://failing-endpoint.local/webhook", disabled=True))
    endpoint_id = endpoint.id
    print(f"Created disabled endpoint with ID: {endpoint_id}")

    # 4. Update this endpoint to:
    #    - Change its URL to http://working-endpoint.local/webhook.
    #    - Re-enable it (disabled=False).
    svix_client.endpoint.update(app_id, endpoint_id, EndpointUpdate(url="http://working-endpoint.local/webhook", disabled=False))
    print(f"Updated endpoint {endpoint_id} to be enabled with new URL")

    # 5. Recover the failed messages for this endpoint since 24 hours ago
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    svix_client.endpoint.recover(app_id, endpoint_id, RecoverIn(since=since))
    print(f"Triggered recovery for messages since {since}")

if __name__ == "__main__":
    main()
