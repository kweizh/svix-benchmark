import os
import sys
from svix.api import Svix, ApplicationIn, EndpointIn

def main():
    # 2. Use the SVIX_AUTH_TOKEN environment variable to initialize the Svix client.
    auth_token = os.environ.get("SVIX_AUTH_TOKEN")
    if not auth_token:
        print("Error: SVIX_AUTH_TOKEN environment variable is not set.")
        sys.exit(1)

    svix = Svix(auth_token)

    try:
        # 1. Create a new Svix Application named "Custom Header App".
        app = svix.application.create(ApplicationIn(name="Custom Header App"))
        print(f"Created Application: {app.id}")

        # 2. Create an Endpoint for this application with the URL https://example.com/webhook/.
        # 3. Configure the endpoint to include a custom header X-Custom-Auth with the value secret-token-123.
        endpoint = svix.endpoint.create(
            app.id,
            EndpointIn(
                url="https://example.com/webhook/",
                headers={"X-Custom-Auth": "secret-token-123"}
            )
        )
        print(f"Created Endpoint: {endpoint.id} with custom headers.")

        # 4. Save the created application ID to /home/user/project/app_id.txt 
        # and the endpoint ID to /home/user/project/endpoint_id.txt.
        with open("/home/user/project/app_id.txt", "w") as f:
            f.write(app.id)
        
        with open("/home/user/project/endpoint_id.txt", "w") as f:
            f.write(endpoint.id)
        
        print("IDs saved to files.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
