# Svix Webhook Verification in NestJS

This project demonstrates how to implement Svix webhook verification in a NestJS application.

## Key Implementation Details

1.  **Raw Body Preservation**: In `src/main.ts`, the NestJS application is configured with `rawBody: true`. This is essential because Svix requires the original, unparsed raw body for signature verification.
    ```typescript
    const app = await NestFactory.create(AppModule, {
      rawBody: true,
    });
    ```

2.  **Webhook Endpoint**: A `POST /webhook` endpoint is implemented in `src/app.controller.ts`.
    - It retrieves the raw body from `req.rawBody`.
    - It extracts the necessary headers.
    - It uses the `svix` SDK's `Webhook` class to verify the signature with the provided secret.

3.  **Verification Logic**:
    ```typescript
    const wh = new Webhook(secret);
    try {
      wh.verify(payload, headers);
    } catch (err) {
      return res.status(HttpStatus.BAD_REQUEST).send({ message: 'Invalid signature' });
    }
    ```

## Files Included
- `main.ts`: Application bootstrap with raw body configuration.
- `app.controller.ts`: Webhook endpoint implementation.
- `package.json`: Dependencies including `svix`.
