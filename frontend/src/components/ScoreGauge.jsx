import React from 'react';

function ScoreGauge({ score, verdict }) {
  const getClass = () => {
    if (score < 40) return 'score-danger';
    if (score < 70) return 'score-warning';
    return 'score-success';
  };

  const getEmoji = () => {
    if (score < 40) return '❌';
    if (score < 70) return '⚠️';
    return '✅';
  };

  const getDescription = () => {
    if (score < 40) return 'Plusieurs affirmations ne sont pas confirmées par les sources de référence. Contenu peu fiable.';
    if (score < 70) return 'Certaines affirmations sont partiellement vérifiées. À lire avec prudence.';
    return 'Les affirmations principales sont confirmées par plusieurs sources fiables.';
  };

  return (
    <div className="score-card">
      <div className={`score-circle ${getClass()}`}>
        <span className="num">{score}%</span>
        <span className="label">confiance</span>
      </div>
      <div className="score-info">
        <h2>{getEmoji()} {verdict}</h2>
        <p>{getDescription()}</p>
      </div>
    </div>
  );
}

export default ScoreGauge;