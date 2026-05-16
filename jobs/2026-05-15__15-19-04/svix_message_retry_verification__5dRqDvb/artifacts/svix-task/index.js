const { Svix } = require("svix");
const fs = require("fs");
const crypto = require("crypto");

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const token = process.env.SVIX_AUTH_TOKEN;
  if (!token) {
    throw new Error("SVIX_AUTH_TOKEN environment variable is not set");
  }

  const svix = new Svix(token);

  // 1. Create a new Application with a unique name and UID
  const uid = `app-${crypto.randomUUID()}`;
  console.log(`Creating application with UID: ${uid}`);
  const app = await svix.application.create({
    name: `Test App ${uid}`,
    uid: uid,
  });
  console.log(`Application created: id=${app.id}, uid=${app.uid}`);

  // 2. Create an Endpoint pointing to a non-existent server
  console.log("Creating endpoint pointing to http://localhost:9999/webhook ...");
  const endpoint = await svix.endpoint.create(app.id, {
    url: "http://localhost:9999/webhook",
    version: 1,
    description: "Test endpoint (non-existent server)",
    filterTypes: ["user.signup"],
  });
  console.log(`Endpoint created: id=${endpoint.id}`);

  // 3. Send a message with eventType "user.signup"
  console.log("Sending message with eventType: user.signup ...");
  const message = await svix.message.create(app.id, {
    eventType: "user.signup",
    payload: {
      type: "user.signup",
      data: {
        userId: `user-${crypto.randomUUID()}`,
        email: "test@example.com",
        createdAt: new Date().toISOString(),
      },
    },
  });
  console.log(`Message sent: id=${message.id}`);

  // 4. Wait a few seconds for delivery attempts to be processed
  console.log("Waiting 15 seconds for delivery attempts to be processed...");
  await sleep(15000);

  // 5. Fetch message attempts
  console.log("Fetching message attempts...");
  const attemptsResponse = await svix.messageAttempt.listByMsg(app.id, message.id);
  const attempts = attemptsResponse.data;

  console.log(`Found ${attempts.length} attempt(s)`);

  let status = null;
  if (attempts.length > 0) {
    status = attempts[0].status;
    console.log(`First attempt status: ${status} (0=Success, 1=Pending, 2=Fail, 3=Sending, 4=Canceled)`);
    console.log(`First attempt response status code: ${attempts[0].responseStatusCode}`);
  } else {
    console.log("No attempts found yet — using null for status");
  }

  // 6. Write output.json
  const output = {
    app_uid: app.uid,
    msg_id: message.id,
    status: status,
  };

  const outputPath = "/home/user/svix-task/output.json";
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.log(`\nOutput written to ${outputPath}:`);
  console.log(JSON.stringify(output, null, 2));
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
