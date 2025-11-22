# GEMINI_AGENT.md - Agent Guidelines

## Project Context
You are working on a modular POS system. The system is split into:
- **Frontend:** React + TypeScript + Vite
- **Backend:** Multiple FastAPI microservices

## Architecture Notes
- **Service Communication:** Services communicate via HTTP APIs (internal) or Event Bus (RabbitMQ/Redis - *check implementation*).
- **Database:** PostgreSQL in production, SQLite for local testing (watch out for JSONB compatibility).
- **Shared Libs:** Currently, code is duplicated or shared via `pymath` style libs (check `backend/common` if it exists, otherwise respect service isolation).

## Running the System
The system is containerized.
- To run: `docker compose up --build`
- API Gateway/Proxy: The frontend Vite proxy forwards `/api` requests to the backend services.

## Testing Strategy
1. **Unit Tests:** pytest in each service.
2. **Integration Tests:** Use `docker compose exec` to run tests inside the container environment.
3. **E2E:** Playwright tests in `frontend/e2e`.

## Task Execution
- When given a task, first **read the relevant files**.
- **Plan** your changes.
- **Implement** incrementally.
- **Verify** by running tests (if environment allows) or creating a reproduction script.
