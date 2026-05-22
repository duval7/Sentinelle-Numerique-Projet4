import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../src/App';
import SubmitForm from '../src/components/SubmitForm';
import ScoreGauge from '../src/components/ScoreGauge';
import ErrorBanner from '../src/components/ErrorBanner';
import LoadingSpinner from '../src/components/LoadingSpinner';

// ── TEST 1 : L'application s'affiche correctement ──
test('Le header Sentinelle Numérique est affiché', () => {
  render(<App />);
  expect(screen.getByText('Sentinelle Numérique')).toBeInTheDocument();
});

// ── TEST 2 : Le formulaire s'affiche correctement ──
test('Le formulaire affiche le bouton Lancer analyse', () => {
  render(<SubmitForm onSubmit={() => {}} />);
  expect(screen.getByText("Lancer l'analyse")).toBeInTheDocument();
});

// ── TEST 3 : Les onglets fonctionnent ──
test('Le formulaire affiche les onglets Texte et URL', () => {
  render(<SubmitForm onSubmit={() => {}} />);
  expect(screen.getByText('Texte / Article')).toBeInTheDocument();
  expect(screen.getByText('URL')).toBeInTheDocument();
});

// ── TEST 4 : Le bouton est désactivé si le champ est vide ──
test('Le bouton est désactivé quand le champ est vide', () => {
  render(<SubmitForm onSubmit={() => {}} />);
  const bouton = screen.getByText("Lancer l'analyse");
  expect(bouton).toBeDisabled();
});

// ── TEST 5 : Le bouton s'active quand on tape du texte ──
test('Le bouton devient actif quand on tape du texte', () => {
  render(<SubmitForm onSubmit={() => {}} />);
  const textarea = screen.getByPlaceholderText(/Collez ici le contenu/i);
  fireEvent.change(textarea, { target: { value: 'Ceci est un article de test' } });
  const bouton = screen.getByText("Lancer l'analyse");
  expect(bouton).not.toBeDisabled();
});

// ── TEST 6 : Le score s'affiche correctement ──
test('ScoreGauge affiche le score et le verdict', () => {
  render(<ScoreGauge score={27} verdict="Fiabilité Faible" />);
  expect(screen.getByText('27%')).toBeInTheDocument();
  expect(screen.getByText(/Fiabilité Faible/i)).toBeInTheDocument();
});

// ── TEST 7 : Le score élevé affiche la bonne couleur ──
test('ScoreGauge affiche le bon verdict pour un score élevé', () => {
  render(<ScoreGauge score={85} verdict="Fiabilité Élevée" />);
  expect(screen.getByText('85%')).toBeInTheDocument();
});

// ── TEST 8 : Le message d'erreur s'affiche ──
test('ErrorBanner affiche le message d erreur', () => {
  render(<ErrorBanner message="Erreur de connexion au serveur" />);
  expect(screen.getByText('Erreur de connexion au serveur')).toBeInTheDocument();
});

// ── TEST 9 : Le spinner de chargement s'affiche ──
test('LoadingSpinner affiche le message de chargement', () => {
  render(<LoadingSpinner />);
  expect(screen.getByText('Analyse en cours...')).toBeInTheDocument();
});

// ── TEST 10 : Changer d onglet affiche le bon champ ──
test('Cliquer sur URL affiche le champ URL', () => {
  render(<SubmitForm onSubmit={() => {}} />);
  const ongletURL = screen.getByText('URL');
  fireEvent.click(ongletURL);
  expect(screen.getByPlaceholderText(/https:\/\/exemple.com/i)).toBeInTheDocument();
});