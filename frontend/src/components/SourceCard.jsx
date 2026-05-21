import React from 'react';

function SourceCard({ source }) {
  const getTag = (status) => {
    if (status === 'confirmed') return { label: 'Confirmé', cls: 'tag-ok' };
    if (status === 'unverified') return { label: 'Non vérifié', cls: 'tag-danger' };
    return { label: 'Partiel', cls: 'tag-warn' };
  };

  const tag = getTag(source.status);

  return (
    <div className="source-card">
      <h4>{source.name}</h4>
      <p>{source.description}</p>
      <span className={`source-tag ${tag.cls}`}>{tag.label}</span>
    </div>
  );
}

export default SourceCard;