const fs = require("fs");
const Svix = require("svix");

async function main() {
  const token = process.env.SVIX_TOKEN;
  if (!token) {
    throw new Error("SVIX_TOKEN environment variable is required.");
  }

  const svix = new Svix(token);

  const app = await svix.application.create({
    name: "Idempotency Test",
  });

  const messageIn = {
    eventType: "user.signup",
    payload: { id: "user_123" },
  };

  const options = {
    idempotencyKey: "my-unique-key-123",
  };

  await svix.message.create(app.id, messageIn, options);
  await svix.message.create(app.id, messageIn, options);

  const messages = await svix.message.list(app.id);
  const count = messages.data.length;

  fs.writeFileSync("/home/user/app/output.txt", `${count}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
