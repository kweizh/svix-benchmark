# Svix Webhook Receiver with FastAPI

## Background
Svix is an enterprise-grade webhooks-as-a-service platform. When receiving webhooks from Svix, it is critical to verify the cryptographic signatures to ensure the payload is authentic and hasn't been tampered with. This task requires you to build a FastAPI webhook receiver that correctly verifies Svix signatures.

## Requirements
- Create a FastAPI application with a single POST endpoint at `/webhook`.
- The endpoint must verify incoming Svix webhook signatures using the `svix` Python library.
- The webhook secret to use is `whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw`.
- If the signature is valid, return a 204 No Content response.
- If the signature is invalid (or missing), return a 400 Bad Request response.
- You must use the raw request body for verification, as parsing it to JSON before verification will cause the signature check to fail.

## Implementation Guide
1. Initialize a Python project in `/home/user/svix_project`.
2. Install `fastapi`, `uvicorn`, and `svix`.
3. Create `main.py` containing the FastAPI application.
4. Add the `/webhook` endpoint.
5. Extract the required headers (`svix-id`, `svix-timestamp`, `svix-signature`) and the raw request body.
6. Use the `svix.Webhook` class to verify the signature.
7. Handle verification errors properly.

## Constraints
- Project path: `/home/user/svix_project`
- Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Port: 8000