from fastapi import FastAPI, Request, Response
from svix import Webhook, WebhookVerificationError

WEBHOOK_SECRET = "whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"

app = FastAPI()


@app.post("/webhook")
async def svix_webhook(request: Request) -> Response:
    payload = await request.body()
    headers = request.headers

    svix_id = headers.get("svix-id")
    svix_timestamp = headers.get("svix-timestamp")
    svix_signature = headers.get("svix-signature")

    if not svix_id or not svix_timestamp or not svix_signature:
        return Response(status_code=400)

    webhook = Webhook(WEBHOOK_SECRET)

    try:
        webhook.verify(
            payload,
            {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            },
        )
    except WebhookVerificationError:
        return Response(status_code=400)

    return Response(status_code=204)
