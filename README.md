# TradeGPT BTC Optimizer

> **Simulation uniquement — pas un conseil financier.**

Générateur, optimiseur et analyseur de stratégies de trading Bitcoin en **Pine Script v5** pour TradingView.

Fonctionnel **sans clé API** grâce au mode mock intégré.

---

## Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| 🤖 Génération IA | Prompt naturel → Pine Script v5 (OpenAI / Anthropic / Mock) |
| 📋 Templates | SMA Cross, Supertrend, RSI, ADX, SMA+RSI+ADX Combined |
| ✏️ Éditeur | Monaco Editor + versioning illimité |
| 🐛 Debug | Détection et correction automatique d'erreurs Pine Script |
| 📊 Backtest | Simulation locale sur données BTC historiques (yfinance) |
| 🔧 Optimisation | Grid search sur plages de paramètres |
| ⚖️ Comparaison | A/B test entre deux stratégies |
| 📄 Rapports | Export Markdown complet par stratégie |

---

## Installation rapide

### Prérequis

- Python 3.11+
- Node.js 20+
- (Optionnel) Docker + Docker Compose

### Windows — démarrage rapide

```powershell
# Cloner le projet
git clone https://github.com/farkh2023-art/tradegpt-btc-optimizer.git
cd tradegpt-btc-optimizer

# Backend
python -m venv backend\.venv
backend\.venv\Scripts\activate
pip install -r backend\requirements.txt
copy .env.example .env

cd backend
python -m uvicorn app.main:app --reload
```

```powershell
# Frontend (autre terminal)
cd frontend
npm install
npm run dev
```

Ou en un clic :
```powershell
.\scripts\start_all.ps1
```

### Linux / macOS

```bash
bash scripts/start_all.sh
```

### Docker

```bash
cp .env.example .env
docker compose up --build
```

---

## URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Documentation API | http://localhost:8000/docs |

---

## Configuration IA

Éditez `.env` :

```env
# Mode sans clé API (défaut)
AI_PROVIDER=mock

# Avec OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Avec Anthropic
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Tests

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Architecture

Voir [ARCHITECTURE.md](ARCHITECTURE.md) pour le détail technique.

## Roadmap

Voir [ROADMAP.md](ROADMAP.md).

## Sécurité

Voir [SECURITY.md](SECURITY.md).

## Disclaimer

Voir [DISCLAIMER.md](DISCLAIMER.md).

---

**Mode paper trading uniquement. Aucun ordre réel n'est jamais exécuté.**
