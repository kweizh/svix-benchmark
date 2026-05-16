const { Svix } = require("svix");
const fs = require("fs");

async function main() {
  const token = process.env.SVIX_AUTH_TOKEN;
  if (!token) {
    throw new Error("SVIX_AUTH_TOKEN is required");
  }

  const svix = new Svix(token);
  const appUid = `app_${Date.now()}`;

  console.log("Creating app...");
  const app = await svix.application.create({
    name: `Test App ${appUid}`,
    uid: appUid,
  });

  console.log("Creating endpoint...");
  await svix.endpoint.create(app.id, {
    url: "http://localhost:9999/webhook",
    // let's try not setting filterTypes to see if it catches all
  }).catch(async (e) => {
    // If it fails, maybe we need filterTypes
    return await svix.endpoint.create(app.id, {
      url: "http://localhost:9999/webhook",
      filterTypes: ["user.signup"],
    });
  });

  console.log("Sending message...");
  const message = await svix.message.create(app.id, {
    eventType: "user.signup",
    payload: {
      userId: 123,
      email: "test@example.com",
    },
  });

  console.log("Message created with ID:", message.id);

  console.log("Waiting for attempts...");
  for (let i = 0; i < 10; i++) {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    console.log(`Checking attempts... (${i+1})`);
    try {
      const attempts = await svix.messageAttempt.listByMsg(app.id, message.id);
      if (attempts.data && attempts.data.length > 0) {
        console.log("Found attempts!", attempts.data[0]);
        const status = attempts.data[0].status;
        const result = {
          app_uid: appUid,
          msg_id: message.id,
          status: status,
        };
        fs.writeFileSync("/home/user/svix-task/output.json", JSON.stringify(result, null, 2));
        fs.mkdirSync("/logs/artifacts/code", { recursive: true });
        fs.copyFileSync("/home/user/svix-task/index.js", "/logs/artifacts/code/index.js");
        fs.copyFileSync("/home/user/svix-task/output.json", "/logs/artifacts/code/output.json");
        console.log("Done");
        return;
      }
    } catch (e) {
      if (e.code !== 404) {
        console.error("Error:", e.body || e);
      }
    }
  }

  console.log("No attempts found after waiting.");
}

main().catch(console.error);
