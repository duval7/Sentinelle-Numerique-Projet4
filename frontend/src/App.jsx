import React, { useState } from 'react';
import SubmitForm    from './components/SubmitForm';
import ScoreGauge    from './components/ScoreGauge';
import ClaimTable    from './components/ClaimTable';
import SourceCard    from './components/SourceCard';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorBanner   from './components/ErrorBanner';
import { analyseContent, getResult } from './api/client';
import './styles/main.css';

function App() {
  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const handleAnalyse = async (data) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Step 1 — Submit article and get jobId
      const { jobId } = await analyseContent(data);

      // Step 2 — Poll every 2 seconds until result is ready
      const finalResult = await pollResult(jobId);

      // Step 3 — Map backend response to frontend format
      setResult({
        score:   finalResult.confidenceScore,
        verdict: finalResult.verdict,
        claims:  finalResult.claimBreakdown?.map(c => ({
          text:   c.text,
          status: c.verdict === 'HIGH'
            ? 'verified'
            : c.verdict === 'LOW'
            ? 'unverified'
            : 'partial',
          source: c.wikiSources?.[0] || c.newsSources?.[0] || null,
        })) || [],
        sources: finalResult.claimBreakdown?.flatMap(c => [
          ...c.wikiSources || [],
          ...c.newsSources?.map(s => s.url) || [],
        ]) || [],
      });

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo-dot"></div>
        <h1>Sentinelle Numérique</h1>
        <p>Fact-Checker Automatisé</p>
      </header>

      <main className="app-main">
        <SubmitForm onSubmit={handleAnalyse} />
        {loading && <LoadingSpinner />}
        {error   && <ErrorBanner message={error} />}
        {result  && (
          <>
            <ScoreGauge score={result.score} verdict={result.verdict} />
            <ClaimTable claims={result.claims} />
            <div className="sources-grid">
              {result.sources && result.sources.map((src, i) => (
                <SourceCard key={i} source={src} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

// Poll /api/result/:jobId every 2 seconds until status is not pending
async function pollResult(jobId, maxAttempts = 15) {
  for (let i = 0; i < maxAttempts; i++) {
    const data = await getResult(jobId);
    if (data.status !== 'pending') return data;
    await new Promise(r => setTimeout(r, 2000));
  }
  throw new Error('Analysis timed out. Please try again.');
}

export default App;