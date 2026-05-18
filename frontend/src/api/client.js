const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const analyseContent = async (data) => {
  const response = await fetch(`${API_BASE_URL}/api/analyse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Erreur lors de la connexion au serveur');
  }

  return response.json();
};

export const getHistory = async () => {
  const response = await fetch(`${API_BASE_URL}/api/history`);

  if (!response.ok) {
    throw new Error('Erreur lors de la récupération de l\'historique');
  }

  return response.json();
};