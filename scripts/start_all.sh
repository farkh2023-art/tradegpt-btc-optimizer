#!/usr/bin/env bash
echo "Démarrage backend + frontend..."
bash "$(dirname "$0")/start_backend.sh" &
sleep 3
bash "$(dirname "$0")/start_frontend.sh" &
echo ""
echo "Backend  : http://localhost:8000"
echo "Frontend : http://localhost:5173"
echo "API docs : http://localhost:8000/docs"
wait
