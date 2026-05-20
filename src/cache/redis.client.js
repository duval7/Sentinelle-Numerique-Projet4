const { createClient } = require('redis');

const client = createClient({
    url: 'redis://127.0.0.1:6379'
});

client.on('error', (err) => console.log('Redis Error', err));

const connectRedis = async () => {
    if (!client.isOpen) {
        await client.connect();
        console.log('🚀 Redis Cache Layer: ONLINE');
    }
};

module.exports = { client, connectRedis };