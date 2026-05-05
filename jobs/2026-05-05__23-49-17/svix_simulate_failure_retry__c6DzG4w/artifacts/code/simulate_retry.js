const express = require('express');
const { Svix } = require('svix');
const { spawn } = require('child_process');
const fs = require('fs');

const PORT = 3000;
const SVIX_AUTH_TOKEN = process.env.SVIX_AUTH_TOKEN;

if (!SVIX_AUTH_TOKEN) {
    console.error('SVIX_AUTH_TOKEN is not set');
    process.exit(1);
}

const svix = new Svix(SVIX_AUTH_TOKEN);

let requestCount = 0;
const app = express();
app.use(express.json());

app.post('/webhook', (req, res) => {
    requestCount++;
    console.log(`Received webhook request #${requestCount}`);
    if (requestCount <= 2) {
        console.log('Responding with 500');
        res.status(500).send('Internal Server Error');
    } else {
        console.log('Responding with 200');
        res.status(200).send('OK');
    }
});

const server = app.listen(PORT, () => {
    console.log(`Express server listening on port ${PORT}`);
});

async function run() {
    let svixListenProcess;
    try {
        // 2. Svix CLI Tunnel
        console.log('Starting svix listen...');
        svixListenProcess = spawn('svix', ['listen', `http://localhost:${PORT}/webhook`]);

        let playUrl = '';
        await new Promise((resolve, reject) => {
            const timeout = setTimeout(() => reject(new Error('Timeout waiting for Play URL')), 60000);
            
            const handleData = (data) => {
                const output = data.toString();
                process.stdout.write(output); // Forward to main stdout for visibility
                const match = output.match(/https:\/\/play\.svix\.com\/in\/[^\/\s]+\//);
                if (match) {
                    playUrl = match[0];
                    clearTimeout(timeout);
                    resolve();
                }
            };

            svixListenProcess.stdout.on('data', handleData);
            svixListenProcess.stderr.on('data', handleData);
        });

        console.log(`\nObtained Play URL: ${playUrl}`);

        // 3. Svix SDK Setup
        console.log('Creating Application...');
        const svixApp = await svix.application.create({ name: `Retry Simulation ${Date.now()}` });
        const appId = svixApp.id;
        console.log(`Created Application: ${appId}`);

        console.log('Creating Endpoint...');
        const endpoint = await svix.endpoint.create(appId, {
            url: playUrl,
            version: 1,
        });
        const endpointId = endpoint.id;
        console.log(`Created Endpoint: ${endpointId}`);

        console.log('Sending Message...');
        const message = await svix.message.create(appId, {
            eventType: 'test.event',
            payload: { hello: 'world' },
        });
        const msgId = message.id;
        console.log(`Sent Message: ${msgId}`);

        // Wait a bit for the message to be processed
        await new Promise(r => setTimeout(r, 2000));

        // 4. Manual Retry Loop
        let failuresVerified = 0;
        let successDetected = false;

        while (!successDetected) {
            console.log(`Polling attempts for msg ${msgId} in app ${appId}... current requestCount: ${requestCount}`);
            
            let attempts;
            try {
                attempts = await svix.messageAttempt.listByMsg(appId, msgId);
            } catch (e) {
                console.error(`Error listing attempts: ${e.message}`);
                if (e.body) console.error(`Error body: ${JSON.stringify(e.body)}`);
                await new Promise(r => setTimeout(r, 2000));
                continue;
            }
            const failedAttempts = attempts.data.filter(a => a.status === 2); // 2 is Failure
            const successfulAttempts = attempts.data.filter(a => a.status === 0); // 0 is Success

            if (successfulAttempts.length > 0) {
                console.log('Successful attempt detected!');
                successDetected = true;
                break;
            }

            if (failedAttempts.length > failuresVerified) {
                console.log(`Detected new failed attempt (${failedAttempts.length}). Resending...`);
                await svix.messageAttempt.resend(appId, msgId, endpointId);
                failuresVerified = failedAttempts.length;
            }

            if (!successDetected) {
                await new Promise(r => setTimeout(r, 2000));
            }
        }

        // 5. Execution & Output
        console.log('Target reached. Writing output...');
        const result = { appId, msgId };
        fs.writeFileSync('/home/user/project/output.json', JSON.stringify(result, null, 2));
        console.log('Output written to /home/user/project/output.json');

    } catch (error) {
        console.error('Error during execution:', error);
    } finally {
        if (svixListenProcess) {
            console.log('Terminating svix listen process...');
            svixListenProcess.kill();
        }
        console.log('Closing server...');
        server.close();
        process.exit(0);
    }
}

run();
