from fastapi import FastAPI, Request, Response, HTTPException
from svix.webhooks import Webhook, WebhookVerificationError

app = FastAPI()

# In a real production environment, this should be loaded from an environment variable
WEBHOOK_SECRET = "whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"

@app.post("/webhook")
async def webhook(request: Request):
    # Get the raw body as bytes to ensure signature verification works
    payload = await request.body()
    
    # Get Svix headers
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")
    
    # Verify presence of required headers
    if not svix_id or not svix_timestamp or not svix_signature:
        raise HTTPException(status_code=400, detail="Missing required Svix headers")
    
    wh = Webhook(WEBHOOK_SECRET)
    
    try:
        # Verify the webhook signature
        wh.verify(payload, {
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": svix_signature,
        })
    except WebhookVerificationError:
        # Return 400 Bad Request if verification fails
        raise HTTPException(status_code=400, detail="Invalid Svix signature")
    
    # Return 204 No Content for successful verification
    return Response(status_code=204)
