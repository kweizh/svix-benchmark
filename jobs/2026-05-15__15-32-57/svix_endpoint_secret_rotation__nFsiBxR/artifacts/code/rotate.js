const { Svix } = require("svix");

// Read command-line arguments
const appId = process.argv[2];
const endpointId = process.argv[3];
const newSecret = process.argv[4];

// Read authentication token from environment variable
const authToken = process.env.SVIX_AUTH_TOKEN;

// Validate required inputs
if (!authToken) {
  console.error("Error: SVIX_AUTH_TOKEN environment variable is not set");
  process.exit(1);
}

if (!appId || !endpointId || !newSecret) {
  console.error("Usage: node rotate.js <appId> <endpointId> <newSecret>");
  process.exit(1);
}

// Initialize Svix client
const svix = new Svix(authToken);

// Rotate the endpoint secret
async function rotateEndpointSecret() {
  try {
    await svix.endpoint.rotateSecret(appId, endpointId, {
      key: newSecret,
    });
    console.log(`Successfully rotated secret for endpoint ${endpointId} in application ${appId}`);
  } catch (error) {
    console.error("Failed to rotate endpoint secret:", error.message);
    process.exit(1);
  }
}

rotateEndpointSecret();