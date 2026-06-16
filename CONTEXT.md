# Alpha Trade India - Project Context Ledger
This document serves as the project ledger, tracking architectural decisions, current system state, directory layouts, and known gaps. It is updated after reviewing the repository structure and active code paths.

---

## 1. Project Summary
**Alpha Trade India** is a modular, hybrid trading platform combining a Python/FastAPI backend with a React/Vite frontend. The system is built around a live trading orchestrator that integrates with Angel One's SmartAPI to scan market data, apply an Opening Range Breakout (ORB) strategy, and stream real-time prices to a dashboard.

The product aims to provide a live command center for intraday trading, with features for market scanning, watchlist management, settings sync, and real-time position visibility.

---

## 2. Current Development Phase
- **Active Status**: Phase 2 — Live Trading Orchestration and UI Integration.
- **Next Up**: Phase 3 — Backend endpoint completion, trade history retrieval, risk kill-switch endpoint integration, and production hardening.

---

## 3. Technology Stack & Specifications
- **Backend**: Python 3, FastAPI, SQLAlchemy, SQLite.
- **Frontend**: React 19, Vite, Tailwind CSS 4, React Router v7.
- **Realtime**: FastAPI WebSocket for browser dashboard updates.
- **Broker Integration**: Angel One `SmartApi` / `SmartWebSocketV2`.
- **Data/Analytics**: pandas, pandas_ta for historical candle processing and VWAP.
- **Authentication**: OTP-based SmartAPI login via `pyotp` and `.env` credentials.
- **Persistence**: `trades.db` SQLite file for `Trade` and `Config` records.

---

## 4. Completed Milestones
### Phase 1: Modular Backend & Database Setup (Completed)
- Built a FastAPI app in `backend/app/main.py` with CORS enabled.
- Defined SQLAlchemy models in `backend/app/db/models.py` for `Trade` and `Config`.
- Configured SQLite session management in `backend/app/db/session.py`.
- Added auto table creation at startup using `Base.metadata.create_all(bind=engine)`.

### Phase 2: Trading Orchestration and UI Connectivity (Completed)
- Implemented `backend/app/main_bot.py` orchestrator with market-hour loop, market scanner, live price ingestion, and UI broadcasting.
- Integrated a `StrategyService` in `backend/app/services/strategy.py` using ORB and VWAP rules.
- Implemented risk management in `backend/app/services/risk_manager.py` with daily loss and trade count controls.
- Added `DataStreamer` in `backend/app/services/streamer.py` to connect to Angel One live feeds and update shared state.
- Built `frontend/src/pages/Dashboard.jsx` with WebSocket-based live metrics and active positions display.
- Created UI market scanning and stock search in `frontend/src/pages/MarketExplorer.jsx`.
- Added settings sync UI in `frontend/src/pages/Settings.jsx`.
- Implemented a reusable sidebar navigation in `frontend/src/components/Sidebar.jsx`.

### Phase 2.5: Broker Market Data and Search Support (Completed)
- Added `backend/app/services/script_manager.py` to load the Angel One Scrip Master (`scrip_master.json`) and support NSE stock search.
- Implemented market movers endpoint in `backend/app/api/v1/endpoints/market.py`.
- Built WebSocket endpoint in `backend/app/api/v1/endpoints/ws.py` for live UI streaming.
- Added settings update endpoint in `backend/app/api/v1/endpoints/settings.py`.

---

## 5. Current File Structure
```text
alpha-trade-india/
├── CONTEXT.md
├── .gitignore
├── trades.db
├── backend/
│   ├── .env
│   ├── scrip_master.json
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── main_bot.py
│   │   ├── state.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/
│   │   │           ├── dashboard.py
│   │   │           ├── market.py
│   │   │           ├── settings.py
│   │   │           └── ws.py
│   │   ├── db/
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   └── services/
│   │       ├── broker.py
│   │       ├── connection_manager.py
│   │       ├── market_service.py
│   │       ├── order_manager.py
│   │       ├── risk_manager.py
│   │       ├── script_manager.py
│   │       ├── strategy.py
│   │       └── streamer.py
│   └── logs/
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── eslint.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── index.css
│       ├── App.css
│       ├── assets/
│       ├── components/
│       │   ├── MetricCard.jsx
│       │   └── Sidebar.jsx
│       ├── features/
│       │   └── MarketExplorer.jsx
│       ├── hooks/
│       │   ├── useBotStatus.js
│       │   └── useTradingSocket.js
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── History.jsx
│       │   ├── MarketExplorer.jsx
│       │   └── Settings.jsx
│       ├── services/
│       │   └── api.js
│       └── utils/
└── Documents/
```

---

## 6. Architecture Overview
### Backend
- `backend/app/main.py`: FastAPI entrypoint, CORS, DB initialization, router registration, and startup background task.
- `backend/app/main_bot.py`: Orchestrator loop handling login, watchlist scanning, signal checks, broker streaming, and UI broadcasts.
- `backend/app/db/models.py`: SQLAlchemy `Trade` and `Config` models.
- `backend/app/db/session.py`: SQLite session config using `sqlite:///../trades.db`.
- `backend/app/api/v1/router.py`: Aggregates modular API endpoints for dashboard, market, ws, and settings.
- `backend/app/api/v1/endpoints/market.py`: Market data endpoints including movers, stock search, and watchlist add.
- `backend/app/api/v1/endpoints/ws.py`: WebSocket endpoint for live dashboard updates.
- `backend/app/api/v1/endpoints/settings.py`: Settings update endpoint.
- `backend/app/services/broker.py`: Angel One login and SmartAPI session management.
- `backend/app/services/streamer.py`: WebSocket market feed subscription and live price updates into shared state.
- `backend/app/services/strategy.py`: ORB/VWAP-based trade signal generation and entry/exit logic.
- `backend/app/services/order_manager.py`: Trade placement abstraction and SQLite logging.
- `backend/app/services/risk_manager.py`: Daily loss, max trade count, position sizing, kill-switch state.
- `backend/app/services/script_manager.py`: Scrip Master loader and search for NSE equities.
- `backend/app/services/market_service.py`: Market mover construction from dynamic universe.
- `backend/app/services/connection_manager.py`: WebSocket connection manager for UI broadcast.
- `backend/app/state.py`: Shared runtime state for latest prices and MTM.

### Frontend
- `frontend/src/App.jsx`: React Router shell with routes to dashboard, market explorer, settings, and history.
- `frontend/src/pages/Dashboard.jsx`: Live portfolio UI, WebSocket integration, emergency square-off button, active positions table.
- `frontend/src/pages/MarketExplorer.jsx`: Search across NSE stocks, display top gainers/losers, add stocks to bot watchlist.
- `frontend/src/pages/Settings.jsx`: Capital and max trade controls synced to backend.
- `frontend/src/pages/History.jsx`: Placeholder trade history page.
- `frontend/src/components/Sidebar.jsx`: Navigation UI.
- `frontend/src/components/MetricCard.jsx`: Reusable dashboard metric card.
- `frontend/src/hooks/useTradingSocket.js`: WebSocket connection lifecycle and live data state.
- `frontend/src/services/api.js`: Axios REST client to `http://127.0.0.1:8000/api/v1`.

---

## 7. Known Gaps / Work In Progress
- `frontend` includes a kill switch action (`/risk/kill`) but a corresponding backend route is not present in the current codebase.
- `frontend` routes to `History` but there is no backend history endpoint exposing saved trades.
- Backend dependency management is not captured in a requirements file; dependencies are inferred from imports.
- The backend currently logs trades and settings to SQLite, but there is no explicit migration or versioning system.
- `backend/.env` contains live credentials and should remain gitignored; a secure secrets management plan is advised.

---

## 8. Environment & Run Notes
- Backend entrypoint: `backend/app/main.py`.
- Frontend dev server: `frontend` directory with `npm run dev`.
- SQLite file: `trades.db` at repository root.
- Environment file: `backend/.env`.
- Backend WebSocket URL used by frontend: `ws://localhost:8000/api/v1/ws/live`.

---

## 9. Suggested Next Development Focus
1. Implement the missing `/risk/kill` backend route and wire it to `RiskManager.activate_kill_switch()`.
2. Add trade history API exposure and connect `frontend/src/pages/History.jsx`.
3. Create explicit Python dependency tracking (`requirements.txt` or `pyproject.toml`).
4. Harden the live bot loop with disconnect recovery and error state handling.
5. Add config persistence for `capital` and `max_trades` to ensure UI changes reflect the live strategy engine.
