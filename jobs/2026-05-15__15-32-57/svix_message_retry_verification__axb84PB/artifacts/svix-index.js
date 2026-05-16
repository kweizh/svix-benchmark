const { Svix } = require("svix");
const fs = require("fs");
const path = require("path");

async function main() {
  // Get the auth token from environment variable
  const authToken = process.env.SVIX_AUTH_TOKEN;
  
  if (!authToken) {
    throw new Error("SVIX_AUTH_TOKEN environment variable is not set");
  }

  // Initialize the Svix client
  const svix = new Svix(authToken);

  console.log("Creating application...");
  
  // Create a new Application with a unique name and UID
  const uniqueId = Date.now().toString();
  const app = await svix.application.create({
    name: `svix-retry-test-${uniqueId}`,
    uid: `app-${uniqueId}`,
  });

  console.log(`Application created with UID: ${app.uid}`);

  console.log("Creating endpoint...");
  
  // Create an Endpoint for that application pointing to a non-existent server
  const endpoint = await svix.endpoint.create(app.id, {
    url: "http://localhost:9999/webhook",
    description: "Test endpoint for retry verification",
  });

  console.log(`Endpoint created: ${endpoint.url}`);

  console.log("Sending message...");
  
  // Send a message with eventType: "user.signup" and a payload
  const message = await svix.message.create(app.id, {
    eventType: "user.signup",
    payload: {
      userId: uniqueId,
      email: `test-${uniqueId}@example.com`,
      timestamp: new Date().toISOString(),
    },
  });

  console.log(`Message sent with ID: ${message.id}`);

  // Wait a few seconds for the delivery attempt to be processed
  console.log("Waiting 5 seconds for delivery attempt...");
  await new Promise(resolve => setTimeout(resolve, 5000));

  console.log("Fetching message attempts...");
  
  // Fetch the message attempts for the sent message
  const attempts = await svix.messageAttempt.list(app.id, {
    message_id: message.id,
  });

  console.log(`Found ${attempts.data.length} attempt(s)`);

  // Get the first attempt's status
  const firstAttempt = attempts.data[0];
  const status = firstAttempt ? firstAttempt.status : "unknown";

  console.log(`First attempt status: ${status}`);

  // Write the output to JSON file
  const output = {
    app_uid: app.uid,
    msg_id: message.id,
    status: status,
  };

  const outputPath = path.join(__dirname, "output.json");
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

  console.log(`Output written to ${outputPath}`);
  console.log("Done!");
}

main().catch(error => {
  console.error("Error:", error.message);
  process.exit(1);
});