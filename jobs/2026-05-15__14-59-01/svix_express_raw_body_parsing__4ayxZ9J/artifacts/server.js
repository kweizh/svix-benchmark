const express = require('express');
const { Webhook } = require('svix');

const app = express();
const secret = "whsec_testsecret"; 

app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
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

app.use(express.json());

app.post('/api/data', (req, res) => {
    res.json(req.body);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
