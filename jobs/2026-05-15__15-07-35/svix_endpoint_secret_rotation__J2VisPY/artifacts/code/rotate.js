const { Svix } = require("svix");

async function rotateSecret() {
  const authToken = process.env.SVIX_AUTH_TOKEN;
  if (!authToken) {
    console.error("Error: SVIX_AUTH_TOKEN environment variable is not set.");
    process.exit(1);
  }

  const appId = process.argv[2];
  const endpointId = process.argv[3];
  const newSecret = process.argv[4];

  if (!appId || !endpointId || !newSecret) {
    console.error("Usage: node rotate.js <appId> <endpointId> <newSecret>");
    process.exit(1);
  }

  const svix = new Svix(authToken);

  try {
    await svix.endpoint.rotateSecret(appId, endpointId, {
      key: newSecret,
    });
    console.log(`Successfully rotated secret for endpoint ${endpointId} in app ${appId}`);
  } catch (error) {
    console.error("Error rotating secret:", error.message || error);
    process.exit(1);
  }
}

rotateSecret();
