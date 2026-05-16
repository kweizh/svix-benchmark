# Svix Webhook Verification in NestJS - Implementation Guide

## Overview

This implementation provides secure webhook verification using the Svix SDK in a NestJS application. The key challenge solved is preserving the raw request body for cryptographic signature verification, as NestJS automatically parses JSON bodies.

## Architecture

```
┌─────────────────┐
│ Incoming Request│
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ RawBodyMiddleware       │
│ (Captures raw body)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ NestJS Body Parser      │
│ (Parses JSON)           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ WebhookController       │
│ (Verifies signature)    │
└─────────────────────────┘
```

## Files Created/Modified

### 1. `src/raw-body.middleware.ts`
Custom middleware that captures the raw request body before NestJS parses it. Only applies to the `/webhook` POST endpoint.

### 2. `src/webhook.controller.ts`
Controller that handles webhook verification:
- Extracts Svix headers (`svix-id`, `svix-timestamp`, `svix-signature`)
- Uses the Svix SDK to verify the signature against the raw body
- Returns 200 OK for valid signatures, 400 Bad Request for invalid ones

### 3. `src/main.ts`
Modified to apply the raw body middleware at the application level, before body parsing occurs.

### 4. `src/app.module.ts`
Updated to include the WebhookController.

### 5. `package.json`
Added `svix` dependency.

## How It Works

1. **Raw Body Capture**: The middleware intercepts requests to `/webhook` and captures the raw body stream before NestJS parses it.

2. **Body Storage**: The raw body is stored in `req.rawBody` as a Buffer.

3. **Signature Verification**: The webhook controller uses the Svix SDK to verify the signature against the raw body and headers.

4. **Response**: Returns appropriate HTTP status codes based on verification result.

## Running the Application

```bash
# Install dependencies
npm install

# Start the server
npm run start

# The server will be available at http://localhost:3000
```

## Testing

The webhook endpoint is available at `POST http://localhost:3000/webhook`.

See `WEBHOOK_EXAMPLE.md` for detailed testing examples.

## Security Considerations

1. **Environment Variables**: In production, store the webhook secret in environment variables:
   ```typescript
   private readonly webhookSecret = process.env.WEBHOOK_SECRET;
   ```

2. **HTTPS**: Always use HTTPS in production to prevent man-in-the-middle attacks.

3. **Timestamp Validation**: The Svix SDK automatically validates timestamps to prevent replay attacks.

4. **Rate Limiting**: Consider implementing rate limiting for the webhook endpoint.

## Troubleshooting

### "Raw body not available" error
- Ensure the middleware is applied before body parsing in `main.ts`
- Check that the middleware is correctly capturing the `/webhook` route

### "Invalid webhook signature" error
- Verify the webhook secret matches what's configured in Svix
- Ensure headers are being passed correctly
- Check that the raw body is not being modified

### TypeScript compilation errors
- Ensure `import type` is used for type-only imports
- Verify all dependencies are installed correctly

## Dependencies

- `@nestjs/common`: ^11.0.1
- `@nestjs/core`: ^11.0.1
- `@nestjs/platform-express`: ^11.0.1
- `svix`: Latest version

## License

This implementation is provided as-is for educational and commercial use.