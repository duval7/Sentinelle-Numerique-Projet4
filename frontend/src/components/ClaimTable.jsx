import React from 'react';

function ClaimTable({ claims }) {
  const getIcon = (status) => {
    if (status === 'verified') return '✅';
    if (status === 'unverified') return '❌';
    return '⚠️';
  };

  return (
    <div className="claim-table">
      <h3>Détail des vérifications</h3>
      {claims && claims.length > 0 ? (
        claims.map((claim, i) => (
          <div className="claim-row" key={i}>
            <span className="claim-icon">{getIcon(claim.status)}</span>
            <div>
              <div className="claim-text">{claim.text}</div>
              {claim.source && (
                <div className="claim-source">→ source : {claim.source}</div>
              )}
            </div>
          </div>
        ))
      ) : (
        <p style={{ color: 'var(--muted)', fontSize: '14px' }}>
          Aucune affirmation détectée.
        </p>
      )}
    </div>
  );
}

export default ClaimTable;