'use strict';

/**
 * simulate_retry.js
 *
 * Demonstrates Svix webhook failure and manual retry:
 *  1. Starts an Express server on :3000 that fails the first two POSTs (500)
 *     and succeeds the third (200).
 *  2. Spawns `svix listen` to get a public tunnel URL.
 *  3. Creates a Svix Application + Endpoint + Message via the SDK.
 *  4. Polls for each failed attempt and immediately resends it manually.
 *  5. On the third (successful) delivery, writes output.json and exits cleanly.
 */

const express = require('express');
const { spawn } = require('child_process');
const { Svix } = require('svix');
const fs = require('fs');
const path = require('path');

// ── helpers ──────────────────────────────────────────────────────────────────

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Poll until the predicate returns a truthy value, then return that value.
 * Throws after `maxAttempts` retries.
 */
async function pollUntil(fn, { intervalMs = 2000, maxAttempts = 60, label = '' } = {}) {
  for (let i = 1; i <= maxAttempts; i++) {
    const result = await fn();
    if (result) return result;
    console.log(`  [poll${label ? ' ' + label : ''}] attempt ${i}/${maxAttempts} – not ready yet, waiting ${intervalMs}ms…`);
    await sleep(intervalMs);
  }
  throw new Error(`pollUntil timed out after ${maxAttempts} attempts${label ? ' (' + label + ')' : ''}`);
}

// ── 1. Express server ─────────────────────────────────────────────────────────

let requestCount = 0;
// Promises that resolve when the Nth request arrives
const requestReceivedResolvers = {};
const requestReceivedPromises = {};
for (const n of [1, 2, 3]) {
  requestReceivedPromises[n] = new Promise((resolve) => {
    requestReceivedResolvers[n] = resolve;
  });
}

function startServer() {
  return new Promise((resolve) => {
    const app = express();
    app.use(express.json());
    app.use(express.text({ type: '*/*' }));

    app.post('/webhook', (req, res) => {
      requestCount += 1;
      const n = requestCount;
      console.log(`\n[server] Received request #${n}`);

      if (n <= 2) {
        console.log(`[server] Responding 500 (simulated failure) for request #${n}`);
        res.status(500).json({ error: 'simulated failure' });
      } else {
        console.log(`[server] Responding 200 (success) for request #${n}`);
        res.status(200).json({ ok: true });
      }

      // Notify waiting code
      if (requestReceivedResolvers[n]) {
        requestReceivedResolvers[n](n);
      }
    });

    const server = app.listen(3000, () => {
      console.log('[server] Express listening on http://localhost:3000');
      resolve(server);
    });
  });
}

// ── 2. svix listen tunnel ────────────────────────────────────────────────────

function startSvixListen() {
  return new Promise((resolve, reject) => {
    console.log('[tunnel] Spawning: svix listen http://localhost:3000/webhook');
    const proc = spawn('svix', ['listen', 'http://localhost:3000/webhook'], {
      env: { ...process.env },
    });

    let buffer = '';

    proc.stdout.on('data', (chunk) => {
      buffer += chunk.toString();
      process.stdout.write('[tunnel stdout] ' + chunk.toString());

      // The CLI prints a line like:
      //   Webhook URL: https://play.svix.com/in/e_XXXXX/
      // or sometimes just a bare URL on a line
      const urlMatch = buffer.match(/https?:\/\/play\.svix\.com\/in\/[^\s]+/);
      if (urlMatch) {
        resolve({ proc, url: urlMatch[0].trim() });
      }
    });

    proc.stderr.on('data', (chunk) => {
      process.stderr.write('[tunnel stderr] ' + chunk.toString());
    });

    proc.on('error', (err) => reject(err));
    proc.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.warn(`[tunnel] svix listen exited with code ${code}`);
      }
    });

    // Give up waiting for the URL after 30 seconds
    setTimeout(() => reject(new Error('Timed out waiting for svix listen URL')), 30_000);
  });
}

// ── main ──────────────────────────────────────────────────────────────────────

async function main() {
  const authToken = process.env.SVIX_AUTH_TOKEN;
  if (!authToken) {
    throw new Error('SVIX_AUTH_TOKEN environment variable is not set');
  }

  const svix = new Svix(authToken);
  const OUTPUT_PATH = path.join(__dirname, 'output.json');

  // 1. Start local server
  const server = await startServer();

  // 2. Start tunnel
  const { proc: tunnelProc, url: webhookUrl } = await startSvixListen();
  console.log(`\n[tunnel] Public URL: ${webhookUrl}\n`);

  // Give the tunnel a moment to fully establish
  await sleep(2000);

  // 3. Ensure the event type exists (some environments require it before
  //    endpoints can filter on it)
  const EVENT_TYPE = 'demo.event';
  console.log(`[svix] Ensuring event type '${EVENT_TYPE}' exists…`);
  await svix.eventType
    .create({ name: EVENT_TYPE, description: 'Demo event for retry test' })
    .catch((e) => {
      // 409 Conflict means it already exists – that is fine
      if (e && e.code === 409) {
        console.log(`[svix] Event type '${EVENT_TYPE}' already exists, continuing.`);
      } else {
        throw e;
      }
    });

  // 4. Create Svix application
  console.log('[svix] Creating application…');
  const app = await svix.application.create({ name: 'retry-demo-app' });
  const appId = app.id;
  console.log(`[svix] Application created: ${appId}`);

  // 5. Create endpoint pointing at the tunnel URL
  //    filterTypes is required on this environment.
  console.log('[svix] Creating endpoint…');
  const endpoint = await svix.endpoint.create(appId, {
    url: webhookUrl,
    filterTypes: [EVENT_TYPE],
  });
  const endpointId = endpoint.id;
  console.log(`[svix] Endpoint created: ${endpointId}`);

  // Small pause so the endpoint is fully registered before we send
  await sleep(1000);

  // 6. Send a message
  console.log('[svix] Sending message…');
  const message = await svix.message.create(appId, {
    eventType: EVENT_TYPE,
    payload: { hello: 'world', timestamp: new Date().toISOString() },
  });
  const msgId = message.id;
  console.log(`[svix] Message sent: ${msgId}`);

  // ── Manual retry loop (for failures 1 and 2) ─────────────────────────────

  for (let failureNumber = 1; failureNumber <= 2; failureNumber++) {
    console.log(`\n[retry] Waiting for failure #${failureNumber} to arrive at local server…`);
    await requestReceivedPromises[failureNumber];
    console.log(`[retry] Local server registered failure #${failureNumber}.`);

    // Give Svix a moment to record the attempt on its side
    await sleep(3000);

    // Verify the attempt is recorded as failed
    // Svix MessageStatus: Success=0, Pending=1, Fail=2, Sending=3
    const failedAttempt = await pollUntil(
      async () => {
        const list = await svix.messageAttempt.listByMsg(appId, msgId, {
          endpointId,
          status: 2, // 2 = Fail in Svix SDK
        });
        if (list.data && list.data.length >= failureNumber) {
          return list.data[0]; // most recent first
        }
        return null;
      },
      { intervalMs: 2000, maxAttempts: 30, label: `failed attempt #${failureNumber}` },
    );

    console.log(
      `[retry] Confirmed failed attempt #${failureNumber}: id=${failedAttempt.id}, status=${failedAttempt.status}, responseStatusCode=${failedAttempt.responseStatusCode}`,
    );

    // Manually resend
    console.log(`[retry] Manually resending message (attempt ${failureNumber + 1})…`);
    console.log(`[retry]   appId=${appId} msgId=${msgId} endpointId=${endpointId}`);
    await svix.messageAttempt.resend(appId, msgId, endpointId).catch((e) => {
      console.error('[retry] resend error:', JSON.stringify(e.body), 'code:', e.code);
      throw e;
    });
    console.log(`[retry] Resend request sent for failure #${failureNumber}.`);
  }

  // ── Wait for the 3rd (successful) delivery ────────────────────────────────

  console.log('\n[retry] Waiting for 3rd delivery (expected 200)…');
  await requestReceivedPromises[3];
  console.log('[retry] 3rd delivery received by local server (200 OK).');

  // Give Svix time to record the successful attempt
  await sleep(3000);

  // Confirm success in Svix
  const successAttempt = await pollUntil(
    async () => {
      const list = await svix.messageAttempt.listByMsg(appId, msgId, {
        endpointId,
        status: 0, // 0 = Success in Svix SDK (MessageStatus)
      });
      if (list.data && list.data.length > 0) {
        return list.data[0];
      }
      return null;
    },
    { intervalMs: 2000, maxAttempts: 30, label: 'successful attempt' },
  );

  console.log(
    `\n[svix] Confirmed successful delivery: id=${successAttempt.id}, status=${successAttempt.status}, responseStatusCode=${successAttempt.responseStatusCode}`,
  );

  // ── Write output.json ─────────────────────────────────────────────────────

  const output = { appId, msgId };
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output, null, 2) + '\n');
  console.log(`\n[output] Written to ${OUTPUT_PATH}:`);
  console.log(JSON.stringify(output, null, 2));

  // ── Clean shutdown ────────────────────────────────────────────────────────

  console.log('\n[shutdown] Stopping Express server…');
  await new Promise((resolve) => server.close(resolve));

  console.log('[shutdown] Stopping svix listen tunnel…');
  tunnelProc.kill('SIGTERM');

  console.log('[shutdown] Done. Exiting.');
  process.exit(0);
}

main().catch((err) => {
  console.error('\n[fatal]', err);
  process.exit(1);
});
