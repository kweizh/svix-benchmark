const { Svix } = require('svix');
const fs = require('fs');

async function run() {
    const svixToken = process.env.SVIX_TOKEN;
    if (!svixToken) {
        process.exit(1);
    }

    const svix = new Svix(svixToken);

    try {
        // Create a new application
        const app = await svix.application.create({
            name: 'Idempotency Test'
        });

        const messageData = {
            eventType: "user.signup",
            payload: { "id": "user_123" }
        };

        const idempotencyKey = "my-unique-key-123";

        // Send the first message
        await svix.message.create(app.id, messageData, { idempotencyKey });

        // Send the second message with the same idempotency key
        await svix.message.create(app.id, messageData, { idempotencyKey });

        // Wait a bit for the message to be processed/indexed
        await new Promise(resolve => setTimeout(resolve, 5000));

        // Fetch the list of messages for the application
        const messages = await svix.message.list(app.id);
        const count = messages.data.length;

        // Write the count to output.txt
        fs.writeFileSync('/home/user/app/output.txt', count.toString());

    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
}

run();
