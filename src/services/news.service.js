const axios = require('axios');
const { client } = require('../cache/redis.client');
require('dotenv').config();

const NEWS_API_KEY = process.env.NEWS_API_KEY;

const getNewsData = async (query) => {
    const cacheKey = `news:${query.toLowerCase().replace(/\s+/g, '_')}`;

    try {
        // 1. Check Cache
        if (client.isOpen) {
            const cached = await client.get(cacheKey);
            if (cached) return JSON.parse(cached);
        }

        // 2. Fetch from NewsAPI
        const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&language=en&pageSize=3&apiKey=${NEWS_API_KEY}`;
        const response = await axios.get(url);

        const articles = response.data.articles.map(article => ({
            source: article.source.name,
            headline: article.title,
            url: article.url
        }));

        // 3. Store in Cache for 6 hours
        if (client.isOpen) {
            await client.setEx(cacheKey, 21600, JSON.stringify(articles));
        }

        return articles;
    } catch (error) {
        return [];
    }
};

module.exports = { getNewsData };