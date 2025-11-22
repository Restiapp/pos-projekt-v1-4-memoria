# CLAUDE.md - Agent Guidelines

## Project Overview
This repository contains a Point of Sale (POS) system with a microservices architecture.
- **Backend:** Python (FastAPI), SQLAlchemy, Pydantic.
- **Frontend:** React (TypeScript), Vite.
- **Infrastructure:** Docker Compose.

## Agent Roles
- **Jules (Coordinator):** Manages the sprint plan, assigns tasks, and maintains context.
- **Web Claude (Feature Dev):** Implements specific issues/features on remote branches.
- **VS Claude (Integrator):** Runs locally, merges branches, runs full integration tests, and manages the deployment.

## Development Workflow
1. **Code Style:**
   - Backend: Follow PEP 8. Use `black` for formatting if available.
   - Frontend: Follow standard ESLint/Prettier rules.
2. **State Management:**
   - Do NOT assume the state of the database. Always check models.
   - Do NOT delete existing code unless explicitly instructed. Refactor or deprecate instead.
3. **Testing:**
   - Backend tests run in Docker containers.
   - Frontend tests use Playwright.

## Commands
### Backend
- **Start All:** `docker compose up --build`
- **Run Tests (Specific Service):** `docker compose exec <service_name> pytest`
  - Example: `docker compose exec service_orders pytest`
- **Run All Tests:** (Requires script) or run individually per service.

### Frontend
- **Install:** `npm install --prefix frontend`
- **Dev Server:** `npm run dev --prefix frontend`
- **Build:** `npm run build --prefix frontend`
- **Test (Unit):** `npm run test --prefix frontend`
- **Test (E2E):** `npx playwright test --config=frontend/playwright.config.ts`

## Directory Structure
- `backend/`: Contains microservices (`service_*`).
  - Each service has `models/`, `routers/`, `schemas/`, `tests/`.
- `frontend/`: React application.
- `docker-compose.yml`: Orchestration.

## Key Constraints
- **Mocking:** When testing FastAPI endpoints, prefer integration tests with a test DB over complex mocking.
- **JSONB:** Use `CompatibleJSON` type decorator for `JSONB` columns to ensure SQLite compatibility in tests.
