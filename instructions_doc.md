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
10. [Troubleshooting](#troubleshooting)

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
