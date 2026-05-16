const fs = require("fs");
const { Svix } = require("svix");

const authToken = process.env.SVIX_AUTH_TOKEN;
if (!authToken) {
  console.error("Missing SVIX_AUTH_TOKEN environment variable.");
  process.exit(1);
}

const appId = process.argv[2];
const msgId = process.argv[3];

if (!appId || !msgId) {
  console.error("Usage: node index.js <appId> <msgId>");
  process.exit(1);
}

const svix = new Svix(authToken);

async function run() {
  try {
    const response = await svix.messageAttempt.listByMsg(appId, msgId);
    fs.writeFileSync(
      "/home/user/myproject/attempts.json",
      JSON.stringify(response.data, null, 2),
      "utf8"
    );
    console.log("Wrote attempts to /home/user/myproject/attempts.json");
  } catch (error) {
    console.error("Failed to fetch message attempts:", error);
    process.exit(1);
  }
}

run();
