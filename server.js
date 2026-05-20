require('dotenv').config();
const express = require('express');
const { verifyClaim } = require('./src/services/aggregator.service');
const { connectRedis } = require('./src/cache/redis.client');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to parse JSON
app.use(express.json());

// The "Verification" Route
app.get('/api/verify', async (req, res) => {
    const { claim } = req.query;

    if (!claim) {
        return res.status(400).json({ error: 'Please provide a claim to verify.' });
    }

    try {
        const report = await verifyClaim(claim);
        res.json(report);
    } catch (error) {
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// Start the server
const startServer = async () => {
    await connectRedis(); // Connect to your Ubuntu Redis instance
    app.listen(PORT, () => {
        console.log(`🚀 Sentinelle Numérique API is running on http://localhost:${PORT}`);
    });
};

startServer();