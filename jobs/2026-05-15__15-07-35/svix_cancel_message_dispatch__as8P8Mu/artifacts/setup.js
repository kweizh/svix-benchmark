const { Svix } = require('svix');
const fs = require('fs');

async function main() {
  const authToken = process.env.SVIX_AUTH_TOKEN;
  if (!authToken) {
    console.error('SVIX_AUTH_TOKEN environment variable is not set');
    process.exit(1);
  }

  const svix = new Svix(authToken);

  console.log('Creating application...');
  const app = await svix.application.create({
    name: 'Transformation App',
  });
  console.log(`Application created: ${app.id}`);

  console.log('Creating endpoint...');
  // Note: filterTypes is required by the server in this environment
  const endpoint = await svix.endpoint.create(app.id, {
    url: 'https://example.com/webhook',
    version: 1,
    filterTypes: ['event.test'],
  });
  console.log(`Endpoint created: ${endpoint.id}`);

  const transformationCode = `function handler(webhook) {
  if (webhook.payload.cancel_me === true) {
    webhook.cancel = true;
  }
  return webhook;
}`;

  console.log('Applying transformation...');
  await svix.endpoint.patchTransformation(app.id, endpoint.id, {
    code: transformationCode,
    enabled: true,
  });
  console.log('Transformation applied.');

  const output = {
    app_id: app.id,
    endpoint_id: endpoint.id,
  };

  fs.writeFileSync('output.json', JSON.stringify(output, null, 2));
  console.log('output.json written.');
}

main().catch(err => {
  if (err.body) {
    console.error('Error Body:', JSON.stringify(err.body, null, 2));
  } else {
    console.error('Error:', err);
  }
  process.exit(1);
});
