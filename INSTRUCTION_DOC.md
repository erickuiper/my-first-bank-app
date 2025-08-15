# My First Bank App — INSTRUCTION_DOC.md

## Project Title

My First Bank App — Parent‑managed virtual bank accounts for children

## Overview

**Goal:** Build a cross‑platform mobile app (React Native + TypeScript) with a FastAPI + PostgreSQL backend so parents can create child profiles and manage virtual checking and savings accounts for them (virtual money only — no real payments).

**Primary users:** Parents who want to allocate and track pocket money for children.

---

## MVP (v0.1) — scope

**Core features (must be implemented for MVP):**

* Parent authentication (email + password, JWT).
* Parent can create and list child profiles (name, birthdate).
* Each child has two virtual accounts automatically created: `checking` and `savings` (starting balance = 0).
* Parent can deposit virtual money into an account with idempotency support.
* Parent can view account balances and transaction history.
* Transaction history is cursor (keyset) paginated; mobile client implements infinite scroll.

**Non‑functional essentials (MVP must include):**

* Transaction ledger + ACID correctness (no balance races).
* Idempotency for deposits (client provides `idempotency_key`).
* Currency correctness: store amounts in integer cents (`BIGINT`) or Decimal with explicit scale — no floats.
* Authentication & access control: parents can only operate on their children/accounts.
* Input validation & reasonable limits (min > 0, max per deposit).
* Tests: unit tests for deposit logic and concurrency; API tests for auth and pagination; Playwright E2E tests for frontend user flows.
* Basic logging, error handling, and meaningful error responses.

---

## Success criteria / Acceptance tests

Automate where possible; otherwise provide manual verification steps.

### Auth

* Parent can register and receive a JWT.
* Protected endpoints return `401` without a valid JWT.
* **Frontend:** User can successfully register, login, and logout through the UI (Playwright test).

### Child & accounts

* Creating a child returns the child record and two accounts: `checking` and `savings`, both with balance `0`.
* Parent can list their children.
* **Frontend:** User can view the dashboard with child profiles and account information (Playwright test).

### Deposit & ledger

* `POST /accounts/{id}/deposit` with `amount_cents` and `idempotency_key`:
  * Creates a transaction record.
  * Updates account balance atomically.
  * Returns the transaction and new balance.
* Replaying the same `idempotency_key` does NOT create a duplicate transaction.
* Concurrent deposits produce consistent final balance (test by running N concurrent deposits and assert sum equals final balance).
* **Frontend:** User can navigate to deposit screen, enter amount, and successfully make deposits (Playwright test).

### Transactions & pagination

* `GET /accounts/{id}/transactions?limit=20` returns up to `limit` items + `next_cursor` when more pages exist.
* Cursor navigation is deterministic and stable across inserts.
* **Frontend:** User can view transaction history and navigate through paginated results (Playwright test).

---

## Tech stack & infra

* Backend: Python 3.11+, FastAPI, async SQLAlchemy / SQLAlchemy core (or Databases), Alembic for migrations.
* DB: PostgreSQL 13+.
* Mobile: React Native + TypeScript (Expo managed recommended for v0.1).
* Auth: JWT (short-lived access token; refresh tokens optional).
* Testing: pytest, httpx for API tests; Playwright for frontend E2E tests.
* CI/CD: GitHub Actions with comprehensive test suites, linting, and console integration.
* Local dev: Docker + docker-compose (postgres + backend + frontend).
* Lint/format: black / isort for Python, ESLint/Prettier for TypeScript.
* Frontend testing: Playwright with web-first approach for React Native web builds.

---

## GitHub CI/CD Pipeline Requirements

**Pipeline Structure:**
* **Trigger:** On push to main branch, pull requests, and manual workflow dispatch
* **Matrix Strategy:** Test against multiple Python versions (3.11, 3.12) and Node.js versions (18, 20)
* **Parallel Execution:** Backend and frontend tests run in parallel for efficiency
* **Artifact Management:** Test results, coverage reports, and Playwright reports stored as artifacts
* **Console Integration:** Rich console output with test summaries, coverage metrics, and failure details

**Pipeline Stages:**

### 1. Setup & Dependencies
* Checkout code
* Setup Python (3.11, 3.12) and Node.js (18, 20) environments
* Install system dependencies (PostgreSQL, Playwright browsers)
* Cache dependencies for faster builds

### 2. Backend Testing Matrix
* **Python 3.11 & 3.12**
* Install Python dependencies
* Run linting (black, isort, flake8)
* Run type checking (mypy)
* Run unit tests with pytest
* Generate coverage reports
* Run API integration tests
* Performance testing for concurrent operations

### 3. Frontend Testing Matrix
* **Node.js 18 & 20**
* Install Node.js dependencies
* Run linting (ESLint, Prettier)
* Run type checking (TypeScript)
* Build React Native web bundle
* Run Playwright E2E tests
* Generate Playwright HTML reports
* Test responsive design across viewports

### 4. Integration Testing
* Full-stack testing with Docker Compose
* Database migration testing
* API endpoint validation
* Frontend-backend integration tests

### 5. Quality Gates
* All tests must pass
* Coverage thresholds (backend: 80%, frontend: 70%)
* No critical security vulnerabilities
* Performance benchmarks met

### 6. Artifacts & Reporting
* Test results in JUnit XML format
* Coverage reports (HTML + XML)
* Playwright HTML reports with screenshots/videos
* Performance metrics
* Security scan results

---

## Frontend Testing with Playwright

**Requirements:**
* Install Playwright as a dev dependency in the frontend project.
* Configure Playwright to test the React Native web build.
* Create E2E test suites covering:
  * User registration and login flows
  * Dashboard navigation and child profile viewing
  * Account detail viewing and transaction history
  * Deposit functionality with form validation
  * Error handling and edge cases
* Tests should run in CI/CD pipeline.
* Tests should be able to run against local Docker containers.

**Test Structure:**
```
frontend/tests/
├── e2e/
│   ├── auth.spec.ts          # Registration, login, logout
│   ├── dashboard.spec.ts     # Child profiles, account overview
│   ├── accounts.spec.ts      # Account details, transactions
│   ├── deposits.spec.ts      # Deposit flows, validation
│   └── utils/
│       ├── test-data.ts      # Test user data, mock accounts
│       └── helpers.ts        # Common test utilities
├── playwright.config.ts      # Playwright configuration
└── package.json scripts      # Test execution commands
```

**Key Test Scenarios:**
1. **Authentication Flow:** Complete user journey from registration to successful login
2. **Dashboard Experience:** Verify child profiles and account balances display correctly
3. **Account Management:** Test account detail views and transaction pagination
4. **Deposit Workflow:** End-to-end deposit process with validation
5. **Error Handling:** Test form validation, API errors, and edge cases
6. **Responsive Design:** Ensure UI works across different viewport sizes

---

## Console Integration & Monitoring

**CI/CD Console Features:**
* **Real-time Test Progress:** Live updates during test execution with progress bars
* **Test Result Summaries:** Clear pass/fail counts with execution times
* **Coverage Metrics:** Visual representation of code coverage with trend analysis
* **Performance Benchmarks:** Response time and throughput measurements
* **Error Details:** Stack traces, screenshots, and video recordings for failed tests
* **Security Alerts:** Vulnerability scan results and dependency warnings

**Console Output Examples:**
```
✅ Backend Tests (Python 3.11) - PASSED
   📊 Coverage: 87.3% (+2.1% from last run)
   ⚡ Performance: 2.3s avg response time
   🔒 Security: 0 vulnerabilities found

✅ Frontend Tests (Node.js 18) - PASSED
   🎭 Playwright: 24/24 tests passed
   📱 Responsive: All viewport tests passed
   🎨 UI: No visual regressions detected

📈 Integration Tests - PASSED
   🐳 Docker: All services healthy
   🔗 API: 100% endpoint coverage
   🗄️ Database: Migrations successful
```

**Monitoring & Alerts:**
* **Slack/Teams Integration:** Real-time notifications for build status
* **Email Reports:** Daily/weekly summaries of test results
* **Dashboard Integration:** Grafana or similar for metrics visualization
* **Failure Analysis:** Automatic issue creation for failed builds
* **Performance Tracking:** Historical trend analysis and regression detection

---

## Local Development Workflow

**Pre-commit Hooks:**
* Automatic linting and formatting
* Type checking
* Unit test execution
* Security vulnerability scanning

**Development Commands:**
```bash
# Backend
make test          # Run all backend tests
make lint          # Run linting and formatting
make coverage      # Generate coverage report

# Frontend
npm run test:e2e   # Run Playwright tests
npm run lint       # Run ESLint and Prettier
npm run type-check # Run TypeScript compiler

# Full Stack
docker-compose up  # Start all services
make integration   # Run integration tests
```

**Quality Gates:**
* All tests must pass locally before pushing
* Coverage thresholds enforced
* No linting errors or warnings
* Security scans clean
