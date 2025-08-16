# My First Bank App — Complete Development Guide

## Project Title

My First Bank App — Parent‑managed virtual bank accounts for children

## Overview

**Goal:** Build a cross‑platform mobile app (React Native + TypeScript) with a FastAPI + PostgreSQL backend so parents can create child profiles and manage virtual checking and savings accounts for them (virtual money only — no real payments).

**Primary users:** Parents who want to allocate and track pocket money for children.

---

## MVP (v0.1) — Scope

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

### 2. Backend Testing Matrix
* **Python 3.11 & 3.12:** Run linting, type checking, and tests
* **Linting:** Black formatting, isort import sorting, Flake8 linting
* **Type Checking:** MyPy static type analysis
* **Testing:** Pytest with coverage reporting (XML, HTML, terminal)
* **Artifacts:** Upload coverage reports and test results

### 3. Frontend Testing Matrix
* **Node.js 18 & 20:** Install dependencies, run linting, build, and tests
* **Linting:** ESLint for code quality
* **Type Checking:** TypeScript compilation check
* **Build:** Verify production build succeeds
* **Testing:** Playwright E2E tests with HTML and JUnit reporting
* **Artifacts:** Upload Playwright reports and test results

### 4. Integration Testing
* Start full application stack (PostgreSQL, Backend, Frontend)
* Health checks for all services
* Run integration tests (when implemented)

### 5. Security & Performance
* **Security:** Trivy vulnerability scanning
* **Performance:** Docker Compose-based performance tests

### 6. Summary & Reporting
* Generate comprehensive test summary
* Console integration with rich formatting
* Artifact collection and reporting

---

## Development Instructions

### Prerequisites

#### System Requirements
- **Operating System**: Linux (WSL2), macOS, or Windows
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Node.js**: Version 18 or higher
- **Python**: Version 3.11 or higher
- **Git**: Latest version

#### Required Software
- Docker Desktop
- VS Code or preferred IDE
- PostgreSQL client (optional, for direct database access)

### Environment Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/erickuiper/my-first-bank-app.git
cd my-first-bank-app
```

#### 2. Environment Variables
Create a `.env` file in the root directory:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/bankapp

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=My First Bank App
DEBUG=true

# Limits
MAX_DEPOSIT_AMOUNT_CENTS=1000000
MIN_DEPOSIT_AMOUNT_CENTS=1
```

#### 3. Start the Environment
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 3000

### Backend Development

#### Project Structure
```
backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py
│   │   │   ├── children.py
│   │   │   └── accounts.py
│   │   └── api.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── deps.py
│   │   └── security.py
│   ├── models/
│   │   ├── user.py
│   │   ├── child.py
│   │   ├── account.py
│   │   └── transaction.py
│   └── schemas/
│       ├── user.py
│       ├── child.py
│       ├── account.py
│       └── transaction.py
├── tests/
│   ├── test_api.py
│   └── test_deposit_logic.py
├── alembic/
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

#### Key Components

**Models (`app/models/`):**
- **User**: Parent accounts with email/password authentication
- **Child**: Child profiles linked to parent users
- **Account**: Virtual checking/savings accounts for children
- **Transaction**: Financial transactions with idempotency support

**API Endpoints (`app/api/v1/endpoints/`):**
- **Auth**: User registration and login
- **Children**: Child profile management
- **Accounts**: Account operations and transaction history

**Core Services (`app/core/`):**
- **Database**: Async SQLAlchemy setup and session management
- **Security**: JWT token handling and password hashing
- **Config**: Environment-based configuration management
- **Deps**: FastAPI dependency injection utilities

#### Development Commands

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ --cov=app --cov-report=term-missing

# Run linting
black . --line-length=120
isort . --profile=black --line-length=120
flake8 . --max-line-length=120

# Run type checking
mypy . --config-file=pyproject.toml

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "Description"
```

### Frontend Development

#### Project Structure
```
frontend/
├── src/
│   ├── screens/
│   │   ├── DashboardScreen.tsx
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── ChildProfileScreen.tsx
│   │   ├── AccountScreen.tsx
│   │   └── DepositScreen.tsx
│   ├── contexts/
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   └── utils/
│       └── currency.ts
├── tests/e2e/
│   ├── auth.spec.ts
│   └── diagnostic.spec.ts
├── package.json
├── App.tsx
└── Dockerfile
```

#### Key Features

**Authentication Flow:**
- User registration and login
- JWT token management
- Protected route handling

**Child Management:**
- Create and view child profiles
- Automatic account creation (checking/savings)
- Balance display and transaction history

**Transaction System:**
- Deposit functionality with validation
- Idempotency support
- Paginated transaction history

#### Development Commands

```bash
# Install dependencies
cd frontend
npm ci

# Start development server
npm start

# Run web version
npm run web

# Run tests
npm test

# Run Playwright tests
npx playwright test

# Build for production
npm run build

# Linting and type checking
npm run lint
npm run type-check
```

### Testing Strategy

#### Backend Testing
- **Unit Tests**: Core business logic (deposit calculations, idempotency)
- **Integration Tests**: API endpoint testing with TestClient
- **Database Tests**: Transaction isolation and ACID compliance
- **Coverage Target**: 80%+ code coverage

#### Frontend Testing
- **E2E Tests**: Playwright for user flow validation
- **Component Tests**: React component testing (when implemented)
- **API Integration**: Frontend-backend communication testing

#### Test Commands

```bash
# Backend tests
cd backend
pytest tests/ --cov=app --cov-report=html

# Frontend tests
cd frontend
npx playwright test --reporter=html

# Run all tests
pre-commit run --all-files
```

### Database Management

#### Schema Overview
- **users**: Parent user accounts
- **children**: Child profiles linked to parents
- **accounts**: Virtual accounts (checking/savings)
- **transactions**: Financial transaction records

#### Migration Commands

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Docker Development

#### Services
- **PostgreSQL**: Database with persistent volume
- **Backend**: FastAPI application with hot reload
- **Frontend**: React Native web with Expo

#### Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Access database
docker-compose exec postgres psql -U postgres -d bankapp
```

### Code Quality & Linting

#### Python (Backend)
- **Black**: Code formatting (120 character line length)
- **isort**: Import sorting (Black-compatible profile)
- **Flake8**: Linting with custom rules
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanning

#### TypeScript/JavaScript (Frontend)
- **ESLint**: Code quality and consistency
- **TypeScript**: Static type checking
- **Prettier**: Code formatting (when implemented)

#### Configuration Files
- `backend/pyproject.toml`: Centralized Python tool configuration
- `frontend/.eslintrc.js`: ESLint configuration
- `frontend/tsconfig.json`: TypeScript configuration
- `.pre-commit-config.yaml`: Pre-commit hooks configuration

### Pre-Commit Checklist for CI/CD Success

**IMPORTANT**: Complete ALL of these steps locally before committing to avoid CI/CD failures and multiple pipeline iterations.

#### 1. Backend Code Quality (Required)
```bash
cd backend

# 1. Black formatting check
black . --line-length=120 --check

# 2. isort import sorting check
isort . --profile=black --line-length=120 --check-only

# 3. Flake8 linting check
flake8 . --max-line-length=120

# 4. MyPy type checking
mypy . --config-file=pyproject.toml

# 5. Pytest collection and execution
pytest --collect-only
pytest tests/ --cov=app --cov-report=term-missing
```

#### 2. Frontend Code Quality (Required)
```bash
cd frontend

# 1. ESLint linting
npm run lint

# 2. TypeScript type checking
npm run type-check

# 3. Build verification
npm run build
```

#### 3. Full Stack Integration
```bash
# 1. Start services
docker-compose up -d

# 2. Wait for services to be ready
sleep 30

# 3. Verify backend health
curl -f http://localhost:8000/health

# 4. Verify frontend loads
curl -f http://localhost:3000/
```

#### 4. Pre-commit Hook Execution
```bash
# Install pre-commit hooks (first time only)
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg

# Run all hooks
pre-commit run --all-files
```

#### Common CI/CD Failure Points

**Backend Issues:**
- MyPy type errors (currently disabled in pre-commit)
- Black formatting differences
- Import sorting issues
- Test failures or missing dependencies

**Frontend Issues:**
- TypeScript compilation errors
- ESLint violations
- Build failures
- Missing dependencies

**Integration Issues:**
- Database connection problems
- Service startup failures
- Port conflicts

#### Step-by-Step Pre-commit Workflow

1. **Code Changes**: Make your changes
2. **Local Testing**: Run backend and frontend quality checks
3. **Service Verification**: Ensure Docker services are running
4. **Pre-commit Hooks**: Run `pre-commit run --all-files`
5. **Fix Issues**: Address any failures before committing
6. **Commit**: Use conventional commit format
7. **Push**: Monitor CI/CD pipeline results

---

## MVP Version 0.2 Roadmap

### Overview
MVP 0.2 focuses on enhancing the educational value of the app by implementing chore-based allowance systems and recurring bill rules, while also improving the technical foundation for future development.

### Core Features (Priority 1)

#### 1. Chore-Based Allowance System
**Goal**: Implement a weekly allowance system where children earn money based on completed chores.

**User Stories:**
- As a parent, I can define a weekly allowance rule for a child (base_amount_cents, frequency=weekly)
- As a parent, I can define chores with expected completion per pay period and penalties (penalty_cents per missed chore)
- On each scheduled pay run, the system calculates earned_allowance = base_amount - penalty * missed_chores, creates transactions, and deposits the earned amount into the designated account (checking by default)

**Data Models:**
```sql
-- Allowance rules
allowance_rules (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES children(id),
    base_amount_cents INTEGER NOT NULL,
    frequency VARCHAR(20) DEFAULT 'weekly',
    pay_day VARCHAR(20) DEFAULT 'friday', -- day of week
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chore definitions
chores (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES children(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    expected_per_week INTEGER DEFAULT 1,
    penalty_cents INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chore completion tracking
chore_completions (
    id SERIAL PRIMARY KEY,
    chore_id INTEGER REFERENCES chores(id),
    completed_at TIMESTAMP DEFAULT NOW(),
    verified_by INTEGER REFERENCES users(id), -- parent verification
    notes TEXT
);
```

**API Endpoints:**
```python
# Allowance management
POST /children/{child_id}/allowance-rules
GET /children/{child_id}/allowance-rules
PUT /allowance-rules/{rule_id}
DELETE /allowance-rules/{rule_id}

# Chore management
POST /children/{child_id}/chores
GET /children/{child_id}/chores
PUT /chores/{chore_id}
DELETE /chores/{chore_id}

# Chore completion
POST /chores/{chore_id}/complete
GET /children/{child_id}/chore-summary

# Manual allowance payout
POST /children/{child_id}/allowance-payout
```

**Frontend Screens:**
- Chore Management Screen (parent)
- Chore Completion Screen (child)
- Allowance Rules Screen (parent)
- Weekly Summary Screen (parent/child)

**Implementation Priority**: High
**Effort Estimate**: 3-4 weeks

#### 2. Recurring Bill Rules
**Goal**: Implement automated monthly bills that teach children about recurring expenses.

**User Stories:**
- As a parent, I can define recurring bill rules (amount_cents, description, due_date rule e.g., last day of month) that create scheduled transactions which move money to savings (or just tag transactions as bills)

**Data Models:**
```sql
-- Bill rules
bill_rules (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES children(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    amount_cents INTEGER NOT NULL,
    due_day INTEGER DEFAULT 28, -- day of month
    account_type VARCHAR(20) DEFAULT 'savings', -- which account to debit
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bill transactions (auto-generated)
bill_transactions (
    id SERIAL PRIMARY KEY,
    bill_rule_id INTEGER REFERENCES bill_rules(id),
    amount_cents INTEGER NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, overdue
    created_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints:**
```python
# Bill rule management
POST /children/{child_id}/bill-rules
GET /children/{child_id}/bill-rules
PUT /bill-rules/{rule_id}
DELETE /bill-rules/{rule_id}

# Bill transaction management
GET /children/{child_id}/bills
POST /bills/{bill_id}/mark-paid
GET /children/{child_id}/bill-summary
```

**Frontend Screens:**
- Bill Rules Management (parent)
- Bill Payment Screen (child)
- Monthly Bill Summary (parent/child)

**Implementation Priority**: High
**Effort Estimate**: 2-3 weeks

#### 3. Backend Deployment to Heroku
**Goal**: Deploy the backend to production using GitHub pipelines for automated deployment.

**Implementation Steps:**
1. Create Heroku app and configure environment variables
2. Set up GitHub Actions deployment workflow
3. Configure database (Heroku Postgres)
4. Implement health checks and monitoring
5. Set up logging and error tracking

**API Endpoints:**
```python
# Health and monitoring
GET /health
GET /metrics
GET /status
```

**Implementation Priority**: High
**Effort Estimate**: 1-2 weeks

#### 4. Android App Development
**Goal**: Create a native Android app for the frontend and test it on a test device.

**Implementation Steps:**
1. Configure Expo for Android builds
2. Implement Android-specific features
3. Test on physical device
4. Optimize for mobile performance
5. Implement push notifications (optional)

**Implementation Priority**: Medium
**Effort Estimate**: 2-3 weeks

### Technical Improvements

#### 1. In-Memory Database Testing
**Goal**: Remove the skipped CI/CD tests in later releases by implementing comprehensive in-memory database testing.

**Implementation:**
- Use SQLite in-memory database for CI/CD tests
- Convert TestClient integration tests to use in-memory database
- Remove CI/CD skip conditions
- Achieve 80%+ backend test coverage

**Benefits:**
- Faster CI/CD pipeline execution
- More reliable test results
- Better code quality assurance

**Implementation Priority**: High
**Effort Estimate**: 1-2 weeks

#### 2. Enhanced Security
**Goal**: Improve authentication and authorization systems.

**Features:**
- Refresh token implementation
- Rate limiting for API endpoints
- Input validation improvements
- Security headers and CORS configuration

**Implementation Priority**: Medium
**Effort Estimate**: 1-2 weeks

#### 3. Performance Optimization
**Goal**: Improve application performance and scalability.

**Features:**
- Database query optimization
- Caching implementation (Redis)
- API response optimization
- Frontend performance improvements

**Implementation Priority**: Low
**Effort Estimate**: 2-3 weeks

### Implementation Phases

#### Phase 1: Core Business Logic (Weeks 1-4)
1. Implement chore-based allowance system
2. Implement recurring bill rules
3. Add comprehensive testing

#### Phase 2: Infrastructure (Weeks 5-6)
1. Deploy backend to Heroku
2. Set up monitoring and logging

#### Phase 3: Mobile Development (Weeks 7-9)
1. Develop Android app
2. Test on physical device
3. Optimize mobile experience

#### Phase 4: Testing & Quality (Weeks 10-11)
1. Implement in-memory database testing
2. Remove CI/CD skip conditions
3. Achieve 80%+ test coverage

### Success Metrics

#### Functional Metrics
- 100% of chore-based allowance features working
- 100% of recurring bill features working
- Backend successfully deployed to Heroku
- Android app functional on test device

#### Technical Metrics
- 80%+ backend test coverage
- All CI/CD tests passing without skips
- Sub-2 second API response times
- 99.9% uptime on production backend

#### User Experience Metrics
- Parent can successfully set up allowance rules
- Children can complete chores and see earnings
- Bill payments are automated and tracked
- Mobile app provides smooth user experience

---

## Troubleshooting

### Common Issues

#### Backend Issues
**Database Connection Errors:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Restart database service
docker-compose restart postgres
```

**Import Errors:**
```bash
# Ensure you're in the backend directory
cd backend

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Verify imports
python -c "from app.core.config import settings; print('OK')"
```

**MyPy Type Errors:**
```bash
# Run MyPy with verbose output
mypy . --config-file=pyproject.toml --show-error-codes

# Check specific file
mypy app/api/v1/endpoints/auth.py --config-file=pyproject.toml
```

#### Frontend Issues
**Build Failures:**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm ci

# Check TypeScript errors
npm run type-check

# Verify build configuration
npm run build
```

**Playwright Test Failures:**
```bash
# Install/update Playwright browsers
npx playwright install --with-deps

# Run tests with debug output
npx playwright test --debug

# Check browser compatibility
npx playwright test --project=chromium
```

#### Docker Issues
**Service Startup Failures:**
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs [service_name]

# Restart all services
docker-compose down
docker-compose up -d

# Check resource usage
docker stats
```

**Port Conflicts:**
```bash
# Check what's using a port
sudo netstat -tulpn | grep :8000

# Kill process using port
sudo kill -9 [PID]

# Use different ports in docker-compose.yml
```

### Performance Issues

#### Database Performance
```bash
# Check slow queries
docker-compose exec postgres psql -U postgres -d bankapp -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Analyze table statistics
docker-compose exec postgres psql -U postgres -d bankapp -c "ANALYZE;"
```

#### API Performance
```bash
# Test API response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/health"

# Monitor with htop
htop

# Check memory usage
free -h
```

### Debug Mode

#### Backend Debug
```bash
# Enable debug logging
export DEBUG=true

# Run with debug output
uvicorn app.main:app --reload --log-level debug

# Check environment variables
python -c "from app.core.config import settings; print(settings.dict())"
```

#### Frontend Debug
```bash
# Enable React DevTools
export REACT_DEVTOOLS_GLOBAL_HOOK=1

# Run with debug output
DEBUG=* npm start

# Check browser console for errors
```

---

## Contributing

### Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/feature-name`
2. **Make Changes**: Implement your feature with tests
3. **Run Quality Checks**: Complete pre-commit checklist
4. **Test Locally**: Verify all tests pass
5. **Commit Changes**: Use conventional commit format
6. **Push Branch**: `git push origin feature/feature-name`
7. **Create PR**: Submit pull request for review

### Code Standards

- **Python**: Follow PEP 8 with Black formatting
- **TypeScript**: Use strict TypeScript configuration
- **Testing**: Maintain 80%+ test coverage
- **Documentation**: Update this guide for new features
- **Commits**: Use conventional commit format

### Review Process

1. **Code Review**: All changes require review
2. **Testing**: Ensure all tests pass
3. **Documentation**: Update relevant documentation
4. **Approval**: At least one approval required
5. **Merge**: Squash and merge to main branch

---

## Support & Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Native Documentation](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Playwright Documentation](https://playwright.dev/)

### Community
- [FastAPI Community](https://github.com/tiangolo/fastapi/discussions)
- [React Native Community](https://github.com/react-native-community/discussions-and-proposals)
- [Expo Community](https://forums.expo.dev/)

### Tools & Services
- [GitHub Actions](https://github.com/features/actions)
- [Docker Hub](https://hub.docker.com/)
- [Heroku](https://www.heroku.com/)
- [Codecov](https://codecov.io/)

---

*Last updated: August 2024*
*Version: 1.0 - Complete Development Guide*
