const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';

const HEADERS = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer dev-test-token-groupe4',
};

export const analyseContent = async (data) => {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Erreur lors de la connexion au serveur');
  }

  return response.json();
};

export const getResult = async (jobId) => {
  const response = await fetch(`${API_BASE_URL}/api/result/${jobId}`, {
    headers: HEADERS,
  });

  if (!response.ok) {
    throw new Error('Erreur lors de la récupération du résultat');
  }

  return response.json();
};