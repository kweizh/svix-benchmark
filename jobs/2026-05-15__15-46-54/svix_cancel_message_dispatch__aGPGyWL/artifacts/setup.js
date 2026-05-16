const { Svix } = require("svix");
const fs = require("fs");

async function main() {
    const svix = new Svix(process.env.SVIX_AUTH_TOKEN);

    try {
        const app = await svix.application.create({
            name: "Transformation App"
        });

        // Try creating an event type first
        await svix.eventType.create({
            name: "user.created",
            description: "User created"
        }).catch(() => {}); // ignore if exists

        const endpoint = await svix.endpoint.create(app.id, {
            url: "https://example.com/webhook",
            filterTypes: ["user.created"]
        });

        const transformationCode = `
function handler(webhook) {
  if (webhook.payload && webhook.payload.cancel_me === true) {
    webhook.cancel = true;
  }
  return webhook;
}
`;

        await svix.endpoint.patchTransformation(app.id, endpoint.id, {
            code: transformationCode,
            enabled: true
        });

        const output = {
            app_id: app.id,
            endpoint_id: endpoint.id
        };

        fs.writeFileSync("/home/user/svix-project/output.json", JSON.stringify(output, null, 2));
        
        fs.mkdirSync("/logs/artifacts", { recursive: true });
        fs.writeFileSync("/logs/artifacts/output.json", JSON.stringify(output, null, 2));
        fs.writeFileSync("/logs/artifacts/setup.js", fs.readFileSync(__filename));
    } catch (err) {
        if (err.body) {
            console.error("API Error Body:", JSON.stringify(err.body, null, 2));
        } else {
            console.error(err);
        }
        process.exit(1);
    }
}

main();
