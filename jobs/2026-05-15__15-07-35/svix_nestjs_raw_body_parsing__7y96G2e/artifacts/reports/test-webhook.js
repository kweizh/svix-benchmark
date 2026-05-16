const { Webhook } = require('svix');
const http = require('http');

const secret = 'whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ';
const payload = JSON.stringify({ test: 'data' });
const wh = new Webhook(secret);

async function test(headers, expectedStatus, label) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: '/webhook',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
    };

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode === expectedStatus) {
          console.log(`[PASS] ${label}: Received expected status ${res.statusCode}`);
          resolve();
        } else {
          console.log(`[FAIL] ${label}: Expected ${expectedStatus}, got ${res.statusCode}. Body: ${body}`);
          reject(new Error(`${label} failed`));
        }
      });
    });

    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function runTests() {
  const msgId = 'msg_123';
  const timestamp = new Date();
  const signature = wh.sign(msgId, timestamp, payload);

  // Test 1: Valid signature
  await test({
    'svix-id': msgId,
    'svix-timestamp': Math.floor(timestamp.getTime() / 1000).toString(),
    'svix-signature': signature,
  }, 200, 'Valid signature');

  // Test 2: Invalid signature
  await test({
    'svix-id': msgId,
    'svix-timestamp': Math.floor(timestamp.getTime() / 1000).toString(),
    'svix-signature': 'v1,invalid',
  }, 400, 'Invalid signature');

  // Test 3: Missing headers
  await test({
    'svix-id': msgId,
  }, 400, 'Missing headers');

  console.log('All tests passed!');
}

runTests().catch(err => {
  console.error(err);
  process.exit(1);
});
