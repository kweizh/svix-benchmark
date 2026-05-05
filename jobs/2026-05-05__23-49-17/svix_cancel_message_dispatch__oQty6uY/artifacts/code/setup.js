const { Svix } = require('svix');
const fs = require('fs');

async function run() {
    const svixToken = process.env.SVIX_AUTH_TOKEN;
    if (!svixToken) {
        console.error('SVIX_AUTH_TOKEN environment variable is not set');
        process.exit(1);
    }

    const svix = new Svix(svixToken);

    try {
        // 1. Create Application
        console.log('Creating application...');
        const app = await svix.application.create({
            name: 'Transformation App',
        });
        console.log(`Application created: ${app.id}`);

        // 2. Create Endpoint
        console.log('Creating endpoint...');
        const endpoint = await svix.endpoint.create(app.id, {
            url: 'https://example.com/webhook',
            version: 1,
        });
        console.log(`Endpoint created: ${endpoint.id}`);

        // 3. Apply Transformation
        console.log('Applying transformation...');
        const transformationCode = `
function handler(webhook) {
    if (webhook.payload && webhook.payload.cancel_me === true) {
        webhook.cancel = true;
    }
    return webhook;
}
        `.trim();

        await svix.endpoint.patchTransformation(app.id, endpoint.id, {
            code: transformationCode,
            enabled: true,
        });
        console.log('Transformation applied and enabled.');

        // 4. Output to JSON file
        const output = {
            app_id: app.id,
            endpoint_id: endpoint.id,
        };

        fs.writeFileSync('output.json', JSON.stringify(output, null, 2));
        console.log('Output written to output.json');

    } catch (error) {
        console.error('Error:', error.message);
        if (error.body) {
            console.error('Error body:', JSON.stringify(error.body, null, 2));
        }
        process.exit(1);
    }
}

run();
