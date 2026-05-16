const { Svix } = require('svix');
const fs = require('fs');

async function run() {
    const authToken = process.env.SVIX_AUTH_TOKEN;
    if (!authToken) {
        console.error('SVIX_AUTH_TOKEN environment variable is not set');
        process.exit(1);
    }

    const svix = new Svix(authToken);
    const appUid = `app_${Date.now()}`;
    
    console.log(`Creating application with UID: ${appUid}`);
    const app = await svix.application.create({
        name: `Test App ${appUid}`,
        uid: appUid
    });

    console.log(`Creating endpoint for application: ${app.id}`);
    await svix.endpoint.create(app.id, {
        url: 'http://localhost:9999/webhook',
        version: 1,
        filterTypes: ['user.signup']
    });

    console.log(`Sending message...`);
    const msg = await svix.message.create(app.id, {
        eventType: 'user.signup',
        payload: {
            test: true,
            timestamp: new Date().toISOString()
        }
    });

    console.log(`Message sent with ID: ${msg.id}. Waiting for delivery attempt...`);
    // Wait for Svix to attempt delivery and record the failure
    await new Promise(resolve => setTimeout(resolve, 10000));

    console.log(`Fetching message attempts...`);
    const attempts = await svix.messageAttempt.listByMsg(app.id, msg.id);
    
    if (attempts.data.length === 0) {
        console.log('No attempts found yet, waiting longer...');
        await new Promise(resolve => setTimeout(resolve, 10000));
        const retryAttempts = await svix.messageAttempt.listByMsg(app.id, msg.id);
        attempts.data = retryAttempts.data;
    }

    const firstAttempt = attempts.data[0];
    const status = firstAttempt ? firstAttempt.status : 'no_attempt';

    const output = {
        app_uid: app.uid,
        msg_id: msg.id,
        status: status
    };

    const outputPath = '/home/user/svix-task/output.json';
    fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
    console.log(`Output written to ${outputPath}`);
    console.log(JSON.stringify(output, null, 2));
}

run().catch(err => {
    console.error('Error occurred:');
    if (err.body) {
        console.error(err.body);
    } else {
        console.error(err);
    }
    process.exit(1);
});
