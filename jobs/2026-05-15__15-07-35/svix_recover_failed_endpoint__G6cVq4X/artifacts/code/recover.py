import os
from datetime import datetime, timezone, timedelta
from svix.api import Svix, ApplicationIn, EndpointIn, EndpointUpdate, RecoverIn

def main():
    # 1. Initialize the Svix client using the SVIX_AUTH_TOKEN environment variable.
    auth_token = os.environ.get("SVIX_AUTH_TOKEN")
    if not auth_token:
        print("Error: SVIX_AUTH_TOKEN environment variable is not set.")
        return

    svix_client = Svix(auth_token)

    # 2. Create a new application named RecoverApp.
    print("Creating application 'RecoverApp'...")
    app = svix_client.application.create(ApplicationIn(name="RecoverApp"))
    app_id = app.id
    print(f"Application created with ID: {app_id}")

    # 3. Create a new endpoint for this application with the URL http://failing-endpoint.local/webhook 
    # and set it to be disabled (disabled=True).
    print("Creating disabled endpoint...")
    endpoint = svix_client.endpoint.create(
        app_id, 
        EndpointIn(url="http://failing-endpoint.local/webhook", disabled=True)
    )
    endpoint_id = endpoint.id
    print(f"Endpoint created with ID: {endpoint_id}")

    # 4. Update this endpoint to:
    # - Change its URL to http://working-endpoint.local/webhook.
    # - Re-enable it (disabled=False).
    print("Updating endpoint to working URL and enabling it...")
    svix_client.endpoint.update(
        app_id, 
        endpoint_id, 
        EndpointUpdate(url="http://working-endpoint.local/webhook", disabled=False)
    )
    print("Endpoint updated successfully.")

    # 5. Recover the failed messages for this endpoint since 24 hours ago.
    print("Recovering failed messages from the last 24 hours...")
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    svix_client.endpoint.recover(
        app_id, 
        endpoint_id, 
        RecoverIn(since=since)
    )
    print("Recovery triggered successfully.")

if __name__ == "__main__":
    main()
