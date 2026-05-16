const express = require('express');
const { Webhook } = require('svix');

const app = express();
const secret = "whsec_testsecret"; 

// Apply raw body parsing only for the /webhook route so that Svix can verify
// the HMAC signature against the original, unparsed request body.
// express.json() is NOT applied globally; instead it is added as route-level
// middleware on every other endpoint that needs parsed JSON.
app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
    // req.body is a Buffer here; Svix's verify() accepts Buffer or string.
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

// Parse JSON for all other routes.
app.use(express.json());

app.post('/api/data', (req, res) => {
    res.json(req.body);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
