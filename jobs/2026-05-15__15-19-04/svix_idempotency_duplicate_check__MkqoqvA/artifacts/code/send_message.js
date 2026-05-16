const { Svix } = require("svix");
const fs = require("fs");

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const token = process.env.SVIX_TOKEN;
  if (!token) {
    throw new Error("SVIX_TOKEN environment variable is not set");
  }

  const svix = new Svix(token);

  // Create a new application
  const app = await svix.application.create({ name: "Idempotency Test" });
  const appId = app.id;
  console.log(`Created application: ${appId}`);

  // Add a dummy endpoint so that messages get queued and appear in the list
  await svix.endpoint.create(appId, {
    url: "https://example.com/webhook",
    filterTypes: ["user.signup"],
  });
  console.log("Created dummy endpoint");

  const messagePayload = {
    eventType: "user.signup",
    payload: { id: "user_123" },
  };

  const idempotencyKey = "my-unique-key-123";

  // Send the message the first time
  const firstMessage = await svix.message.create(appId, messagePayload, {
    idempotencyKey,
  });
  console.log(`First message sent, id: ${firstMessage.id}`);

  // Send the exact same message a second time with the same idempotency key
  const secondMessage = await svix.message.create(appId, messagePayload, {
    idempotencyKey,
  });
  console.log(`Second message sent (should be duplicate), id: ${secondMessage.id}`);

  // Both IDs should be identical due to idempotency
  console.log(`Idempotency working: ${firstMessage.id === secondMessage.id}`);

  // Wait for messages to be indexed
  await sleep(3000);

  // Fetch the list of messages for the application (retry up to 10 times)
  let totalCount = 0;
  for (let attempt = 1; attempt <= 10; attempt++) {
    const messages = await svix.message.list(appId);
    totalCount = messages.data.length;
    console.log(`Attempt ${attempt}: Total messages in application: ${totalCount}`);
    if (totalCount > 0) {
      break;
    }
    await sleep(2000);
  }

  // Write only the count to output.txt
  fs.writeFileSync("/home/user/app/output.txt", String(totalCount));
  console.log("Output written to output.txt");
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
