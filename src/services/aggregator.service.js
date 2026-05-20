const { getWikipediaData } = require('./wikipedia.service');
const { getNewsData } = require('./news.service');

/**
 * Sentinelle Numérique - Aggregator
 * Combines Wikipedia and News evidence to score a claim.
 */
const verifyClaim = async (claim) => {
    // Run both requests in parallel for maximum speed
    const [wikiResult, newsResult] = await Promise.all([
        getWikipediaData(claim),
        getNewsData(claim)
    ]);

    let score = 0;
    
    // 1. Scoring Wikipedia (Base reliability)
    if (wikiResult) {
        score += 50;
    }

    // 2. Scoring News (Social/Current proof)
    if (newsResult && newsResult.length > 0) {
        // Add 10 points per article, max 30
        score += Math.min(newsResult.length * 10, 30);
    }

    // 3. Consistency Bonus (If both sources agree it exists)
    if (wikiResult && newsResult.length > 0) {
        score += 20;
    }

    return {
        claim,
        reliabilityScore: score,
        verdict: score >= 70 ? 'HIGH' : score >= 40 ? 'MODERATE' : 'LOW',
        details: {
            hasWiki: !!wikiResult,
            newsCount: newsResult ? newsResult.length : 0
        },
        timestamp: new Date().toISOString()
    };
};

module.exports = { verifyClaim };