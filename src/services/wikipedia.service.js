const axios = require('axios');
const { client } = require('../cache/redis.client');

const fetchWikiData = async (query) => {
    const cacheKey = `wiki:${query.toLowerCase().replace(/\s+/g, '_')}`;
    try {
        if (client.isOpen) {
            const cached = await client.get(cacheKey);
            if (cached) return JSON.parse(cached);
        }

        const res = await axios.get('https://en.wikipedia.org/w/api.php', {
            params: { action: 'query', list: 'search', srsearch: query, format: 'json', origin: '*' },
            headers: { 'User-Agent': 'BorisStudentProject/1.0' }
        });

        const result = res.data.query.search[0] || { snippet: "No results." };

        if (client.isOpen) await client.setEx(cacheKey, 3600, JSON.stringify(result));
        return result;
    } catch (error) {
        throw new Error("Wiki Unreachable");
    }
};

module.exports = { fetchWikiData };
