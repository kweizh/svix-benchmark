const express = require('express');
const { spawn } = require('child_process');
const { Svix } = require('svix');
const fs = require('fs');
const path = require('path');

// Global request counter
let requestCounter = 0;
let server = null;
let svixProcess = null;

// Express app
const app = express();
app.use(express.json());

// Webhook endpoint
app.post('/webhook', (req, res) => {
  requestCounter++;
  console.log(`[${new Date().toISOString()}] Received request #${requestCounter}`);
  
  if (requestCounter <= 2) {
    console.log(`[${new Date().toISOString()}] Request #${requestCounter} - Responding with 500`);
    res.status(500).send({ error: 'Internal Server Error' });
  } else {
    console.log(`[${new Date().toISOString()}] Request #${requestCounter} - Responding with 200`);
    res.status(200).send({ success: true });
  }
});

// Start Express server
async function startServer() {
  return new Promise((resolve) => {
    server = app.listen(3000, () => {
      console.log('Express server started on port 3000');
      resolve();
    });
  });
}

// Start svix listen process
async function startSvixListen() {
  return new Promise((resolve, reject) => {
    console.log('Starting svix listen process...');
    svixProcess = spawn('svix', ['listen', 'http://localhost:3000/webhook']);
    
    let output = '';
    let urlFound = false;
    
    svixProcess.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      console.log('[svix listen]', text.trim());
      
      // Extract the public URL
      const urlMatch = text.match(/https:\/\/play\.svix\.com\/in\/[^\/\s]+\/?/);
      if (urlMatch && !urlFound) {
        urlFound = true;
        const publicUrl = urlMatch[0].replace(/\/$/, '');
        console.log(`Found public URL: ${publicUrl}`);
        resolve(publicUrl);
      }
    });
    
    svixProcess.stderr.on('data', (data) => {
      console.error('[svix listen stderr]', data.toString().trim());
    });
    
    svixProcess.on('error', (error) => {
      console.error('Failed to start svix listen:', error);
      reject(error);
    });
    
    // Timeout if URL not found
    setTimeout(() => {
      if (!urlFound) {
        reject(new Error('Timeout: Could not extract public URL from svix listen'));
      }
    }, 30000);
  });
}

// Wait for webhook request
async function waitForRequest(expectedCount) {
  return new Promise((resolve) => {
    const checkInterval = setInterval(() => {
      if (requestCounter >= expectedCount) {
        clearInterval(checkInterval);
        // Give a small delay to ensure the response is processed
        setTimeout(resolve, 500);
      }
    }, 100);
  });
}

// Check message attempt status
async function checkAttemptStatus(svix, appId, msgId, endpointId) {
  const attempts = await svix.messageAttempt.listByMsg(appId, msgId, {
    limit: 10,
  });
  
  const endpointAttempts = attempts.filter(a => a.endpointId === endpointId);
  if (endpointAttempts.length > 0) {
    const latestAttempt = endpointAttempts[0];
    console.log(`Latest attempt status: ${latestAttempt.status}, responseStatusCode: ${latestAttempt.responseStatusCode}`);
    return latestAttempt;
  }
  
  return null;
}

// Main execution
async function main() {
  try {
    // Get Svix auth token from environment
    const authToken = process.env.SVIX_AUTH_TOKEN;
    if (!authToken) {
      throw new Error('SVIX_AUTH_TOKEN environment variable is not set');
    }
    
    // Initialize Svix SDK
    const svix = new Svix(authToken);
    
    // Start Express server
    await startServer();
    
    // Start svix listen and get public URL
    const publicUrl = await startSvixListen();
    
    // Wait a bit for svix listen to be ready
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Create Application
    console.log('Creating Application...');
    const application = await svix.application.create({
      name: 'Retry Test App',
    });
    const appId = application.id;
    console.log(`Application created: ${appId}`);
    
    // Create Endpoint
    console.log('Creating Endpoint...');
    const endpoint = await svix.endpoint.create(appId, {
      url: publicUrl,
      description: 'Test endpoint for retry simulation',
    });
    const endpointId = endpoint.id;
    console.log(`Endpoint created: ${endpointId}`);
    
    // Send Message
    console.log('Sending Message...');
    const message = await svix.message.create(appId, {
      eventType: 'test.retry',
      payload: {
        test: 'data',
        timestamp: new Date().toISOString(),
      },
    });
    const msgId = message.id;
    console.log(`Message sent: ${msgId}`);
    
    // Monitor and retry on failures
    let successCount = 0;
    const maxRetries = 2;
    
    while (successCount < 1) {
      // Wait for the local server to receive the request
      const expectedRequestCount = requestCounter + 1;
      console.log(`Waiting for request #${expectedRequestCount}...`);
      await waitForRequest(expectedRequestCount);
      
      // Wait a bit for Svix to process the attempt
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Check the attempt status
      const attempt = await checkAttemptStatus(svix, appId, msgId, endpointId);
      
      if (attempt && attempt.status === 'Failure' && attempt.responseStatusCode === 500) {
        console.log(`Attempt failed as expected. Manually resending...`);
        
        // Manually resend the message
        await svix.messageAttempt.resend(appId, msgId, endpointId);
        console.log('Message resent successfully');
      } else if (attempt && attempt.status === 'Success' && attempt.responseStatusCode === 200) {
        console.log('Attempt succeeded!');
        successCount++;
      } else {
        console.log(`Unexpected attempt status: ${attempt ? attempt.status : 'null'}, waiting...`);
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    // Write output to JSON file
    console.log('Writing output to output.json...');
    const outputPath = '/home/user/project/output.json';
    fs.writeFileSync(outputPath, JSON.stringify({
      appId: appId,
      msgId: msgId,
    }, null, 2));
    console.log(`Output written to ${outputPath}`);
    
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  } finally {
    // Cleanup
    console.log('Cleaning up...');
    
    if (server) {
      server.close(() => {
        console.log('Express server closed');
      });
    }
    
    if (svixProcess) {
      svixProcess.kill('SIGTERM');
      console.log('svix listen process terminated');
    }
    
    console.log('Done!');
  }
}

// Run the script
main();