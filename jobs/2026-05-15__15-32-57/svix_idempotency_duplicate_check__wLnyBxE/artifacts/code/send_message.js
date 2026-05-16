const { Svix } = require("svix");

async function main() {
  // Initialize the Svix client using the SVIX_TOKEN environment variable
  const svix = new Svix(process.env.SVIX_TOKEN);

  // Create a new application with the name "Idempotency Test"
  const app = await svix.application.create({
    name: "Idempotency Test",
  });

  console.log(`Created application with ID: ${app.id}`);

  // Send a message to this application with idempotency key
  const eventType = "user.signup";
  const payload = { id: "user_123" };
  const idempotencyKey = "my-unique-key-123";

  // Send the first message
  await svix.message.create(app.id, {
    eventType,
    payload,
    options: {
      idempotencyKey,
    },
  });

  console.log("Sent first message with idempotency key");

  // Immediately send the exact same message a second time with the same idempotency key
  await svix.message.create(app.id, {
    eventType,
    payload,
    options: {
      idempotencyKey,
    },
  });

  console.log("Sent second message with same idempotency key");

  // Fetch the list of messages for the application
  const messages = await svix.message.list(app.id);

  // Print the total count of messages to output.txt
  const fs = require("fs");
  fs.writeFileSync("/home/user/app/output.txt", messages.data.length.toString());

  console.log(`Total messages: ${messages.data.length}`);
  console.log("Message count written to output.txt");
}

main().catch((error) => {
  console.error("Error:", error);
  process.exit(1);
});