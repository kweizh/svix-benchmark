const { Svix } = require('svix');

async function main() {
  const token = process.env.SVIX_AUTH_TOKEN;
  if (!token) {
    console.error('Missing SVIX_AUTH_TOKEN environment variable.');
    process.exit(1);
  }

  const appId = process.argv[2];
  const endpointId = process.argv[3];
  const newSecret = process.argv[4];

  if (!appId || !endpointId || !newSecret) {
    console.error('Usage: node rotate.js <appId> <endpointId> <newSecret>');
    process.exit(1);
  }

  const svix = new Svix(token);

  try {
    await svix.endpoint.rotateSecret(appId, endpointId, { key: newSecret });
    console.log(`Successfully rotated secret for endpoint ${endpointId} in app ${appId}`);
  } catch (error) {
    console.error('Failed to rotate secret:', error);
    process.exit(1);
  }
}

main();