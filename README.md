# AI Market-Intelligence Platform

This project turns global + Indian information into usable trading signals.

## Product Definition
1. Collects data from news, social trends, and live market prices.
2. Uses AI to score each event for sentiment, impact strength, affected assets, and time horizon.
3. Confirms with price action (volume/volatility/trend) to reduce false alerts.
4. Sends user alerts with event summary, expected movers, confidence score, and risk warning.
5. Supports optional broker auto-trading later with strict risk controls.

## What You Sell
1. API product: event analysis, sentiment/impact, and signal endpoints.
2. Trader dashboard/app: live alerts, watchlists, explainable signal cards.

## Core Modules
- Ingestion (news/social/market feeds)
- NLP + Impact engine
- Signal engine
- Risk engine
- Alert delivery (Telegram/email/webhooks)
- API + billing + auth
- Monitoring + audit logs + compliance

## Backend API
- `GET /health`
- `GET /api/v1/intelligence/overview`
- `POST /api/v1/intelligence/analyze-event`
- `POST /api/v1/intelligence/generate-signal`
- `POST /api/v1/intelligence/send-alert`
- `GET /api/v1/intelligence/audit/decision-log`

## Run Locally
1. Backend
   - `cd backend`
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload`
2. Frontend
   - `cd frontend`
   - `npm install`
   - `npm run dev`

## Notes
- `backend/requirements-ml.txt` contains optional heavy ML stack.
- Docker/Kubernetes infra remains in `infra/` for production expansion.

## Real-time Connectors
Backend now ingests Indian market intelligence from:
- Business journals/newspapers RSS: Economic Times, Moneycontrol, Business Standard, Mint, The Hindu (Business)
- Social media: Reddit (IndianStreetBets, IndiaInvestments, stocks)
- X API (optional, when `X_BEARER_TOKEN` is configured)

### Connector APIs
- `GET /api/v1/intelligence/connectors/sources`
- `GET /api/v1/intelligence/connectors/status`
- `POST /api/v1/intelligence/connectors/refresh-live?limit_per_source=20&india_only=true`
- `GET /api/v1/intelligence/connectors/live-events?limit=30&region=IN`

`/api/v1/intelligence/live-signals` uses this live connector pipeline and converts events into actionable signal cards.
