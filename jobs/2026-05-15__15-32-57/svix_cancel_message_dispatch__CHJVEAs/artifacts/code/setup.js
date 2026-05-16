const { Svix } = require("svix");
const fs = require("fs");

async function main() {
  // Initialize the Svix client
  const svix = new Svix(process.env.SVIX_AUTH_TOKEN);

  // Create a new Svix Application
  const app = await svix.application.create({
    name: "Transformation App",
  });
  console.log("Created Application:", app.id);

  // Create event types first
  const eventTypes = ["user.created", "user.updated", "user.deleted"];
  for (const eventType of eventTypes) {
    try {
      await svix.eventType.create({
        name: eventType,
        description: `User ${eventType.split('.')[1]} event`,
      });
      console.log("Created Event Type:", eventType);
    } catch (error) {
      // Event type might already exist, continue
      console.log("Event Type might already exist:", eventType);
    }
  }

  // Create an Endpoint for the Application
  const endpoint = await svix.endpoint.create(app.id, {
    url: "https://example.com/webhook",
    version: 1,
    filterTypes: ["user.created", "user.updated", "user.deleted"], // Common event types
  });
  console.log("Created Endpoint:", endpoint.id);

  // Apply a Transformation to the Endpoint
  const transformation = await svix.endpoint.patchTransformation(app.id, endpoint.id, {
    enabled: true,
    code: `
      function handler(webhook) {
        // Check if payload contains cancel_me with value true
        if (webhook.payload && webhook.payload.cancel_me === true) {
          // Cancel the webhook dispatch
          webhook.cancel = true;
        }
        // Return the webhook (modified or unmodified)
        return webhook;
      }
    `,
  });
  console.log("Applied Transformation:", transformation);

  // Write the app_id and endpoint_id to output.json
  const output = {
    app_id: app.id,
    endpoint_id: endpoint.id,
  };
  fs.writeFileSync("output.json", JSON.stringify(output, null, 2));
  console.log("Output written to output.json:", output);
}

main().catch((error) => {
  console.error("Error:", error);
  if (error.body && error.body.detail) {
    console.error("Error Details:", JSON.stringify(error.body.detail, null, 2));
  }
  process.exit(1);
});