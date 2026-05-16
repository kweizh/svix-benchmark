import { Svix } from "svix";
import fs from "fs";

// Get the auth token from environment variable
const authToken = process.env.SVIX_AUTH_TOKEN;

if (!authToken) {
  console.error("Error: SVIX_AUTH_TOKEN environment variable is not set");
  process.exit(1);
}

// Get appId and msgId from command line arguments
const appId = process.argv[2];
const msgId = process.argv[3];

if (!appId) {
  console.error("Error: appId is required as first argument");
  console.error("Usage: node index.js <appId> <msgId>");
  process.exit(1);
}

if (!msgId) {
  console.error("Error: msgId is required as second argument");
  console.error("Usage: node index.js <appId> <msgId>");
  process.exit(1);
}

try {
  // Initialize Svix client
  const svix = new Svix(authToken);

  // List message attempts for the given message
  const attempts = await svix.messageAttempt.listByMsg(appId, msgId);

  // Write the data array to JSON file
  fs.writeFileSync(
    "/home/user/myproject/attempts.json",
    JSON.stringify(attempts.data, null, 2)
  );

  console.log(`Successfully wrote ${attempts.data.length} attempts to attempts.json`);
} catch (error) {
  console.error("Error fetching message attempts:", error.message);
  process.exit(1);
}