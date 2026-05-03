FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Express application configured with global express.json() for Svix webhook verification task."

RUN mkdir -p /home/user/app && \
    cd /home/user/app && \
    cat >package.json <<'EOF'
{
  "name": "svix-webhook-app",
  "version": "1.0.0",
  "description": "App for svix webhook testing",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "svix": "^1.21.0"
  }
}
EOF

RUN cd /home/user/app && \
    cat >server.js <<'EOF'
const express = require('express');
const { Webhook } = require('svix');

const app = express();
const secret = "whsec_testsecret"; 

app.use(express.json());

app.post('/webhook', (req, res) => {
    const payload = req.body;
    const headers = req.headers;
    const wh = new Webhook(secret);
    
    try {
        const msg = wh.verify(payload, headers);
        console.log("Verified payload:", msg);
        res.status(204).send();
    } catch (err) {
        res.status(400).send("Invalid signature");
    }
});

app.post('/api/data', (req, res) => {
    res.json(req.body);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
EOF

# Container contents:
#   - Node.js v24 installed
#   - /home/user/app - Express project with package.json and server.js
#   - server.js uses app.use(express.json()) globally which breaks Svix webhook verification

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
