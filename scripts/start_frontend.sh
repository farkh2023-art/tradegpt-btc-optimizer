#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../frontend"
echo "Installation des dépendances npm..."
npm install
echo "Démarrage du frontend React sur http://localhost:5173"
npm run dev
