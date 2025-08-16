# My First Bank App - Development Instructions

## Overview
This document provides comprehensive instructions for setting up, developing, testing, and deploying the My First Bank App. The application consists of a FastAPI backend with PostgreSQL database and a React Native frontend with Expo.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [Testing](#testing)
6. [Database Management](#database-management)
7. [Docker Development](#docker-development)
8. [Deployment](#deployment)
9. [Code Quality & Linting](#code-quality--linting)
10. [Pre-Commit Checklist for CI/CD Success](#-pre-commit-checklist-for-cicd-success)
11. [Troubleshooting](#troubleshooting)
12. [MVP Version 0.2 Roadmap](#mvp-version-02-roadmap)

## Prerequisites

### System Requirements
- **Operating System**: Linux (WSL2), macOS, or Windows
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Node.js**: Version 18 or higher
- **Python**: Version 3.11 or higher
- **Git**: Latest version

### Required Software
- Docker Desktop
- VS Code or preferred IDE
- PostgreSQL client (optional, for direct database access)

## Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/erickuiper/my-first-bank-app.git
cd my-first-bank-app
```

### 2. Environment Variables
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

### 3. Start the Environment
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 3000

## Backend Development

### Project Structure
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
└── Dockerfile
```

### Setup Backend Development Environment
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Key Dependencies
- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Token authentication
- **Passlib**: Password hashing library

### Running the Backend
```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints
- **Authentication**: `/api/v1/auth/register`, `/api/v1/auth/login`
- **Children**: `/api/v1/children/` (GET, POST)
- **Accounts**: `/api/v1/accounts/{id}/deposit`, `/api/v1/accounts/{id}/transactions`

## Frontend Development

### Project Structure
```
frontend/
├── src/
│   ├── screens/
│   │   ├── LoginScreen.web.tsx
│   │   ├── RegisterScreen.web.tsx
│   │   └── DashboardScreen.web.tsx
│   ├── components/
│   ├── navigation/
│   └── utils/
├── tests/
│   └── e2e/
├── package.json
└── Dockerfile
```

### Setup Frontend Development Environment
```bash
cd frontend
npm install
```

### Key Dependencies
- **React Native**: Mobile app framework
- **Expo**: Development platform for React Native
- **React Router DOM**: Web routing
- **React Native Paper**: Material Design components
- **Playwright**: End-to-end testing

### Running the Frontend
```bash
# Development mode
npm start

# Build for production
npm run build

# Run tests
npm run test:e2e
```

## Testing

### Backend Testing
```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_register_user -v
```

### Frontend Testing
```bash
cd frontend

# Run Playwright tests
npm run test:e2e

# Run specific test file
npx playwright test tests/e2e/auth.spec.ts

# Run tests in headed mode
npx playwright test --headed
```

### Test Coverage Goals
- **Backend**: Minimum 80% code coverage
- **Frontend**: All critical user flows covered by E2E tests

## Database Management

### Database Schema
The application uses PostgreSQL with the following main tables:
- **users**: User authentication and profile information
- **children**: Child accounts managed by parents
- **accounts**: Financial accounts (checking/savings) for children
- **transactions**: Financial transactions with idempotency support

### Running Migrations
```bash
cd backend
source .venv/bin/activate

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# Check current migration status
alembic current
```

### Database Connection
```bash
# Connect to PostgreSQL container
docker-compose exec postgres psql -U postgres -d bankapp

# View tables
\dt

# View data
SELECT * FROM users;
```

## Docker Development

### Container Management
```bash
# Start all services
docker-compose up -d

# View running containers
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Stop services
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Restart specific service
docker-compose restart backend
```

### Development Workflow
1. **Code Changes**: Make changes to source code
2. **Container Rebuild**: `docker-compose build --no-cache <service>`
3. **Service Restart**: `docker-compose restart <service>`
4. **Test Changes**: Run tests to verify functionality

## Deployment

### Production Deployment
1. **Environment Setup**: Configure production environment variables
2. **Database Migration**: Run `alembic upgrade head`
3. **Container Deployment**: Deploy using Docker Compose or Kubernetes
4. **Health Checks**: Verify all services are running correctly

### Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates configured
- [ ] Monitoring and logging set up
- [ ] Backup strategy implemented
- [ ] Security audit completed

## Code Quality & Linting

### Backend Code Quality Tools

#### Black (Code Formatter)
**Purpose**: Enforces consistent Python code formatting
**Installation**: `pip install black`
**Usage**:
```bash
# Format all files
black .

# Check formatting without changing files
black --check .

# Format specific file
black app/main.py

# Show differences
black --diff .
```

**Configuration**: Black uses sensible defaults, but you can configure line length:
```bash
# Set line length to 88 characters (default)
black --line-length 88 .

# Set line length to 100 characters
black --line-length 100 .
```

#### isort (Import Sorter)
**Purpose**: Automatically sorts and organizes Python imports
**Installation**: `pip install isort`
**Usage**:
```bash
# Sort imports in all files
isort .

# Check import sorting without changing files
isort --check-only .

# Sort imports in specific file
isort app/main.py

# Show differences
isort --diff .
```

**Configuration**: Create `pyproject.toml` for custom settings:
```toml
[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
```

#### Flake8 (Linter)
**Purpose**: Checks Python code for style and potential errors
**Installation**: `pip install flake8`
**Usage**:
```bash
# Lint all files
flake8 .

# Lint specific file
flake8 app/main.py

# Show error codes
flake8 --show-source .

# Ignore specific errors
flake8 --extend-ignore E203,W503 .
```

**Configuration**: Create `.flake8` file:
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,.venv
```

#### MyPy (Type Checker)
**Purpose**: Static type checking for Python code
**Installation**: `pip install mypy`
**Usage**:
```bash
# Type check all files
mypy .

# Type check specific file
mypy app/main.py

# Ignore missing imports
mypy --ignore-missing-imports .

# Show error details
mypy --show-error-codes .
```

**Configuration**: Create `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Frontend Code Quality Tools

#### ESLint
**Purpose**: JavaScript/TypeScript linting and code quality
**Installation**: `npm install -g eslint`
**Usage**:
```bash
# Lint all files
npm run lint

# Lint specific file
npx eslint src/components/Button.tsx

# Auto-fix issues
npx eslint --fix src/
```

#### Prettier
**Purpose**: Code formatting for JavaScript/TypeScript
**Installation**: `npm install -g prettier`
**Usage**:
```bash
# Format all files
npx prettier --write .

# Check formatting
npx prettier --check .

# Format specific file
npx prettier --write src/components/Button.tsx
```

### Running All Quality Checks
```bash
cd backend
source .venv/bin/activate

# Run all quality checks
echo "🔍 Running black..."
black --check --diff .
echo "🔍 Running isort..."
isort --check-only --diff .
echo "🔍 Running flake8..."
flake8 . --max-line-length=88 --extend-ignore=E203,W503
echo "🔍 Running mypy..."
mypy . --ignore-missing-imports
```

### Pre-commit Hooks
Set up pre-commit hooks to automatically run quality checks:
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run all hooks
pre-commit run --all-files
```

### GitHub Actions Integration
The project includes GitHub Actions workflows that automatically run:
- **Backend**: Black, isort, flake8, mypy, pytest
- **Frontend**: ESLint, TypeScript check, Playwright tests
- **Integration**: Docker Compose health checks



## Cursor Background Jobs Workflow

### Overview
Cursor is a powerful tool for managing background jobs and workflows.

### Key Features
- **Job Management**: Monitor and manage long-running tasks.
- **Workflow Automation**: Define complex workflows for repetitive tasks.
- **Error Handling**: Automatically retry failed jobs and notify team members.

### Setup
1. **Install Cursor**:
   - Visit [Cursor](https://cursor.sh)
   - Download and install the Cursor application.

2. **Configure Cursor**:
   - Open Cursor.
   - Go to "Settings" > "Integrations".
   - Click "Add Integration".
   - Select "GitHub" or "Other" (if using a different platform).
   - Copy the API token.

3. **Create a Workflow**:
   - In Cursor, create a new workflow.
   - Name it "My First Bank App Deployment".
   - Add a trigger (e.g., "New Issue Created" from external system).
   - Add an action (e.g., "Deploy to Production" using Docker Compose).

### Example Workflow
1. **New Issue Created**:
   - When a new issue is created, it triggers the Cursor workflow.
   - The workflow automatically deploys the application to production.

### Benefits
- **Reliability**: Ensures consistent deployments and updates.
- **Scalability**: Easily manage multiple background jobs.
- **Error Prevention**: Automatically retries failed deployments.
- **System Updates**: Monitor automatic issue creation and updates
- **CI/CD Integration**: Track pipeline status and automated reporting

## Troubleshooting

### Common Issues

#### Backend Issues
1. **Database Connection Errors**
   - Verify PostgreSQL container is running: `docker-compose ps`
   - Check database logs: `docker-compose logs postgres`
   - Ensure environment variables are correct

2. **Import Errors**
   - Verify virtual environment is activated
   - Check all dependencies are installed: `pip list`
   - Run `pip install -r requirements.txt`

3. **Migration Errors**
   - Check database connection
   - Verify migration files are in correct location
   - Run `alembic current` to check migration status

#### Frontend Issues
1. **Build Failures**
   - Clear node modules: `rm -rf node_modules package-lock.json`
   - Reinstall dependencies: `npm install`
   - Check Node.js version compatibility

2. **Playwright Test Failures**
   - Install browsers: `npx playwright install`
   - Check system dependencies for Linux
   - Verify frontend is running on expected port

#### Docker Issues
1. **Container Won't Start**
   - Check port conflicts: `netstat -tulpn | grep :8000`
   - Verify Docker daemon is running
   - Check container logs: `docker-compose logs <service>`

2. **Build Failures**
   - Clear Docker cache: `docker system prune -a`
   - Rebuild without cache: `docker-compose build --no-cache`
   - Check Dockerfile syntax

### Performance Optimization
1. **Database Queries**
   - Use database indexes for frequently queried fields
   - Implement query pagination for large datasets
   - Monitor slow query performance

2. **API Response Times**
   - Implement caching strategies
   - Use async operations where possible
   - Monitor endpoint performance

3. **Frontend Loading**
   - Implement code splitting
   - Use lazy loading for components
   - Optimize bundle size

### Security Considerations
1. **Authentication**
   - Use strong JWT secrets
   - Implement token expiration
   - Validate user permissions

2. **Data Protection**
   - Encrypt sensitive data
   - Implement rate limiting
   - Use HTTPS in production

3. **Input Validation**
   - Validate all user inputs
   - Use Pydantic schemas for data validation
   - Implement SQL injection protection

## MVP Version 0.2 Roadmap

### 🎯 **Overview**
MVP version 0.2 will focus on enhancing the core banking functionality, improving user experience, and adding essential features for a production-ready application.

### 🚀 **Core Banking Features**

#### 1. **Account Management**
- **Multiple Account Types**: Support for checking, savings, and investment accounts
- **Account Transfers**: Internal transfers between user accounts
- **Account Limits**: Configurable daily/monthly transaction limits
- **Account Statements**: Monthly statements and transaction history export
- **Chore-Based Allowance System**: Weekly allowance with chore completion tracking
- **Recurring Bill Rules**: Automated bill creation and categorization

#### 2. **Enhanced Transaction System**
- **Transaction Categories**: Categorize transactions (food, entertainment, bills, etc.)
- **Recurring Transactions**: Set up automatic recurring payments
- **Transaction Search**: Advanced search and filtering capabilities
- **Transaction Notes**: Add notes and tags to transactions

#### 3. **Learning Tools**
- **Savings Goals**: Set simple savings targets with progress tracking
- **Spending Tracking**: Basic categorization of transactions for learning
- **Money Lessons**: Simple tips and explanations about money concepts

### 🔐 **Security & Compliance**

#### 1. **Basic Security**
- **Simple Authentication**: Username/password with basic validation
- **Parent Controls**: Parent approval for important actions
- **Safe Environment**: No real money, just learning

#### 2. **Child Safety**
- **Age-Appropriate Content**: Simple language and concepts
- **Parent Oversight**: Parents can monitor and guide children
- **Educational Focus**: Learning about money, not financial planning

### 📱 **User Experience Improvements**

#### 1. **Mobile-First Design**
- **Responsive Dashboard**: Optimized for all screen sizes
- **Dark Mode**: Light/dark theme toggle
- **Accessibility**: WCAG 2.1 AA compliance
- **Offline Support**: Basic functionality when offline

#### 2. **Enhanced UI/UX**
- **Customizable Dashboard**: Drag-and-drop widget arrangement
- **Quick Actions**: Frequently used actions accessible from main screen
- **Notifications**: Push notifications for important events
- **Multi-language Support**: Internationalization (i18n)

### 🔧 **Technical Improvements**

#### 1. **Simple Performance**
- **Basic Database**: Simple queries and basic indexing
- **Simple Background Jobs**: Weekly allowance calculations and chore tracking
- **Chore Tracking System**: Monitor chore completion and calculate penalties
- **Scheduled Pay Runs**: Automated weekly allowance calculations and deposits

#### 2. **Basic Monitoring**
- **Simple Health Checks**: Basic service health monitoring
- **Error Logging**: Simple error tracking for debugging
- **Basic Testing**: Simple functionality testing

### 📊 **Simple Learning Tools**

#### 1. **Child Learning**
- **Progress Tracking**: Simple progress on savings goals
- **Basic Charts**: Simple visual representation of money
- **Learning Tips**: Age-appropriate money lessons

#### 2. **Parent Dashboard**
- **Simple Overview**: Basic view of children's accounts
- **Chore Tracking**: Monitor chore completion
- **Allowance Management**: Set up and adjust allowances

### 🔌 **Integration & APIs**

#### 1. **Simple Integrations**
- **Educational Content**: Age-appropriate money learning resources
- **Simple Notifications**: Basic reminders for chores and allowances

#### 2. **Simple Developer Experience**
- **Basic API Docs**: Simple endpoint documentation
- **Easy Testing**: Simple test setup and examples

### 🧪 **Testing & Quality Assurance**

#### 1. **Simple Testing**
- **Basic Coverage**: Simple test coverage for core features
- **Frontend Testing**: Basic component and user flow tests
- **End-to-End Testing**: Simple user journey testing

#### 2. **Simple Quality Checks**
- **Basic Code Quality**: Simple linting and formatting
- **Simple Testing**: Basic automated tests
- **Dependency Updates**: Keep dependencies up to date

### 📋 **Implementation Phases**

#### **Phase 1: Core Enhancements (Weeks 1-4)**
- **Chore-Based Allowance System** (Priority 1)
  - Weekly allowance rules and chore definitions
  - Automated pay calculations and deposits
  - Chore completion tracking and penalty system
- **Recurring Bill Rules** (Priority 2)
  - Automated bill creation and categorization
  - Monthly bill scheduling and savings allocation
- **In-Memory Database Testing** (Priority 3)
  - SQLite in-memory database for CI/CD tests
  - TestClient integration tests for API endpoints
  - Remove CI/CD skip conditions
- Account management improvements
- Enhanced transaction system
- Basic security enhancements

#### **Phase 2: User Experience (Weeks 5-8)**
- UI/UX improvements
- Mobile optimization
- Basic analytics

#### **Phase 3: Learning Features (Weeks 9-12)**
- Simple savings goals and progress tracking
- Basic money lessons and tips
- Simple charts and visualizations
- **Test Infrastructure Enhancement**
  - Complete in-memory database test coverage
  - Performance testing and load testing
  - Test coverage reporting and monitoring

#### **Phase 4: Polish & Deploy (Weeks 13-16)**
- Android app development and testing
- Heroku deployment and CI/CD
- Final testing and documentation

### 🎯 **Success Metrics**

#### **Learning Metrics**
- **Chore Completion**: 80%+ chore completion rate
- **Savings Progress**: Children meeting 70%+ of savings goals
- **User Engagement**: Children using app 3+ times per week
- **Parent Satisfaction**: 4.0/5 stars from parents

#### **Technical Metrics**
- **Test Coverage**: 90%+ backend coverage with in-memory database
- **CI/CD Success**: All tests pass in pipeline without skips
- **Performance**: App responds within 2 seconds
- **Reliability**: App works without crashes

### 📚 **Resources & Dependencies**

#### **Required Skills**
- Basic React Native development
- Simple database design
- Basic security for children's app
- Simple API design

#### **External Dependencies**
- Educational content resources
- Simple notification services
- Basic hosting (Heroku)

### 🚀 **MVP 0.2 Implementation Details**

#### **1. Deployment & Infrastructure**
- **Backend Deployment**: Deploy to Heroku using GitHub Actions CI/CD
- **Android App**: Create native Android app for frontend testing on physical devices
- **Database**: PostgreSQL with new models for chores, allowances, and bill rules

#### **2. Core Feature Implementation**

##### **A. Chore-Based Allowance System (Priority 1)**
**User Stories:**
- As a parent, I can define a weekly allowance rule for a child (base_amount_cents, frequency=weekly)
- As a parent, I can define chores with expected completion per pay period and penalties (penalty_cents per missed chore)
- On each scheduled pay run, the system calculates earned_allowance = base_amount - penalty * missed_chores, creates transactions, and deposits the earned amount into the designated account (checking by default)

**Data Models:**
```sql
-- Allowance rules
CREATE TABLE allowance_rules (
    id UUID PRIMARY KEY,
    child_id UUID REFERENCES children(id),
    base_amount_cents INTEGER NOT NULL,
    frequency VARCHAR(20) DEFAULT 'weekly',
    penalty_per_chore_cents INTEGER DEFAULT 25,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chore definitions
CREATE TABLE chores (
    id UUID PRIMARY KEY,
    child_id UUID REFERENCES children(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    expected_completions_per_period INTEGER DEFAULT 1,
    penalty_cents INTEGER DEFAULT 25,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chore completions
CREATE TABLE chore_completions (
    id UUID PRIMARY KEY,
    chore_id UUID REFERENCES chores(id),
    child_id UUID REFERENCES children(id),
    completed_at TIMESTAMP DEFAULT NOW(),
    verified_by_parent BOOLEAN DEFAULT false,
    notes TEXT
);
```

**API Endpoints:**
```python
# Allowance management
POST /api/v1/allowances/ - Create allowance rule
GET /api/v1/allowances/{child_id} - Get child's allowance rules
PUT /api/v1/allowances/{id} - Update allowance rule

# Chore management
POST /api/v1/chores/ - Create chore
GET /api/v1/chores/{child_id} - Get child's chores
PUT /api/v1/chores/{id} - Update chore
POST /api/v1/chores/{id}/complete - Mark chore as completed

# Pay runs
POST /api/v1/pay-runs/ - Trigger manual pay run
GET /api/v1/pay-runs/{child_id} - Get pay run history
```

##### **B. Recurring Bill Rules (Priority 2)**
**User Stories:**
- As a parent, I can define recurring bill rules (amount_cents, description, due_date rule e.g., last day of month) that create scheduled transactions which move money to savings (or just tag transactions as bills)

**Data Models:**
```sql
-- Bill rules
CREATE TABLE bill_rules (
    id UUID PRIMARY KEY,
    child_id UUID REFERENCES children(id),
    name VARCHAR(100) NOT NULL,
    amount_cents INTEGER NOT NULL,
    description TEXT,
    due_date_rule VARCHAR(50) NOT NULL, -- 'last_day_of_month', 'weekly', 'monthly'
    category VARCHAR(50) DEFAULT 'bills',
    target_account_id UUID REFERENCES accounts(id), -- Usually savings
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Scheduled bills
CREATE TABLE scheduled_bills (
    id UUID PRIMARY KEY,
    bill_rule_id UUID REFERENCES bill_rules(id),
    child_id UUID REFERENCES children(id),
    amount_cents INTEGER NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, overdue
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### **3. Simple Background Jobs**
- **Weekly Pay Runs**: Calculate allowances, apply penalties, create transactions
- **Monthly Bill Processing**: Generate scheduled bills, move money to savings
- **Simple Reminders**: Basic notifications for chores and allowances

#### **4. Simple Frontend Screens**
- **Chore Dashboard**: View, complete, and track chores
- **Allowance Management**: Set up and modify allowance rules
- **Bill Rules**: Configure recurring bills and categories
- **Simple History**: Basic view of past payments
- **Parent Dashboard**: Simple overview of children's accounts

#### **5. Comprehensive Testing Strategy**
- **Unit Tests**: Business logic testing with in-memory database
- **Integration Tests**: API endpoint testing with TestClient
- **E2E Tests**: Full user journeys for core features
- **Mobile Testing**: Android app functionality on physical devices
- **CI/CD Tests**: In-memory database tests for pipeline validation

#### **6. Implementation Priority & Effort Estimates**
1. **Chore-Based Allowance System** (2-3 weeks)
   - Database models and migrations
   - Core business logic
   - Basic API endpoints
   - Frontend chore management

2. **Recurring Bill Rules** (1-2 weeks)
   - Bill rule models and scheduling
   - Automated bill creation
   - Frontend bill management

3. **In-Memory Database Testing** (1-2 weeks)
   - SQLite in-memory database configuration
   - TestClient integration test conversion
   - Remove CI/CD skip conditions
   - Ensure 90%+ test coverage

4. **Background Jobs & Scheduler** (1-2 weeks)
   - Pay run automation
   - Bill processing
   - Scheduled task management

5. **Android App & Deployment** (2-3 weeks)
   - React Native Android build
   - Heroku deployment
   - CI/CD pipeline updates

**Total Estimated Effort: 7-12 weeks**

#### **7. In-Memory Database Testing Implementation**

##### **A. SQLite In-Memory Database Setup**
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create test client with database session override"""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

##### **B. TestClient Integration Tests**
```python
# test_api_integration.py
import pytest
from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    """Test user registration using TestClient"""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_create_child_with_auth(client: TestClient):
    """Test creating a child with authentication"""
    # First register and login
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "parent@example.com", "password": "password123"}
    )
    token = register_response.json()["access_token"]

    # Create child with token
    response = client.post(
        "/api/v1/children/",
        json={"name": "Test Child", "birthdate": "2015-01-01"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

##### **C. Business Logic Unit Tests**
```python
# test_business_logic.py
import pytest
from decimal import Decimal
from app.services.allowance_service import AllowanceService
from app.models.allowance_rule import AllowanceRule
from app.models.chore import Chore

def test_allowance_calculation_with_penalties():
    """Test allowance calculation with chore penalties"""
    service = AllowanceService()

    # Base allowance: $5.00
    base_amount = Decimal("500")
    # Penalty per missed chore: $0.25
    penalty_per_chore = Decimal("25")
    # Missed 2 chores
    missed_chores = 2

    earned_amount = service.calculate_earned_allowance(
        base_amount, penalty_per_chore, missed_chores
    )

    # Expected: $5.00 - ($0.25 * 2) = $4.50
    expected = Decimal("450")
    assert earned_amount == expected
```

##### **D. Benefits of In-Memory Testing**
- **Fast Execution**: No database connection overhead
- **Isolated Tests**: Each test gets a fresh database
- **CI/CD Compatible**: No external database dependencies
- **Realistic Testing**: Tests actual database operations
- **Coverage**: Can test all database interactions
- **Reliability**: No network or connection issues

##### **E. Migration from Current Tests**
1. **Phase 1**: Add in-memory database configuration
2. **Phase 2**: Convert existing httpx tests to TestClient
3. **Phase 3**: Remove CI/CD skip conditions
4. **Phase 4**: Add comprehensive business logic tests
5. **Phase 5**: Achieve 90%+ test coverage

---

## Support and Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Native Documentation](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [Playwright Documentation](https://playwright.dev/)

### Community
- GitHub Issues: Report bugs and feature requests
- Stack Overflow: Technical questions
- Discord/Slack: Community discussions

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes following coding standards
4. Run all tests and quality checks
5. Submit a pull request

---

**Note**: This document is maintained by the development team. For questions or updates, please create an issue or contact the maintainers.

## 🚀 **Development Workflow**

### **Local Development Setup**
1. **Clone and setup**: `git clone` + `docker-compose up`
2. **Backend development**: FastAPI + SQLAlchemy + Alembic
3. **Frontend development**: React + Expo + Playwright
4. **Database management**: PostgreSQL + pgAdmin

### **Testing Strategy**
1. **Backend tests**: `pytest` with coverage
2. **Frontend tests**: Playwright E2E tests
3. **Integration tests**: API endpoint testing
4. **Database tests**: Transaction logic validation

### **CI/CD Pipeline**
1. **GitHub Actions**: Automated testing and deployment
2. **Quality gates**: Linting, type checking, test coverage
3. **Deployment**: Staging and production environments

## ✅ **Pre-Commit Checklist for CI/CD Success**

### **🔍 Pre-Commit Quality Gates**

**IMPORTANT**: Complete ALL of these steps locally before committing to avoid CI/CD failures and multiple pipeline iterations.

#### **1. Backend Code Quality (Required)**
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

#### **2. Frontend Code Quality (Required)**
```bash
cd frontend

# 1. ESLint check
npm run lint

# 2. TypeScript type check
npm run type-check

# 3. Build verification
npm run build

# 4. Playwright tests (if web server available)
npm run test:e2e
```

#### **3. Full Stack Integration (Recommended)**
```bash
# 1. Start full stack locally
docker-compose up -d

# 2. Run backend tests with database
cd backend && pytest tests/ --cov=app

# 3. Run frontend tests with backend
cd frontend && npm run test:e2e

# 4. Stop services
docker-compose down
```

### **🚨 Common CI/CD Failure Points**

#### **Backend Failures**
- **Black formatting**: Run `black . --line-length=120` locally
- **isort imports**: Run `isort . --profile=black --line-length=120` locally
- **Flake8 violations**: Fix all E, W, F errors before committing
- **MyPy errors**: Resolve all type annotation issues
- **Pytest collection**: Ensure `pythonpath = ["."]` in pyproject.toml
- **Import errors**: Check all `from app.` imports resolve correctly

#### **Frontend Failures**
- **ESLint errors**: Run `npm run lint:fix` to auto-fix issues
- **TypeScript errors**: Run `npm run type-check` to identify issues
- **Build failures**: Run `npm run build` locally first
- **Playwright failures**: Ensure web server starts correctly

#### **Integration Failures**
- **Database connection**: Check DATABASE_URL in environment
- **API endpoints**: Verify backend server is running
- **CORS issues**: Check frontend-backend communication
- **Test isolation**: Ensure tests don't interfere with each other

### **📋 Pre-Commit Workflow**

#### **Step 1: Code Changes**
1. Make your code changes
2. Save all files

#### **Step 2: Backend Quality Check**
```bash
cd backend
black . --line-length=120
isort . --profile=black --line-length=120
flake8 . --max-line-length=120
mypy . --config-file=pyproject.toml
pytest tests/ --cov=app --cov-report=term-missing
```

#### **Step 3: Frontend Quality Check**
```bash
cd frontend
npm run lint:fix
npm run type-check
npm run build
```

#### **Step 4: Integration Test (Optional but Recommended)**
```bash
# Start services
docker-compose up -d

# Run integration tests
cd backend && pytest tests/ --cov=app
cd frontend && npm run test:e2e

# Stop services
docker-compose down
```

#### **Step 5: Commit Only When All Checks Pass**
```bash
git add .
git commit -m "Descriptive commit message"
git push
```

### **🎯 Benefits of Pre-Commit Checklist**

1. **Faster CI/CD**: No more waiting for pipeline failures
2. **Higher Quality**: Catch issues before they reach the repository
3. **Developer Experience**: Immediate feedback on code quality
4. **Team Efficiency**: Reduce pipeline iterations and delays
5. **Confidence**: Know your code will pass CI/CD before pushing

### **⚠️ Emergency Override (Use Sparingly)**

If you must commit without full pre-commit checks:

1. **Document the reason** in commit message
2. **Tag with [WIP]** or [SKIP-CHECKS]
3. **Plan immediate follow-up** to fix issues
4. **Notify team** of potential CI/CD delays

**Example**: `git commit -m "[WIP] Emergency fix for production issue - will complete checks in follow-up commit"`
