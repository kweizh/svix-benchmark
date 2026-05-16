const { Svix } = require("svix");
const fs = require("fs");

async function run() {
  const token = process.env.SVIX_TOKEN || "test_token";
  const svix = new Svix(token);

  try {
    const app = await svix.application.create({
      name: "Idempotency Test",
    });

    const messageData = {
      eventType: "user.signup",
      payload: { id: "user_123" },
    };

    const options = {
      idempotencyKey: "my-unique-key-123",
    };

    // Send the first message
    await svix.message.create(app.id, messageData, options);

    // Send the second message with the same idempotency key
    await svix.message.create(app.id, messageData, options);

    // List messages
    const messages = await svix.message.list(app.id);

    // Write the count to output.txt
    fs.writeFileSync("/home/user/app/output.txt", messages.data.length.toString());
  } catch (error) {
    console.error(error);
    process.exit(1);
  }
}

run();
