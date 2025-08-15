# My First Bank App

A cross-platform mobile application for parents to manage virtual bank accounts for their children. Built with React Native (frontend) and FastAPI (backend).

## 🎯 Project Overview

**My First Bank App** allows parents to:
- Create and manage child profiles
- Set up virtual checking and savings accounts
- Make virtual money deposits with idempotency support
- Track account balances and transaction history
- View detailed financial insights

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Native  │    │     FastAPI     │    │   PostgreSQL    │
│    Frontend     │◄──►│     Backend     │◄──►│    Database     │
│   (Mobile App)  │    │   (Python)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Features

### Core Functionality
- **Parent Authentication**: Secure JWT-based login/registration
- **Child Management**: Create and manage child profiles
- **Virtual Accounts**: Automatic checking and savings account creation
- **Deposits**: Virtual money deposits with validation
- **Transaction History**: Cursor-based pagination for transactions
- **ACID Compliance**: Database transactions ensure data consistency

### Technical Features
- **Idempotency**: Prevents duplicate transactions
- **Currency Handling**: Stores amounts in cents (no floating-point errors)
- **Access Control**: Parents can only access their children's accounts
- **Input Validation**: Comprehensive form validation with meaningful errors
- **Responsive Design**: Modern, intuitive mobile interface

## 🛠️ Tech Stack

### Frontend
- **React Native** with Expo
- **TypeScript** for type safety
- **React Navigation** for routing
- **React Hook Form** with Yup validation
- **React Native Paper** for UI components

### Backend
- **FastAPI** for high-performance API
- **SQLAlchemy** with async support
- **PostgreSQL** for data persistence
- **Alembic** for database migrations
- **JWT** for authentication

### Infrastructure
- **Docker** for containerization
- **Docker Compose** for local development
- **PostgreSQL 15** for database

## 📋 Prerequisites

- **Docker** and **Docker Compose**
- **Python 3.11+** (for local backend development)
- **Node.js 16+** (for local frontend development)
- **Expo CLI** (`npm install -g @expo/cli`)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd my-first-bank-app
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **Frontend**: Expo development server will start automatically

### Option 2: Local Development

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
docker-compose up -d postgres
alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📱 Mobile App Usage

1. **Install Expo Go** on your mobile device
2. **Scan the QR code** from the Expo development server
3. **Register** a new parent account
4. **Create child profiles** and start managing virtual accounts

## 🔧 Configuration

### Environment Variables

Create `.env` files in both `backend/` and `frontend/` directories:

#### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/bankapp
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
```

#### Frontend (.env)
```env
API_BASE_URL=http://localhost:8000/api/v1
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
npm run type-check
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Parent registration
- `POST /api/v1/auth/login` - Parent login

### Children
- `POST /api/v1/children/` - Create child profile
- `GET /api/v1/children/` - List children

### Accounts
- `POST /api/v1/accounts/{id}/deposit` - Make deposit
- `GET /api/v1/accounts/{id}/transactions` - Get transaction history

## 🗄️ Database Schema

The application uses four main tables:
- **users**: Parent accounts
- **children**: Child profiles
- **accounts**: Virtual bank accounts (checking/savings)
- **transactions**: Deposit records with idempotency keys

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Access Control**: Parents can only access their children's data
- **Input Validation**: Comprehensive validation on all inputs
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection attacks

## 📈 Performance Features

- **Async Operations**: FastAPI async endpoints for better performance
- **Cursor Pagination**: Efficient transaction history loading
- **Database Indexing**: Optimized queries with proper indexing
- **Connection Pooling**: Efficient database connection management

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Update all sensitive configuration
2. **Database**: Use production PostgreSQL instance
3. **Security**: Change default JWT secret key
4. **Monitoring**: Add logging and health checks
5. **SSL**: Enable HTTPS for production

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 Development Guidelines

- **Code Style**: Follow existing patterns and conventions
- **TypeScript**: Use strict typing for all new code
- **Testing**: Maintain good test coverage
- **Documentation**: Update docs for new features
- **Commits**: Use conventional commit messages

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running and accessible
2. **Port Conflicts**: Check if ports 8000, 5432 are available
3. **Dependencies**: Clear node_modules and reinstall if needed
4. **Docker Issues**: Restart Docker service if containers fail

### Getting Help

- Check the logs: `docker-compose logs <service-name>`
- Verify environment variables are set correctly
- Ensure all prerequisites are installed
- Check the API documentation at `/docs`

## 📄 License

This project is part of the My First Bank App MVP.

## 🙏 Acknowledgments

- FastAPI for the excellent Python web framework
- React Native team for the mobile development platform
- Expo for simplifying React Native development
- PostgreSQL for the reliable database system

---

**Happy coding! 🎉**
