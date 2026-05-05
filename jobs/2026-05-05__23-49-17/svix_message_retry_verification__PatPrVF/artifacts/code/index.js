const { Svix } = require('svix');
const fs = require('fs');
const path = require('path');

async function run() {
  const authToken = process.env.SVIX_AUTH_TOKEN;
  if (!authToken) {
    console.error('SVIX_AUTH_TOKEN environment variable is required');
    process.exit(1);
  }

  const svix = new Svix(authToken);

  try {
    const timestamp = Date.now();
    const appUid = `app_${timestamp}`;
    
    console.log(`Creating application with UID: ${appUid}`);
    const app = await svix.application.create({
      name: `Test Application ${timestamp}`,
      uid: appUid,
    });

    console.log(`Creating endpoint for application: ${app.id}`);
    const endpoint = await svix.endpoint.create(app.id, {
      url: 'https://localhost:9999/webhook',
      version: 1,
      description: 'Test endpoint for failure verification',
    });

    console.log('Sending message...');
    const message = await svix.message.create(app.id, {
      eventType: 'user.signup',
      payload: {
        id: 'user_123',
        username: 'testuser',
      },
    });

    console.log(`Message sent with ID: ${message.id}. Waiting for attempt...`);
    // Wait a few seconds for the delivery attempt to occur
    await new Promise(resolve => setTimeout(resolve, 5000));

    console.log('Fetching message attempts...');
    const attempts = await svix.messageAttempt.listByMsg(app.id, message.id);
    
    const firstAttemptStatus = attempts.data.length > 0 ? attempts.data[0].status : 'no attempts found';
    
    const output = {
      applicationUid: appUid,
      messageId: message.id,
      firstAttemptStatus: firstAttemptStatus,
    };

    const outputPath = path.join(__dirname, 'output.json');
    fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
    console.log(`Output written to ${outputPath}`);
    console.log(JSON.stringify(output, null, 2));

  } catch (error) {
    console.error('Error:', error.body || error.message || error);
    process.exit(1);
  }
}

run();
