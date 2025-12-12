# Trading Quant System (MVP)

A modular, full-stack quantitative trading system designed for multi-exchange strategy execution and manual trading.

## 🚀 Quick Start

### Prerequisites
*   **Docker & Docker Compose** (for Database & Redis)
*   **Python 3.10+** (managed via Poetry)
*   **Node.js 18+** (managed via npm/yarn)

### 1. Infrastructure (Database & Redis)
Start the required services using Docker Compose:
```bash
docker-compose up -d
```
This will start:
*   PostgreSQL: `localhost:5432` (User: postgres, Pass: password, DB: trading_quant)
*   Redis: `localhost:6379`

### 2. Backend (FastAPI)
Open a new terminal for the backend:
```bash
cd backend

# Install dependencies
poetry install

# Initialize Database (Migrations/Tables)
# The app creates tables on startup automatically in this MVP version.

# Start the API Server
poetry run uvicorn app.main:app --reload
```
*   API Docs: http://localhost:8000/docs
*   Health Check: http://localhost:8000/api/v1/health

### 3. Frontend (React)
Open a new terminal for the frontend:
```bash
cd frontend

# Install dependencies
npm install

# Start Development Server
npm run dev
```
*   Dashboard: http://localhost:5173

---

## 📚 Documentation
*   [Requirements (PRD)](./docs/MVP_REQUIREMENTS.md)
*   [Development Guide](./docs/DEVELOPMENT.md) (Structure & Standards)

## 🛠 Tech Stack
*   **Backend**: Python, FastAPI, SQLAlchemy (Async), CCXT, Redis
*   **Frontend**: TypeScript, React, Vite, Ant Design, Zustand
*   **Infra**: Docker, PostgreSQL
