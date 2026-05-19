"use strict";
require("dotenv").config();

const WIKI_WEIGHT = parseFloat(process.env.WIKI_WEIGHT || "0.5");
const NEWS_WEIGHT = parseFloat(process.env.NEWS_WEIGHT || "0.5");

function aggregate(jobId, claims) {
  if (!claims || claims.length === 0) {
    return {
      jobId,
      confidenceScore: 0,
      verdict:         "UNKNOWN",
      claimBreakdown:  [],
      computedAt:      new Date().toISOString(),
    };
  }

  const breakdown = claims.map(claim => {
    const wiki  = clamp(claim.wikiScore, 0, 1);
    const news  = clamp(claim.newsScore, 0, 1);
    const score = wiki * WIKI_WEIGHT + news * NEWS_WEIGHT;
    return {
      text:           claim.text,
      entities:       claim.entities       || [],
      numericalValue: claim.numericalValue || null,
      wikiScore:      round2(wiki),
      newsScore:      round2(news),
      claimScore:     round2(score),
      verdict:        getVerdict(score * 100),
      wikiSources:    claim.wikiSources    || [],
      newsSources:    claim.newsSources    || [],
    };
  });

  const avg             = breakdown.reduce((sum, c) => sum + c.claimScore, 0) / breakdown.length;
  const confidenceScore = Math.round(avg * 100);

  return {
    jobId,
    confidenceScore,
    verdict:        getVerdict(confidenceScore),
    claimBreakdown: breakdown,
    computedAt:     new Date().toISOString(),
  };
}

function getVerdict(score) {
  if (score >= 70) return "HIGH";
  if (score >= 40) return "MEDIUM";
  return "LOW";
}

function clamp(v, min, max) { return Math.min(Math.max(v, min), max); }
function round2(v)           { return Math.round(v * 100) / 100; }

module.exports = { aggregate, getVerdict };