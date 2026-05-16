from fastapi import FastAPI, Request, Response
from svix.webhooks import Webhook, WebhookVerificationError

app = FastAPI()

WEBHOOK_SECRET = "whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"


@app.post("/webhook")
async def receive_webhook(request: Request) -> Response:
    # Extract the raw body bytes — must NOT be parsed to JSON first,
    # as the signature is computed over the exact raw payload bytes.
    raw_body: bytes = await request.body()

    # Collect the three Svix signature headers.
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    # All three headers are required; reject early if any is absent.
    if not svix_id or not svix_timestamp or not svix_signature:
        return Response(
            content="Missing required Svix signature headers",
            status_code=400,
        )

    headers = {
        "svix-id": svix_id,
        "svix-timestamp": svix_timestamp,
        "svix-signature": svix_signature,
    }

    wh = Webhook(WEBHOOK_SECRET)

    try:
        # verify() raises WebhookVerificationError when the signature is invalid
        # or the timestamp is outside the accepted tolerance window.
        wh.verify(raw_body, headers)
    except WebhookVerificationError:
        return Response(
            content="Invalid webhook signature",
            status_code=400,
        )

    # Signature is valid — acknowledge receipt with 204 No Content.
    return Response(status_code=204)
