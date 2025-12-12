# Development Guide

## 1. Project Structure

### Root Directory
```text
.
├── backend/                # Python FastAPI Backend
├── frontend/               # React TypeScript Frontend
├── docs/                   # Documentation (PRD, Dev Guides)
├── docker-compose.yml      # Infrastructure (Postgres, Redis)
└── README.md               # Quick Start
```

### Backend Structure (`/backend`)
Follows a layered architecture pattern:
```text
app/
├── api/                    # API Route Controllers
│   └── v1/                 # Versioned API endpoints
├── core/                   # Core configurations
│   ├── config.py           # Environment variables (Pydantic)
│   └── db.py               # Database connection (Async SQLAlchemy)
├── models/                 # ORM Models (Database Schema)
├── schemas/                # Pydantic Schemas (Request/Response Validation)
├── services/               # Business Logic Layer (Complex operations)
├── strategies/             # Quant Trading Strategies
└── main.py                 # Application Entry Point
```

### Frontend Structure (`/frontend`)
Standard Vite + React + TypeScript structure:
```text
src/
├── api/                    # API Integration (Axios wrappers)
├── components/             # Reusable UI Components
├── layouts/                # Page Layouts (Sidebar, Header)
├── pages/                  # Route Components (Dashboard, Trade)
├── store/                  # Global State (Zustand)
├── types/                  # TypeScript Interfaces
├── utils/                  # Helper functions (Request, Formatting)
└── main.tsx                # Entry Point
```

## 2. Development Standards

### 🐍 Backend (Python)
*   **Dependency Management**: Use `poetry`.
    *   Add lib: `poetry add <package>`
    *   Add dev lib: `poetry add -D <package>`
*   **Code Style**: Enforced via `pre-commit`.
    *   **Black**: Code formatting.
    *   **Isort**: Import sorting.
    *   **Typing**: Use Type Hints everywhere (Python 3.10+ syntax).
*   **Async/Await**: Use `async def` for all I/O bound operations (DB, Network).
*   **Comments**: English comments for logic explanation. Docstrings for functions/classes.

### ⚛️ Frontend (TypeScript)
*   **Framework**: React Functional Components + Hooks.
*   **UI Library**: Ant Design (Follow their design patterns).
*   **State Management**:
    *   Local state: `useState`
    *   Global state: `zustand` (Avoid Redux unless necessary).
    *   Server state: `react-query` (Recommended for future).
*   **Linting**: ESLint + Prettier (Standard Vite config).

### 🔄 Git Workflow
1.  **Commit Messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/).
    *   `feat: add user login`
    *   `fix: resolve order execution bug`
    *   `docs: update readme`
2.  **Pre-commit**: Run `pre-commit install` in the backend directory to ensure code quality before committing.

## 3. Configuration
*   **Environment Variables**:
    *   Backend: Copy `.env.example` (if exists) or create `.env`.
    *   Frontend: Use `.env` or `.env.local` with `VITE_` prefix.
