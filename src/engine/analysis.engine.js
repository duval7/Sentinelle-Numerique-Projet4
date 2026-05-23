"use strict";
require("dotenv").config();
const axios      = require("axios");
const bus        = require("./bus.client");
const aggregator = require("./aggregator");

const QUEUE      = process.env.RABBITMQ_QUEUE  || "analysis_queue";
const NLP_URL    = process.env.NLP_SERVICE_URL || "http://localhost:8000";
const ENG_URL    = `http://localhost:${process.env.PORT_ENGINE || 3001}`;
const REPORT_URL = `http://localhost:${process.env.PORT_REPORT || 3002}`;

async function start() {
  console.log("[Engine] Starting...");
  await bus.consume(QUEUE, handleJob);
  console.log("[Engine] Waiting for jobs on queue:", QUEUE);
}

async function handleJob(job) {
  const { jobId, url, text } = job;
  console.log(`[Engine] Processing job ${jobId}`);

  try {
    // Step 1 — get article text
    const articleText = text || await fetchText(url);

    // Step 2 — extract claims via NLP service (Noella)
    const claims = await extractClaims(articleText);
    if (claims.length === 0) {
      return await saveReport(jobId, {
        confidenceScore: 0,
        verdict:         "UNKNOWN",
        claimBreakdown:  [],
      });
    }

    // Step 3 — verify each claim (Boris)
    const scored = await Promise.all(claims.map(verifyClaim));

    // Step 4 — aggregate scores (Duval)
    const report = aggregator.aggregate(jobId, scored);
    console.log(`[Engine] [${jobId}] Score: ${report.confidenceScore}% — ${report.verdict}`);

    // Step 5 — save report to MongoDB via Report Service
    await saveReport(jobId, report);

  } catch (err) {
    console.error(`[Engine] [${jobId}] Error:`, err.message);
    await saveReport(jobId, {
      confidenceScore: null,
      verdict:         "ERROR",
      error:           err.message,
      claimBreakdown:  [],
    });
  }
}

async function fetchText(url) {
  if (!url) throw new Error("No URL or text provided.");
  const res = await axios.get(url, { timeout: 8000 });
  return res.data.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

async function extractClaims(text) {
  try {
    const res = await axios.post(
      `${NLP_URL}/extract`,
      { text },
      { timeout: 15000 }
    );
    return res.data.claims || [];
  } catch (err) {
    console.warn("[Engine] NLP service unavailable:", err.message);
    return [{ text: "Stub claim", entities: [], numericalValue: null, credibilityScore: 0 }];
  }
}

async function verifyClaim(claim) {
  const q = claim.entities.length > 0
    ? claim.entities.join(" ")
    : claim.text.slice(0, 80);

  const [wiki, news] = await Promise.allSettled([
    axios.get(`${ENG_URL}/wiki/search`, { params: { q }, timeout: 8000 }),
    axios.get(`${ENG_URL}/news/search`, { params: { q }, timeout: 8000 }),
  ]);

  return {
    ...claim,
    wikiScore:   wiki.status === "fulfilled" ? wiki.value.data.score   : 0,
    newsScore:   news.status === "fulfilled" ? news.value.data.score   : 0,
    wikiSources: wiki.status === "fulfilled" ? wiki.value.data.sources : [],
    newsSources: news.status === "fulfilled" ? news.value.data.sources : [],
  };
}

async function saveReport(jobId, report) {
  try {
    await axios.post(
      `${REPORT_URL}/report`,
      { jobId, ...report },
      { timeout: 5000 }
    );
    console.log(`[Engine] Report saved for ${jobId}`);
  } catch (err) {
    console.error("[Engine] Failed to save report:", err.message);
  }
}

start().catch(err => {
  console.error("[Engine] Fatal error:", err.message);
  process.exit(1);
});

module.exports = { handleJob };