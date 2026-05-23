"use strict";
require("dotenv").config();
const axios = require("axios");
const cache = require("../cache/redis.client");

const WIKI_BASE = process.env.WIKIPEDIA_API_BASE || "https://en.wikipedia.org/api/rest_v1";

async function search(keywords) {
  const cacheKey = `wiki:${keywords}`;

  // Check cache first
  const cached = await cache.get(cacheKey);
  if (cached) {
    console.log(`[Wikipedia] Cache hit for "${keywords}"`);
    return cached;
  }

  try {
    // Search for the most relevant Wikipedia page
    const searchRes = await axios.get(`${WIKI_BASE}/page/search`, {
      params: { q: keywords, limit: 3 },
      timeout: 8000,
    });

    const pages = searchRes.data.pages || [];
    if (pages.length === 0) {
      return { score: 0, sources: [] };
    }

    // Get the summary of the top result
    const topPage = pages[0];
    const summaryRes = await axios.get(
      `${WIKI_BASE}/page/summary/${encodeURIComponent(topPage.key)}`,
      { timeout: 8000 }
    );

    const summary = summaryRes.data.extract || "";
    const score   = computeScore(keywords, summary);
    const result  = {
      score,
      sources: [`https://en.wikipedia.org/wiki/${encodeURIComponent(topPage.key)}`],
    };

    // Save to cache
    await cache.set(cacheKey, result);
    return result;

  } catch (err) {
    console.error("[Wikipedia] Error:", err.message);
    return { score: 0, sources: [] };
  }
}

// Score = how many keywords appear in the Wikipedia summary
function computeScore(keywords, summary) {
  const words   = keywords.toLowerCase().split(" ").filter(w => w.length > 2);
  const text    = summary.toLowerCase();
  const matches = words.filter(w => text.includes(w));
  if (words.length === 0) return 0;
  return parseFloat((matches.length / words.length).toFixed(2));
}

module.exports = { search };