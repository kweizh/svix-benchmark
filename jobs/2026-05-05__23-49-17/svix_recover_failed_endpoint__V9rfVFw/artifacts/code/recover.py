import os
from datetime import datetime, timedelta, timezone
from svix.api import Svix, ApplicationIn, EndpointIn, EndpointUpdate, RecoverIn

def main():
    auth_token = os.getenv("SVIX_AUTH_TOKEN")
    if not auth_token:
        print("Error: SVIX_AUTH_TOKEN environment variable not set.")
        # We'll exit gracefully if the token is missing for the sake of the script, 
        # though in a real scenario it might be required.
        return

    svix = Svix(auth_token)

    # 2. Create a new application named RecoverApp
    app = svix.application.create(ApplicationIn(name="RecoverApp"))
    app_id = app.id
    print(f"Created application: {app.name} (ID: {app_id})")

    # 3. Create a new endpoint for this application with the URL http://failing-endpoint.local/webhook and set it to be disabled (disabled=True)
    endpoint = svix.endpoint.create(
        app_id,
        EndpointIn(
            url="http://failing-endpoint.local/webhook",
            disabled=True
        )
    )
    endpoint_id = endpoint.id
    print(f"Created disabled endpoint: {endpoint.url} (ID: {endpoint_id})")

    # 4. Update this endpoint to:
    # - Change its URL to http://working-endpoint.local/webhook.
    # - Re-enable it (disabled=False).
    updated_endpoint = svix.endpoint.update(
        app_id,
        endpoint_id,
        EndpointUpdate(
            url="http://working-endpoint.local/webhook",
            disabled=False
        )
    )
    print(f"Updated endpoint: {updated_endpoint.url} (Disabled: {updated_endpoint.disabled})")

    # 5. Recover the failed messages for this endpoint since 24 hours ago
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    svix.endpoint.recover(
        app_id,
        endpoint_id,
        RecoverIn(since=since)
    )
    print(f"Triggered recovery since {since}")

if __name__ == "__main__":
    main()
