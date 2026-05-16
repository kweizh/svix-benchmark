const fs = require("fs");
const svix = require("svix");

const authToken = process.env.SVIX_AUTH_TOKEN;
if (!authToken) {
  console.error("SVIX_AUTH_TOKEN environment variable is required.");
  process.exit(1);
}

const client = new svix.Svix(authToken);

const transformationCode = `function handler(webhook) {
  if (webhook.payload && webhook.payload.cancel_me === true) {
    webhook.cancel = true;
  }
  return webhook;
}`;

async function main() {
  const app = await client.application.create({
    name: "Transformation App",
  });

  const eventTypeName = "event.test";
  await client.eventType.create({
    name: eventTypeName,
    description: "Test event type for transformations",
  });

  const endpoint = await client.endpoint.create(app.id, {
    url: "https://example.com/webhook",
    filterTypes: [eventTypeName],
  });

  await client.endpoint.patchTransformation(app.id, endpoint.id, {
    enabled: true,
    code: transformationCode,
  });

  const output = {
    app_id: app.id,
    endpoint_id: endpoint.id,
  };

  fs.writeFileSync("/home/user/svix-project/output.json", JSON.stringify(output, null, 2));
  console.log("Created resources:", output);
}

main().catch((error) => {
  console.error("Setup failed:", error);
  if (error && error.body) {
    console.error("Error body:", JSON.stringify(error.body, null, 2));
  }
  process.exit(1);
});
