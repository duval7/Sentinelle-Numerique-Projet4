const axios = require('axios');
const { client } = require('../cache/redis.client');

const getWikipediaData = async (claim) => {
    const cacheKey = `wiki:${claim.toLowerCase().replace(/\s+/g, '_')}`;

    try {
        if (client.isOpen) {
            const cached = await client.get(cacheKey);
            if (cached) return JSON.parse(cached);
        }

        const url = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(claim)}`;
        
        // ADD THIS HEADERS OBJECT
        const response = await axios.get(url, {
            headers: { 'User-Agent': 'SentinelleNumerique/1.0 (Contact: boris@student.com)' }
        });

        const result = {
            source: "Wikipedia",
            summary: response.data.extract,
            url: response.data.content_urls.desktop.page
        };

        if (client.isOpen) {
            await client.setEx(cacheKey, 21600, JSON.stringify(result));
        }
        return result;
    } catch (error) {
        console.error("API Error:", error.message);
        return null;
    }
};

module.exports = { getWikipediaData };