"use strict";
require("dotenv").config();
const axios = require("axios");
const cache = require("../cache/redis.client");

const NEWSAPI_BASE = process.env.NEWSAPI_BASE || "https://newsapi.org/v2";
const NEWSAPI_KEY  = process.env.NEWSAPI_KEY;

async function search(keywords) {
  const cacheKey = `news:${keywords}`;

  // Check cache first
  const cached = await cache.get(cacheKey);
  if (cached) {
    console.log(`[GoogleNews] Cache hit for "${keywords}"`);
    return cached;
  }

  try {
    const res = await axios.get(`${NEWSAPI_BASE}/everything`, {
      params: {
        q:        keywords,
        sortBy:   "relevancy",
        language: "en",
        pageSize: 5,
        apiKey:   NEWSAPI_KEY,
      },
      timeout: 8000,
    });

    const articles = res.data.articles || [];
    if (articles.length === 0) {
      return { score: 0, sources: [] };
    }

    // Filter articles from last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const recent = articles.filter(a => new Date(a.publishedAt) >= thirtyDaysAgo);

    const score   = computeRelevance(keywords, recent);
    const result  = {
      score,
      sources: recent.map(a => ({ title: a.title, url: a.url })),
    };

    // Save to cache
    await cache.set(cacheKey, result);
    return result;

  } catch (err) {
    console.error("[GoogleNews] Error:", err.message);
    return { score: 0, sources: [] };
  }
}

// Score = ratio of articles whose title contains at least one keyword
function computeRelevance(keywords, articles) {
  if (articles.length === 0) return 0;
  const words    = keywords.toLowerCase().split(" ").filter(w => w.length > 2);
  const matching = articles.filter(a => {
    const title = (a.title || "").toLowerCase();
    return words.some(w => title.includes(w));
  });
  return parseFloat((matching.length / articles.length).toFixed(2));
}

module.exports = { search };