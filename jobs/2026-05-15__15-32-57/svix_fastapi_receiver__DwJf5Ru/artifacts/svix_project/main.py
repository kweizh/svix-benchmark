from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import Response
import svix

app = FastAPI()

WEBHOOK_SECRET = "whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"
wh = svix.Webhook(WEBHOOK_SECRET)


@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """
    Svix webhook receiver endpoint.
    
    Verifies incoming webhook signatures using the Svix library.
    Returns 204 No Content if signature is valid.
    Returns 400 Bad Request if signature is invalid or missing.
    """
    # Extract required headers
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    # Check if all required headers are present
    if not all([svix_id, svix_timestamp, svix_signature]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required Svix headers: svix-id, svix-timestamp, or svix-signature"
        )

    # Get raw request body (must be done before any parsing)
    raw_body = await request.body()

    try:
        # Verify the webhook signature using the raw body
        # This will raise an exception if verification fails
        wh.verify(raw_body, {
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": svix_signature
        })

        # Signature is valid, return 204 No Content
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except svix.WebhookVerificationError as e:
        # Signature verification failed
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    except Exception as e:
        # Other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook verification error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)