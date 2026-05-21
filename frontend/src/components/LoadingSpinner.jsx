import React from 'react';

function LoadingSpinner() {
  return (
    <div className="spinner-wrapper">
      <div className="spinner"></div>
      <p>Analyse en cours...</p>
      <div className="progress-bar">
        <div className="progress-fill"></div>
      </div>
    </div>
  );
}

export default LoadingSpinner;