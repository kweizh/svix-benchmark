from fastapi import FastAPI, Request, HTTPException, Response
from svix.webhooks import Webhook, WebhookVerificationError

app = FastAPI()

WHSEC = "whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"

@app.post("/webhook")
async def handle_webhook(request: Request):
    # Get the raw request body
    payload = await request.body()
    
    # Get the Svix headers
    headers = request.headers
    svix_id = headers.get("svix-id")
    svix_timestamp = headers.get("svix-timestamp")
    svix_signature = headers.get("svix-signature")
    
    # Check if the headers are present
    if not svix_id or not svix_timestamp or not svix_signature:
        raise HTTPException(status_code=400, detail="Missing svix headers")
        
    # Construct the webhook object
    try:
        wh = Webhook(WHSEC)
        # Verify the payload and headers
        wh.verify(payload, headers)
    except WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return Response(status_code=204)
