"use strict";

const { Svix } = require("svix");
const fs = require("fs");
const path = require("path");

async function main() {
  const token = process.env.SVIX_AUTH_TOKEN;
  if (!token) {
    throw new Error("SVIX_AUTH_TOKEN environment variable is not set");
  }

  const svix = new Svix(token);

  // 0. Ensure a known event type exists so we can filter by it
  const eventTypeName = "webhook.event";
  console.log(`Ensuring event type '${eventTypeName}' exists...`);
  try {
    await svix.eventType.create({
      name: eventTypeName,
      description: "Generic webhook event",
    });
    console.log(`Event type '${eventTypeName}' created.`);
  } catch (err) {
    // 409 Conflict means it already exists — that's fine
    if (err.code === 409) {
      console.log(`Event type '${eventTypeName}' already exists.`);
    } else {
      throw err;
    }
  }

  // 1. Create application
  console.log("Creating application...");
  const app = await svix.application.create({ name: "Transformation App" });
  const appId = app.id;
  console.log(`Application created: ${appId}`);

  // 2. Create endpoint
  console.log("Creating endpoint...");
  const endpoint = await svix.endpoint.create(appId, {
    url: "https://example.com/webhook",
    filterTypes: [eventTypeName],
  });
  const endpointId = endpoint.id;
  console.log(`Endpoint created: ${endpointId}`);

  // 3. Apply transformation — cancel dispatch when payload.cancel_me === true
  const transformationCode = `
function handler(webhook) {
  if (webhook.payload && webhook.payload.cancel_me === true) {
    webhook.cancel = true;
  }
  return webhook;
}
`.trim();

  console.log("Applying transformation...");
  await svix.endpoint.patchTransformation(appId, endpointId, {
    enabled: true,
    code: transformationCode,
  });
  console.log("Transformation applied.");

  // 4. Write output.json
  const output = { app_id: appId, endpoint_id: endpointId };
  const outputPath = path.join(__dirname, "output.json");
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.log(`Output written to ${outputPath}`);
  console.log(JSON.stringify(output, null, 2));
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
