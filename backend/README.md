# My First Bank App - Backend

FastAPI backend for the parent-managed virtual bank accounts application.

## Features

- **Authentication**: JWT-based parent authentication
- **Child Management**: Create and manage child profiles
- **Account Management**: Automatic checking and savings account creation
- **Deposits**: Virtual money deposits with idempotency support
- **Transaction History**: Cursor-based pagination for transactions
- **ACID Compliance**: Database transactions ensure data consistency

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy async
- **Authentication**: JWT tokens
- **Migrations**: Alembic
- **Testing**: pytest with async support

## Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 13+

### Local Development

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/bankapp
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Parent registration
- `POST /api/v1/auth/login` - Parent login

### Children
- `POST /api/v1/children/` - Create child profile
- `GET /api/v1/children/` - List children

### Accounts
- `POST /api/v1/accounts/{id}/deposit` - Make deposit
- `GET /api/v1/accounts/{id}/transactions` - Get transaction history

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

## Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

## Development

### Code Formatting

```bash
black .
isort .
```

### Linting

```bash
flake8 .
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
