const { Svix } = require("svix");

const token = process.env.SVIX_AUTH_TOKEN;
if (!token) {
  console.error("Error: SVIX_AUTH_TOKEN environment variable is not set.");
  process.exit(1);
}

const appId = process.argv[2];
const endpointId = process.argv[3];
const newSecret = process.argv[4];

if (!appId || !endpointId || !newSecret) {
  console.error(
    "Usage: node rotate.js <appId> <endpointId> <newSecret>"
  );
  process.exit(1);
}

const svix = new Svix(token);

svix.endpoint
  .rotateSecret(appId, endpointId, { key: newSecret })
  .then(() => {
    console.log(
      `Secret rotated successfully for endpoint '${endpointId}' in app '${appId}'.`
    );
  })
  .catch((err) => {
    console.error("Failed to rotate secret:", err.message || err);
    process.exit(1);
  });
