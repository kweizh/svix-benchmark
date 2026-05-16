import os
import sys
from svix.api import Svix
from svix.models import ApplicationIn, EndpointIn

def main():
    token = os.environ.get("SVIX_AUTH_TOKEN")
    if not token:
        print("SVIX_AUTH_TOKEN environment variable is not set")
        sys.exit(1)

    svix = Svix(token)

    # 1. Create a new Svix Application named "Custom Header App"
    app_in = ApplicationIn(name="Custom Header App")
    app_out = svix.application.create(app_in)
    app_id = app_out.id

    # 2. Create an Endpoint for this application
    # 3. Configure the endpoint to include a custom header
    endpoint_in = EndpointIn(
        url="https://example.com/webhook/",
        headers={"X-Custom-Auth": "secret-token-123"}
    )
    endpoint_out = svix.endpoint.create(app_id, endpoint_in)
    endpoint_id = endpoint_out.id

    # 4. Save the created application ID and endpoint ID
    with open("/home/user/project/app_id.txt", "w") as f:
        f.write(app_id)
        
    with open("/home/user/project/endpoint_id.txt", "w") as f:
        f.write(endpoint_id)
        
    print(f"Created Application ID: {app_id}")
    print(f"Created Endpoint ID: {endpoint_id}")

if __name__ == "__main__":
    main()
