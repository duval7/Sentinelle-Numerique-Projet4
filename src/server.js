require('dotenv').config();
const express = require('express');

// Imports relative to the src folder
const { connectRedis } = require('./cache/redis.client');
const { fetchWikiData } = require('./services/wikipedia.service');
const { fetchNewsData } = require('./services/news.service');

const app = express();
const PORT = 3000;

app.use(express.json());

app.get('/api/verify', async (req, res) => {
    const { claim } = req.query;
    if (!claim) return res.status(400).json({ error: "Search query required" });

    try {
        // Parallel execution: fetch both at the same time
        const [wiki, news] = await Promise.all([
            fetchWikiData(claim),
            fetchNewsData(claim)
        ]);

        res.json({
            student: "KIMBI BORIS",
            status: "Success",
            search_query: claim,
            wikipedia: wiki,
            google_news: news
        });
    } catch (err) {
        res.status(500).json({ error: "Module Error", message: err.message });
    }
});

const start = async () => {
    try {
        await connectRedis();
        app.listen(PORT, () => console.log(`🚀 Boris Module: ONLINE on Port ${PORT}`));
    } catch (err) {
        console.error("Startup failed:", err);
    }
};

start();