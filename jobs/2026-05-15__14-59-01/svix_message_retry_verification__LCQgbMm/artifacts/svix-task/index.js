"use strict";

const { Svix } = require("svix");
const crypto = require("crypto");
const fs = require("fs/promises");

const OUTPUT_PATH = "/home/user/svix-task/output.json";
const WEBHOOK_URL = "http://localhost:9999/webhook";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function main() {
  const authToken = process.env.SVIX_AUTH_TOKEN;
  if (!authToken) {
    throw new Error("SVIX_AUTH_TOKEN is required in the environment.");
  }

  const svix = new Svix(authToken);
  const uniqueId = crypto.randomUUID().replace(/-/g, "");
  const appUid = `app_${uniqueId}`;
  const appName = `Retry Verification ${uniqueId}`;

  const application = await svix.application.create({
    name: appName,
    uid: appUid,
  });

  const appId = application.id;

  await svix.endpoint.create(appId, {
    url: WEBHOOK_URL,
    description: "Non-existent endpoint for retry verification",
    filterTypes: ["user.signup"],
  });

  const message = await svix.message.create(appId, {
    eventType: "user.signup",
    payload: {
      userId: uniqueId,
      email: `user+${uniqueId}@example.com`,
    },
  });

  let attempts = [];
  for (let i = 0; i < 10; i += 1) {
    await delay(3000);
    try {
      const attemptResponse = await svix.messageAttempt.listByMsg(appId, message.id, {
        limit: 1,
      });
      attempts = attemptResponse.data || [];
      if (attempts.length > 0) {
        break;
      }
    } catch (error) {
      if (error && error.code === 404) {
        continue;
      }
      throw error;
    }
  }

  if (attempts.length === 0) {
    throw new Error("No message attempts were recorded for the message.");
  }

  const output = {
    app_uid: application.uid,
    msg_id: message.id,
    status: attempts[0].status,
  };

  await fs.writeFile(OUTPUT_PATH, JSON.stringify(output, null, 2));
}

main().catch((error) => {
  if (error && error.body) {
    console.error("Svix error body:", JSON.stringify(error.body, null, 2));
  }
  console.error(error);
  process.exit(1);
});
