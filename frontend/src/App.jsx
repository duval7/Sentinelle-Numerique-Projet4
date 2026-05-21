import React, { useState } from 'react';
import SubmitForm from './components/SubmitForm';
import ScoreGauge from './components/ScoreGauge';
import ClaimTable from './components/ClaimTable';
import SourceCard from './components/SourceCard';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorBanner from './components/ErrorBanner';
import './styles/main.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyse = async (data) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('/api/analyse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Erreur serveur');
      const json = await response.json();
      setResult(json);
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
        {error && <ErrorBanner message={error} />}
        {result && (
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

export default App;