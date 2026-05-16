const { Svix } = require("svix");

async function main() {
  const authToken = process.env.SVIX_AUTH_TOKEN;
  if (!authToken) {
    throw new Error("SVIX_AUTH_TOKEN environment variable is required.");
  }

  const appId = process.argv[2];
  const endpointId = process.argv[3];
  const newSecret = process.argv[4];

  if (!appId || !endpointId || !newSecret) {
    throw new Error(
      "Usage: node rotate.js <appId> <endpointId> <newSecret>"
    );
  }

  const svix = new Svix(authToken);
  await svix.endpoint.rotateSecret(appId, endpointId, { key: newSecret });
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
