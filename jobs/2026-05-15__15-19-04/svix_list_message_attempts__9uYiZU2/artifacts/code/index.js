const { Svix } = require("svix");
const fs = require("fs");

const authToken = process.env.SVIX_AUTH_TOKEN;
if (!authToken) {
  console.error("Error: SVIX_AUTH_TOKEN environment variable is not set.");
  process.exit(1);
}

const appId = process.argv[2];
const msgId = process.argv[3];

if (!appId || !msgId) {
  console.error("Usage: node index.js <appId> <msgId>");
  process.exit(1);
}

const svix = new Svix(authToken);

async function main() {
  const response = await svix.messageAttempt.listByMsg(appId, msgId);
  const data = response.data;

  fs.writeFileSync(
    "/home/user/myproject/attempts.json",
    JSON.stringify(data, null, 2)
  );

  console.log(`Written ${data.length} attempt(s) to attempts.json`);
}

main().catch((err) => {
  console.error("Error fetching message attempts:", err);
  process.exit(1);
});
