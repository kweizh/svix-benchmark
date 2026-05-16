const express = require("express");
const { spawn } = require("child_process");
const fs = require("fs");
const { Svix } = require("svix");
const EventEmitter = require("events");

const PORT = 3000;
const OUTPUT_PATH = "/home/user/project/output.json";

const events = new EventEmitter();
let receivedCount = 0;

function waitForRequestCount(targetCount) {
  if (receivedCount >= targetCount) {
    return Promise.resolve();
  }
  return new Promise((resolve) => {
    const handler = () => {
      if (receivedCount >= targetCount) {
        events.off("request", handler);
        resolve();
      }
    };
    events.on("request", handler);
  });
}

function startServer() {
  const app = express();
  app.use(express.json());

  app.post("/webhook", (req, res) => {
    receivedCount += 1;
    events.emit("request", receivedCount);

    if (receivedCount <= 2) {
      res.status(500).send("Simulated failure");
      return;
    }

    res.status(200).send("OK");
  });

  return new Promise((resolve) => {
    const server = app.listen(PORT, () => resolve(server));
  });
}

function startSvixListen() {
  const child = spawn("svix", ["listen", `http://localhost:${PORT}/webhook`], {
    stdio: ["ignore", "pipe", "pipe"],
  });

  const urlPromise = new Promise((resolve, reject) => {
    const onData = (data) => {
      const text = data.toString();
      const match = text.match(/https:\/\/play\.svix\.com\/[^\s]+\//);
      if (match) {
        child.stdout.off("data", onData);
        resolve(match[0]);
      }
    };

    child.stdout.on("data", onData);
    child.on("error", reject);
    child.stderr.on("data", (data) => {
      const text = data.toString();
      const match = text.match(/https:\/\/play\.svix\.com\/[^\s]+\//);
      if (match) {
        child.stdout.off("data", onData);
        resolve(match[0]);
      }
    });
  });

  return { child, urlPromise };
}

async function waitForAttemptStatus(svix, appId, msgId, desiredStatus) {
  while (true) {
    const attempts = await svix.messageAttempt.listByMsg(appId, msgId, { limit: 10 });
    const match = attempts.data.find((attempt) => attempt.status === desiredStatus);
    if (match) {
      return match;
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}

async function main() {
  if (!process.env.SVIX_AUTH_TOKEN) {
    throw new Error("SVIX_AUTH_TOKEN is required in the environment.");
  }

  const server = await startServer();
  const { child: svixListen, urlPromise } = startSvixListen();

  let appId;
  let msgId;

  try {
    const publicUrl = await urlPromise;
    const svix = new Svix(process.env.SVIX_AUTH_TOKEN);

    const app = await svix.application.create({ name: "Manual Retry Demo" });
    appId = app.id;

    const endpoint = await svix.endpoint.create(appId, {
      url: publicUrl,
      description: "Local tunnel endpoint",
      version: 1,
    });

    const message = await svix.message.create(appId, {
      eventType: "demo.retry",
      payload: { demo: "manual-retry" },
    });
    msgId = message.id;

    await waitForRequestCount(1);
    await waitForAttemptStatus(svix, appId, msgId, "failed");
    await svix.messageAttempt.resend(appId, msgId, endpoint.id);

    await waitForRequestCount(2);
    await waitForAttemptStatus(svix, appId, msgId, "failed");
    await svix.messageAttempt.resend(appId, msgId, endpoint.id);

    await waitForRequestCount(3);
    await waitForAttemptStatus(svix, appId, msgId, "success");

    fs.writeFileSync(OUTPUT_PATH, JSON.stringify({ appId, msgId }, null, 2));
  } finally {
    server.close();
    svixListen.kill();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
