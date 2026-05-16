const express = require('express');
const { Webhook } = require('svix');

const app = express();
const secret = "whsec_testsecret"; 

// Webhook endpoint - use raw body parsing for Svix signature verification
app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
    const payload = req.body; // This is now a Buffer (raw string)
    const headers = req.headers;
    const wh = new Webhook(secret);
    
    try {
        const msg = wh.verify(payload, headers);
        console.log("Verified payload:", msg);
        res.status(204).send();
    } catch (err) {
        console.error("Webhook verification failed:", err);
        res.status(400).send("Invalid signature");
    }
});

// Other endpoints - use JSON parsing
app.use(express.json());

app.post('/api/data', (req, res) => {
    res.json(req.body);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});