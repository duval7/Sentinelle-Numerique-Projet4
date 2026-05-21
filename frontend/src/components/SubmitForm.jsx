import React, { useState } from 'react';

function SubmitForm({ onSubmit }) {
  const [activeTab, setActiveTab] = useState('text');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');

  const handleSubmit = () => {
    if (activeTab === 'text' && text.trim()) {
      onSubmit({ type: 'text', content: text });
    } else if (activeTab === 'url' && url.trim()) {
      onSubmit({ type: 'url', content: url });
    }
  };

  return (
    <div className="submit-form">
      <h2>Vérifiez un contenu</h2>
      <p>Soumettez un texte ou une URL pour analyser sa fiabilité.</p>

      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'text' ? 'active' : ''}`}
          onClick={() => setActiveTab('text')}
        >
          Texte / Article
        </button>
        <button
          className={`tab-btn ${activeTab === 'url' ? 'active' : ''}`}
          onClick={() => setActiveTab('url')}
        >
          URL
        </button>
      </div>

      {activeTab === 'text' && (
        <div className="form-group">
          <label>Contenu à analyser</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Collez ici le contenu d'un article dont vous souhaitez vérifier les affirmations..."
          />
        </div>
      )}

      {activeTab === 'url' && (
        <div className="form-group">
          <label>URL de l'article</label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://exemple.com/article..."
          />
        </div>
      )}

      <button
        className="btn-submit"
        onClick={handleSubmit}
        disabled={activeTab === 'text' ? !text.trim() : !url.trim()}
      >
        Lancer l'analyse
      </button>
    </div>
  );
}

export default SubmitForm;