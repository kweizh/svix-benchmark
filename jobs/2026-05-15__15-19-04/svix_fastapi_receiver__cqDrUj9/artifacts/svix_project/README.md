# Svix Webhook Receiver — FastAPI

## Overview
A FastAPI application that receives and cryptographically verifies Svix webhook
signatures before processing any payload.

## Project layout
```
svix_project/
└── main.py   # FastAPI application
```

## Start command
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Endpoint

| Method | Path       | Success | Failure |
|--------|------------|---------|---------|
| POST   | `/webhook` | 204     | 400     |

## Verification logic
1. Read the **raw** request body (never parse to JSON first — doing so can
   mutate whitespace and break the HMAC check).
2. Extract three required headers: `svix-id`, `svix-timestamp`, `svix-signature`.
3. Instantiate `svix.webhooks.Webhook` with the shared secret.
4. Call `wh.verify(raw_body, headers)`.
   - On success → return `204 No Content`.
   - On `WebhookVerificationError` → return `400 Bad Request`.

## Secret
`whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw`

## Dependencies
- fastapi
- uvicorn
- svix
