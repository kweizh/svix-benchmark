const express = require('express');
const { Svix } = require('svix');
const { spawn } = require('child_process');
const fs = require('fs');

async function run() {
    const app = express();
    app.use(express.json());

    let requestCount = 0;
    let serverInstance;

    app.post('/webhook', (req, res) => {
        requestCount++;
        console.log(`Received request #${requestCount}`);
        if (requestCount < 3) {
            console.log('Responding with 500');
            res.status(500).send('Internal Server Error');
        } else {
            console.log('Responding with 200');
            res.status(200).send('OK');
        }
    });

    serverInstance = app.listen(3000, () => {
        console.log('Server listening on port 3000');
    });

    // 2. Svix CLI Tunnel
    const svixListen = spawn('svix', ['listen', 'http://localhost:3000/webhook']);
    let publicUrl = '';

    const urlPromise = new Promise((resolve, reject) => {
        svixListen.stdout.on('data', (data) => {
            const output = data.toString();
            console.log(`Svix CLI: ${output}`);
            const match = output.match(/https:\/\/play\.svix\.com\/in\/[^\/\s]+\//);
            if (match) {
                publicUrl = match[0];
                resolve(publicUrl);
            }
        });
        svixListen.stderr.on('data', (data) => {
            console.error(`Svix CLI Error: ${data}`);
        });
        svixListen.on('error', (err) => {
            reject(err);
        });
    });

    try {
        await urlPromise;
        console.log(`Public URL: ${publicUrl}`);

        // 3. Svix SDK Setup
        const svixToken = process.env.SVIX_AUTH_TOKEN;
        if (!svixToken) {
            throw new Error('SVIX_AUTH_TOKEN is not set');
        }
        const svix = new Svix(svixToken);

        const application = await svix.application.create({ name: 'Retry Demo App' });
        console.log(`Created Application: ${application.id}`);

        const endpoint = await svix.endpoint.create(application.id, {
            url: publicUrl,
            version: 1,
            filterTypes: ['test.event']
        });
        console.log(`Created Endpoint: ${endpoint.id}`);

        const message = await svix.message.create(application.id, {
            eventType: 'test.event',
            payload: { test: true },
        });
        console.log(`Sent Message: ${message.id}`);

        // 4. Manual Retry Loop
        while (requestCount < 3) {
            console.log(`Current requestCount: ${requestCount}. Waiting for next attempt...`);
            
            // Wait for a request to come in
            const startCount = requestCount;
            while (requestCount === startCount) {
                await new Promise(r => setTimeout(r, 1000));
            }
            console.log(`Request received. New requestCount: ${requestCount}`);

            if (requestCount < 3) {
                // Wait for Svix to record the failure
                await new Promise(r => setTimeout(r, 5000));
                
                console.log(`Checking attempts for message ${message.id} in app ${application.id}`);
                try {
                    const attempts = await svix.messageAttempt.listByMsg(application.id, message.id, { limit: 1 });
                    const lastAttempt = attempts.data[0];

                    if (lastAttempt && lastAttempt.status === 2) { // 2 is Fail
                        console.log(`Attempt failed (Status: ${lastAttempt.status}). Manually resending...`);
                        await svix.messageAttempt.resend(application.id, message.id, endpoint.id);
                    } else {
                        console.log(`Last attempt status: ${lastAttempt ? lastAttempt.status : 'unknown'}. Resending anyway.`);
                        await svix.messageAttempt.resend(application.id, message.id, endpoint.id);
                    }
                } catch (retryErr) {
                    console.log('Error during attempt check/resend:', retryErr.message);
                    console.log('Retrying resend regardless...');
                    await svix.messageAttempt.resend(application.id, message.id, endpoint.id);
                }
            }
        }

        console.log('Successfully received 3rd request!');

        // 5. Execution & Output
        const output = {
            appId: application.id,
            msgId: message.id
        };
        fs.writeFileSync('/home/user/project/output.json', JSON.stringify(output, null, 2));
        console.log('Output written to /home/user/project/output.json');

    } catch (err) {
        console.error('Error during execution:', err);
        if (err.body) console.error('Error body:', JSON.stringify(err.body, null, 2));
    } finally {
        console.log('Cleaning up...');
        svixListen.kill();
        serverInstance.close();
        setTimeout(() => process.exit(0), 1000);
    }
}

run();
