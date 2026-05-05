from fastapi import FastAPI, Request, HTTPException, Response
from svix.webhooks import Webhook, WebhookVerificationError

app = FastAPI()

SVIX_WEBHOOK_SECRET = "whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"

@app.post("/webhook")
async def webhook(request: Request):
    # Extract headers
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    if not svix_id or not svix_timestamp or not svix_signature:
        raise HTTPException(status_code=400, detail="Missing Svix headers")

    # Get raw body
    payload = await request.body()

    # Verify signature
    try:
        wh = Webhook(SVIX_WEBHOOK_SECRET)
        wh.verify(payload, {
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": svix_signature,
        })
    except WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # If valid, return 204 No Content
    return Response(status_code=204)
