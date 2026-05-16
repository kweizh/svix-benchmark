const express = require('express');
const { Svix } = require('svix');
const { spawn } = require('child_process');
const fs = require('fs');

async function main() {
    const app = express();
    app.use(express.json());

    let requestCount = 0;
    
    // We'll use a simple promise-based event system to wait for requests
    let requestResolvers = [];
    const waitForNextRequest = () => new Promise(resolve => requestResolvers.push(resolve));

    app.post('/webhook', (req, res) => {
        requestCount++;
        console.log(`Received request ${requestCount}`);
        
        if (requestCount <= 2) {
            res.status(500).send('Fail');
        } else {
            res.status(200).send('OK');
        }

        if (requestResolvers.length > 0) {
            const resolve = requestResolvers.shift();
            resolve(requestCount);
        }
    });

    const server = app.listen(3000, () => {
        console.log('Server listening on port 3000');
    });

    const svixListen = spawn('svix', ['listen', 'http://localhost:3000/webhook']);

    let playUrl = null;

    svixListen.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`svix listen stdout: ${output}`);
        // Look for URL like https://play.svix.com/in/e_.../
        const match = output.match(/(https:\/\/play\.svix\.com\/in\/[a-zA-Z0-9_]+\/?)/);
        if (match && !playUrl) {
            playUrl = match[1];
            console.log(`Found play URL: ${playUrl}`);
        }
    });

    svixListen.stderr.on('data', (data) => {
        console.error(`svix listen stderr: ${data.toString()}`);
    });

    // Wait for the URL to be found
    while (!playUrl) {
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    const svix = new Svix(process.env.SVIX_AUTH_TOKEN);

    console.log('Creating application...');
    const svixApp = await svix.application.create({ name: 'Test App' });
    console.log(`Created app: ${svixApp.id}`);

    console.log('Creating endpoint...');
    const endpoint = await svix.endpoint.create(svixApp.id, { url: playUrl });
    console.log(`Created endpoint: ${endpoint.id}`);

    console.log('Sending message...');
    const msg = await svix.message.create(svixApp.id, {
        eventType: 'test.event',
        payload: { test: true }
    });
    console.log(`Created message: ${msg.id}`);

    // Wait for 1st request (failure)
    console.log('Waiting for 1st request...');
    await waitForNextRequest();
    
    // Wait a bit for the attempt to be recorded in Svix API
    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log('Resending message after 1st failure...');
    await svix.messageAttempt.resend(svixApp.id, msg.id, endpoint.id);

    // Wait for 2nd request (failure)
    console.log('Waiting for 2nd request...');
    await waitForNextRequest();

    // Wait a bit for the attempt to be recorded in Svix API
    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log('Resending message after 2nd failure...');
    await svix.messageAttempt.resend(svixApp.id, msg.id, endpoint.id);

    // Wait for 3rd request (success)
    console.log('Waiting for 3rd request...');
    await waitForNextRequest();

    console.log('Writing output.json...');
    const outputData = {
        appId: svixApp.id,
        msgId: msg.id
    };
    fs.writeFileSync('/home/user/project/output.json', JSON.stringify(outputData, null, 2));
    fs.writeFileSync('/logs/artifacts/code/output.json', JSON.stringify(outputData, null, 2));

    console.log('Cleaning up...');
    server.close();
    svixListen.kill();
    process.exit(0);
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
