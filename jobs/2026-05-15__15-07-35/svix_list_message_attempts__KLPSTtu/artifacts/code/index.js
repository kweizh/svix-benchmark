const { Svix } = require('svix');
const fs = require('fs');

async function main() {
  const authToken = process.env.SVIX_AUTH_TOKEN;
  const appId = process.argv[2];
  const msgId = process.argv[3];

  if (!authToken) {
    console.error('SVIX_AUTH_TOKEN environment variable is required');
    process.exit(1);
  }

  if (!appId || !msgId) {
    console.error('Usage: node index.js <appId> <msgId>');
    process.exit(1);
  }

  const svix = new Svix(authToken);

  try {
    const response = await svix.messageAttempt.listByMsg(appId, msgId);
    fs.writeFileSync('/home/user/myproject/attempts.json', JSON.stringify(response.data, null, 2));
    console.log('Successfully wrote attempts to /home/user/myproject/attempts.json');
  } catch (error) {
    console.error('Error fetching message attempts:', error.message);
    process.exit(1);
  }
}

main();
