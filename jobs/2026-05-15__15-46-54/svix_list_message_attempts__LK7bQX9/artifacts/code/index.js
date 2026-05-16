const { Svix } = require('svix');
const fs = require('fs');

async function main() {
  const token = process.env.SVIX_AUTH_TOKEN;
  if (!token) {
    console.error("SVIX_AUTH_TOKEN is not set");
    process.exit(1);
  }

  const appId = process.argv[2];
  const msgId = process.argv[3];

  if (!appId || !msgId) {
    console.error("Usage: node index.js <appId> <msgId>");
    process.exit(1);
  }

  const svix = new Svix(token);

  try {
    const response = await svix.messageAttempt.listByMsg(appId, msgId);
    fs.writeFileSync('/home/user/myproject/attempts.json', JSON.stringify(response.data, null, 2));
    console.log("Successfully wrote attempts to attempts.json");
  } catch (error) {
    console.error("Error fetching message attempts:", error);
    process.exit(1);
  }
}

main();
