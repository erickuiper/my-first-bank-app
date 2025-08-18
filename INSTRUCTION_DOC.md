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

#### 4. Account Configuration and Parental Controls
**Goal**: Implement account PIN configuration and comprehensive parental access controls for enhanced security and oversight.

**User Stories:**
- As a parent, I must set up a PIN code after creating an account for my child
- As a parent, I can access a dedicated parental dashboard to manage all aspects of my children's accounts
- As a parent, I can verify my PIN before making any deposits to ensure security
- As a parent, I can change account PINs when needed

**Data Models:**
```sql
-- Enhanced Account model (add to existing)
ALTER TABLE accounts ADD COLUMN pin_hash VARCHAR(255);
```

**API Endpoints:**
```python
# Account PIN management
POST /accounts/{account_id}/setup-pin
POST /accounts/{account_id}/change-pin
POST /accounts/{account_id}/verify-pin

# Enhanced deposit with PIN verification
POST /accounts/{account_id}/deposit (now requires PIN verification)

# Parental dashboard
GET /parental/dashboard
GET /parental/children/{child_id}/summary
```

**Frontend Screens:**
- Account PIN Setup Screen (parent)
- Parental Dashboard Screen (parent)
- PIN Verification Modal (for deposits)
- Account Management Screen (parent)

**Implementation Priority**: High
**Effort Estimate**: 2-3 weeks

#### 5. Android App Development
**Goal**: Create a native Android app for the frontend and test it on a test device.

**Implementation Steps:**
1. Configure Expo for Android builds
2. Implement Android-specific features
3. Test on physical Android device
4. Optimize for Android performance and UX

**Implementation Priority**: Medium
**Effort Estimate**: 2-3 weeks

### Critical Bug Fixes (Priority 1 - Must Fix)

#### 1. Account Balance Calculation Fix
**Issue**: Money added to an account is not properly reflected in the account total balance.

**Problem Description**:
- When deposits are made to accounts, the transaction is recorded but the account balance is not updated correctly
- This leads to incorrect balance displays and potential financial inconsistencies
- Affects both checking and savings accounts

**Required Fixes**:
- Ensure all deposit transactions properly update the account `balance_cents` field
- Implement proper balance validation before allowing transactions
- Add database constraints to prevent negative balances
- Implement balance reconciliation checks

**Data Model Updates**:
```sql
-- Add balance constraint to prevent negative balances
ALTER TABLE accounts ADD CONSTRAINT positive_balance CHECK (balance_cents >= 0);

-- Add balance validation trigger (if needed)
CREATE OR REPLACE FUNCTION validate_account_balance()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.balance_cents < 0 THEN
        RAISE EXCEPTION 'Account balance cannot be negative';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER account_balance_validation
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION validate_account_balance();
```

**API Endpoint Fixes**:
```python
# Enhanced deposit endpoint with proper balance updates
@router.post("/{account_id}/deposit", response_model=BalanceUpdate)
async def deposit(
    account_id: int,
    transaction_data: TransactionCreate,
    pin_verification: AccountPinVerification,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BalanceUpdate:
    # Verify account access and PIN
    account = await verify_account_access(account_id, current_user, db)
    if not await verify_account_pin(account, pin_verification.pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN verification failed. Deposit not allowed."
        )

    # Validate deposit amount
    if transaction_data.amount_cents <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit amount must be positive"
        )

    # Create transaction record
    transaction = Transaction(
        account_id=account_id,
        amount_cents=transaction_data.amount_cents,
        transaction_type="deposit",
        idempotency_key=transaction_data.idempotency_key
    )

    # Update account balance atomically
    new_balance = account.balance_cents + transaction_data.amount_cents
    account.balance_cents = new_balance
    account.updated_at = datetime.now(timezone.utc)

    # Add transaction and update account in single commit
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    await db.refresh(account)

    return BalanceUpdate(
        new_balance_cents=new_balance,
        transaction=transaction
    )
```

**Testing Requirements**:
- Unit tests for balance calculation accuracy
- Integration tests for concurrent deposits
- Database constraint validation tests
- Balance reconciliation tests

**Implementation Priority**: Critical
**Effort Estimate**: 1-2 weeks

#### 2. Inter-Account Transfer Validation
**Issue**: Money can only be transferred to savings from checking, but without proper balance validation.

**Problem Description**:
- Current system allows transfers to savings account without checking if checking account has sufficient funds
- This could lead to negative balances or overdraft situations
- Transfer logic needs proper validation and error handling

**Required Fixes**:
- Implement proper balance validation before allowing transfers
- Add transfer endpoint with source and destination account validation
- Ensure atomic transactions for transfers (both accounts updated or neither)
- Add proper error messages for insufficient funds

**New API Endpoint**:
```python
# New transfer endpoint
@router.post("/transfer", response_model=dict)
async def transfer_between_accounts(
    transfer_data: TransferRequest,
    pin_verification: AccountPinVerification,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Transfer money between a child's checking and savings accounts."""

    # Verify source account access and PIN
    source_account = await verify_account_access(transfer_data.source_account_id, current_user, db)
    if not await verify_account_pin(source_account, pin_verification.pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN verification failed. Transfer not allowed."
        )

    # Verify destination account access
    dest_account = await verify_account_access(transfer_data.destination_account_id, current_user, db)

    # Validate accounts belong to same child
    if source_account.child_id != dest_account.child_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only transfer between accounts of the same child"
        )

    # Validate transfer amount
    if transfer_data.amount_cents <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer amount must be positive"
        )

    # Check sufficient funds in source account
    if source_account.balance_cents < transfer_data.amount_cents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds. Available: {source_account.balance_cents}, Required: {transfer_data.amount_cents}"
        )

    # Create transfer transaction (debit from source)
    debit_transaction = Transaction(
        account_id=source_account.id,
        amount_cents=-transfer_data.amount_cents,  # Negative for debit
        transaction_type="transfer_out",
        idempotency_key=f"transfer_{transfer_data.idempotency_key}_debit"
    )

    # Create transfer transaction (credit to destination)
    credit_transaction = Transaction(
        account_id=dest_account.id,
        amount_cents=transfer_data.amount_cents,  # Positive for credit
        transaction_type="transfer_in",
        idempotency_key=f"transfer_{transfer_data.idempotency_key}_credit"
    )

    # Update account balances atomically
    source_account.balance_cents -= transfer_data.amount_cents
    source_account.updated_at = datetime.now(timezone.utc)

    dest_account.balance_cents += transfer_data.amount_cents
    dest_account.updated_at = datetime.now(timezone.utc)

    # Add all changes in single commit
    db.add(debit_transaction)
    db.add(credit_transaction)
    await db.commit()

    return {
        "message": "Transfer completed successfully",
        "transfer_id": f"transfer_{transfer_data.idempotency_key}",
        "amount_cents": transfer_data.amount_cents,
        "source_account_balance": source_account.balance_cents,
        "destination_account_balance": dest_account.balance_cents
    }
```

**New Schema**:
```python
# Add to schemas/transaction.py
class TransferRequest(BaseModel):
    source_account_id: int = Field(..., description="ID of source account (checking)")
    destination_account_id: int = Field(..., description="ID of destination account (savings)")
    amount_cents: int = Field(..., gt=0, description="Amount to transfer in cents")
    idempotency_key: str = Field(..., description="Unique key to prevent duplicate transfers")
```

**Frontend Updates**:
- Add transfer screen with source/destination account selection
- Display current balances for both accounts
- Show transfer validation errors
- Add transfer confirmation with PIN verification

**Testing Requirements**:
- Unit tests for transfer validation logic
- Integration tests for successful transfers
- Tests for insufficient funds scenarios
- Tests for invalid account combinations
- Concurrent transfer tests

**Implementation Priority**: Critical
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

## Version 0.3 Roadmap - Multi-Currency & Multi-Language Support

### Overview
Version 0.3 focuses on expanding the app's global reach by supporting multiple currencies and languages, while also enhancing the educational value with advanced financial literacy features.

### Core Features (Priority 1)

#### 1. Multi-Currency Support
**Goal**: Enable parents and children to manage accounts in their local currency, with support for currency conversion and exchange rates.

**User Stories:**
- As a parent, I can select my preferred currency when setting up the app
- As a parent, I can view account balances in my local currency
- As a parent, I can set allowance amounts in my local currency
- As a parent, I can see real-time exchange rates for educational purposes
- As a child, I can learn about different currencies and their values

**Data Models:**
```sql
-- Currency support
currencies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) NOT NULL UNIQUE, -- ISO 4217 currency code
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(5) NOT NULL,
    decimal_places INTEGER DEFAULT 2,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Exchange rates (historical tracking)
exchange_rates (
    id SERIAL PRIMARY KEY,
    from_currency_id INTEGER REFERENCES currencies(id),
    to_currency_id INTEGER REFERENCES currencies(id),
    rate DECIMAL(20, 8) NOT NULL,
    effective_date DATE NOT NULL,
    source VARCHAR(50) NOT NULL, -- API source
    created_at TIMESTAMP DEFAULT NOW()
);

-- Enhanced accounts with currency
ALTER TABLE accounts ADD COLUMN currency_id INTEGER REFERENCES currencies(id);
ALTER TABLE accounts ADD COLUMN display_currency_id INTEGER REFERENCES currencies(id);

-- Enhanced transactions with currency
ALTER TABLE transactions ADD COLUMN currency_id INTEGER REFERENCES currencies(id);
ALTER TABLE transactions ADD COLUMN exchange_rate_at_time DECIMAL(20, 8);
```

**API Endpoints:**
```python
# Currency management
GET /currencies
GET /currencies/{currency_id}
GET /currencies/{currency_id}/exchange-rates

# Exchange rate management
GET /exchange-rates/{from_currency}/{to_currency}
GET /exchange-rates/{from_currency}/{to_currency}/history

# Enhanced account endpoints
POST /accounts (now includes currency selection)
PUT /accounts/{account_id}/currency
GET /accounts/{account_id}/balance-in-currency/{currency_code}

# Enhanced transaction endpoints
GET /transactions (now includes currency conversion)
POST /transactions (now supports multi-currency)
```

**Frontend Screens:**
- Currency Selection Screen (parent)
- Multi-Currency Dashboard (parent/child)
- Exchange Rate Learning Screen (child)
- Currency Converter Tool (parent/child)

**Implementation Priority**: High
**Effort Estimate**: 4-5 weeks

#### 2. Multi-Language Support (i18n)
**Goal**: Provide the app in multiple languages to serve diverse global audiences and enhance accessibility.

**User Stories:**
- As a user, I can select my preferred language when first using the app
- As a user, I can change the app language at any time
- As a user, I can see all text, numbers, and dates in my preferred language
- As a user, I can access the app in my native language for better understanding

**Technical Implementation:**
```typescript
// Frontend i18n structure
locales/
├── en/
│   ├── common.json
│   ├── auth.json
│   ├── dashboard.json
│   ├── accounts.json
│   ├── chores.json
│   └── allowances.json
├── es/
│   ├── common.json
│   ├── auth.json
│   └── ...
├── fr/
├── de/
├── ja/
├── zh/
└── ar/
```

**Supported Languages (Phase 1):**
- English (en) - Default
- Spanish (es) - Latin America & Spain
- French (fr) - France & Canada
- German (de) - Germany, Austria, Switzerland
- Japanese (ja) - Japan
- Chinese Simplified (zh-CN) - China
- Arabic (ar) - Middle East & North Africa

**API Endpoints:**
```python
# Language support
GET /languages
GET /languages/{language_code}
POST /users/{user_id}/preferred-language
GET /translations/{language_code}/{namespace}
```

**Frontend Features:**
- Language selector in settings
- Automatic language detection based on device
- RTL (Right-to-Left) support for Arabic
- Localized number and date formatting
- Localized currency display

**Implementation Priority**: High
**Effort Estimate**: 3-4 weeks

#### 4. Dark Mode & Theme Support
**Goal**: Implement comprehensive dark mode and theme customization to enhance user experience and accessibility.

**User Stories:**
- As a user, I can toggle between light and dark mode for better viewing comfort
- As a user, I can have the app automatically follow my system theme preference
- As a user, I can customize accent colors and theme elements
- As a user, I can have different themes for different times of day (auto-switching)

**Technical Implementation:**
```typescript
// Theme configuration structure
themes/
├── light/
│   ├── colors.json
│   ├── typography.json
│   └── spacing.json
├── dark/
│   ├── colors.json
│   ├── typography.json
│   └── spacing.json
└── custom/
    ├── colors.json
    ├── typography.json
    └── spacing.json

// Theme context and hooks
interface ThemeContextType {
  theme: 'light' | 'dark' | 'auto';
  isDark: boolean;
  colors: ThemeColors;
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
}

// Theme-aware components
const ThemedButton = styled.button<{ variant: 'primary' | 'secondary' }>`
  background-color: ${props =>
    props.variant === 'primary'
      ? props.theme.colors.primary
      : props.theme.colors.secondary
  };
  color: ${props => props.theme.colors.onPrimary};
  border: 2px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.spacing.borderRadius};
  padding: ${props => props.theme.spacing.buttonPadding};
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px ${props => props.theme.colors.shadow};
  }
`;
```

**Theme Features**:
- **Automatic Theme Detection**: Follows system preference (light/dark)
- **Manual Theme Selection**: User can override system preference
- **Scheduled Theme Switching**: Auto-switch based on time of day
- **Custom Color Schemes**: Personalized accent colors
- **Accessibility**: High contrast modes and color-blind friendly options

**Data Models**:
```sql
-- User theme preferences
user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    theme_mode VARCHAR(20) DEFAULT 'auto', -- light, dark, auto
    accent_color VARCHAR(7) DEFAULT '#007AFF', -- hex color
    auto_switch_enabled BOOLEAN DEFAULT true,
    light_start_time TIME DEFAULT '06:00:00',
    dark_start_time TIME DEFAULT '18:00:00',
    high_contrast BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints**:
```python
# Theme management
GET /users/{user_id}/theme-preferences
PUT /users/{user_id}/theme-preferences
POST /users/{user_id}/theme-preferences/reset
GET /themes/available
GET /themes/{theme_name}/colors
```

**Frontend Components**:
- Theme toggle switch in settings
- Color picker for accent colors
- Theme preview cards
- Auto-switch time picker
- High contrast mode toggle

**Implementation Priority**: Medium
**Effort Estimate**: 2-3 weeks

#### 3. Advanced Financial Literacy Features
**Goal**: Enhance the educational value with advanced financial concepts and interactive learning tools.

**User Stories:**
- As a child, I can learn about compound interest through interactive simulations
- As a child, I can practice budgeting with virtual scenarios
- As a parent, I can set financial goals and track progress
- As a child, I can earn badges for financial literacy achievements

**Data Models:**
```sql
-- Financial goals
financial_goals (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES children(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    target_amount_cents INTEGER NOT NULL,
    current_amount_cents INTEGER DEFAULT 0,
    target_date DATE,
    goal_type VARCHAR(20) DEFAULT 'savings', -- savings, spending, charity
    status VARCHAR(20) DEFAULT 'active', -- active, completed, cancelled
    created_at TIMESTAMP DEFAULT NOW()
);

-- Learning achievements
achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL, -- savings, budgeting, chores, etc.
    points INTEGER DEFAULT 0,
    icon_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- User achievements
user_achievements (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES children(id),
    achievement_id INTEGER REFERENCES achievements(id),
    earned_at TIMESTAMP DEFAULT NOW(),
    points_earned INTEGER NOT NULL
);

-- Interactive learning sessions
learning_sessions (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES children(id),
    session_type VARCHAR(50) NOT NULL, -- compound_interest, budgeting, etc.
    completed_at TIMESTAMP DEFAULT NOW(),
    score INTEGER,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints:**
```python
# Financial goals
POST /children/{child_id}/financial-goals
GET /children/{child_id}/financial-goals
PUT /financial-goals/{goal_id}
DELETE /financial-goals/{goal_id}
POST /financial-goals/{goal_id}/update-progress

# Achievements
GET /achievements
GET /children/{child_id}/achievements
POST /children/{child_id}/achievements/{achievement_id}/earn

# Learning sessions
POST /children/{child_id}/learning-sessions
GET /children/{child_id}/learning-sessions
GET /children/{child_id}/learning-progress
```

**Frontend Screens:**
- Financial Goals Dashboard (child)
- Interactive Learning Center (child)
- Achievement Gallery (child)
- Progress Tracking (parent/child)
- Educational Games (child)

**Implementation Priority**: Medium
**Effort Estimate**: 4-5 weeks

### Technical Improvements (Priority 2)

#### 1. Performance Optimization
- Implement Redis caching for exchange rates
- Add CDN for static assets
- Optimize database queries for multi-currency operations
- Implement lazy loading for translations

#### 2. Security Enhancements
- Add rate limiting for exchange rate API calls
- Implement currency validation and sanitization
- Add audit logging for currency operations
- Enhanced PIN security with biometric options

#### 3. Monitoring and Analytics
- Multi-currency transaction monitoring
- Language usage analytics
- Performance metrics for different locales
- User engagement tracking by region

### Infrastructure Requirements

#### 1. Exchange Rate Services
- Integration with currency exchange APIs (Fixer.io, ExchangeRate-API)
- Real-time rate updates (every 15 minutes)
- Historical rate data storage
- Fallback rate sources for reliability

#### 2. Localization Infrastructure
- Translation management system
- Automated language detection
- RTL layout support
- Localized content delivery

#### 3. Global Deployment
- Multi-region database deployment
- CDN with edge locations
- Localized hosting options
- Compliance with regional data laws

### Implementation Phases

#### Phase 1: Multi-Currency Foundation (Weeks 1-5)
1. Implement currency data models and APIs
2. Integrate exchange rate services
3. Update account and transaction systems
4. Add currency conversion logic

#### Phase 2: Multi-Language Support (Weeks 6-9)
1. Implement i18n infrastructure
2. Create translation files for 7 languages
3. Add RTL support for Arabic
4. Update frontend for localization

#### Phase 3: Financial Literacy Features (Weeks 10-13)
1. Implement financial goals system
2. Create achievement system
3. Build interactive learning tools
4. Add progress tracking

#### Phase 4: Testing & Optimization (Weeks 14-15)
1. Multi-currency testing
2. Localization testing
3. Performance optimization
4. Security review

### Success Criteria for Version 0.3
- Support for at least 7 major currencies with real-time exchange rates
- Full localization in 7 languages with RTL support
- Interactive financial literacy features with achievement system
- Performance maintained across all locales
- 99.9% uptime for exchange rate services
- Successful deployment in multiple regions
- Positive user feedback from diverse language groups

### Future Considerations (Version 0.4+)
- Cryptocurrency support for educational purposes
- Advanced analytics and reporting
- Social features and family sharing
- Integration with educational institutions
- AI-powered financial advice and recommendations

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
