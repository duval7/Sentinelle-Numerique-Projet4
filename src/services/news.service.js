const Parser = require('rss-parser');
// Adding headers to the parser to mimic a browser
const parser = new Parser({
  headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' },
});

const fetchNewsData = async (query) => {
    try {
        // Broadening search to global results for topics like XAUUSD
        const RSS_URL = `https://news.google.com/rss/search?q=${encodeURIComponent(query)}&hl=en-US&gl=US&ceid=US:en`;
        
        console.log(`[News Attempt] Fetching news for: ${query}`);
        const feed = await parser.parseURL(RSS_URL);
        
        return feed.items.slice(0, 5).map(item => ({
            title: item.title,
            link: item.link,
            pubDate: item.pubDate
        }));
    } catch (error) {
        console.error("News Service Error:", error.message);
        return [{ title: "Network Error: Could not fetch news live." }];
    }
};

module.exports = { fetchNewsData };