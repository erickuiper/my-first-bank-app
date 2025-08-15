# Pre-Commit Hooks Setup for My First Bank App

This document explains how to set up and use pre-commit hooks to ensure code quality before every commit.

## 🎯 **What Are Pre-Commit Hooks?**

Pre-commit hooks automatically run quality checks on your code before you commit. If any check fails, the commit is blocked until you fix the issues. This prevents broken code from reaching the repository and failing CI/CD pipelines.

## 🚀 **Quick Setup**

### **Option 1: Automated Setup (Recommended)**
```bash
# Make the setup script executable and run it
chmod +x scripts/setup-pre-commit.sh
./scripts/setup-pre-commit.sh
```

### **Option 2: Manual Setup**
```bash
# 1. Install pre-commit
pip install -r requirements-pre-commit.txt

# 2. Install commitlint
npm install -g @commitlint/cli @commitlint/config-conventional

# 3. Install pre-commit hooks
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg
```

## 📋 **Available Hooks**

### **🔍 Backend Quality Checks (Python)**
- **Black**: Code formatting with 120 character line length
- **isort**: Import sorting and organization
- **Flake8**: Linting and style enforcement
- **MyPy**: Static type checking
- **Pytest**: Test collection verification
- **Bandit**: Security vulnerability scanning

### **🎨 Frontend Quality Checks (JavaScript/TypeScript)**
- **ESLint**: Code linting and style enforcement
- **TypeScript**: Type checking and validation
- **Build Verification**: Ensures the app builds successfully

### **📝 Git Quality Checks**
- **Commitlint**: Enforces conventional commit format
- **File Checks**: Trailing whitespace, merge conflicts, large files
- **YAML/JSON**: Syntax validation

### **🐳 Docker Quality Checks**
- **Hadolint**: Dockerfile best practices and security

## 🎮 **How to Use**

### **Automatic Execution**
Hooks run automatically on every commit. You don't need to do anything special!

### **Manual Execution**
```bash
# Check all files (even unstaged)
pre-commit run --all-files

# Check only staged files
pre-commit run

# Check specific hook
pre-commit run black
pre-commit run mypy
pre-commit run frontend-lint
```

### **Skip Hooks (Emergency Only)**
```bash
# Skip all hooks (use sparingly!)
git commit -m "feat: emergency fix" --no-verify

# Skip specific hook
SKIP=black git commit -m "feat: new feature"
```

## 📝 **Commit Message Format**

Pre-commit enforces conventional commit format:

```bash
# ✅ Good commit messages
git commit -m "feat: add user authentication system"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation"
git commit -m "style: format code with black"
git commit -m "test: add unit tests for auth module"
git commit -m "ci: update GitHub Actions workflow"

# ❌ Bad commit messages
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "updates"
```

### **Commit Types**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes
- `wip`: Work in progress
- `skip`: Skip checks (emergency overrides)

## 🚨 **Common Issues and Solutions**

### **Black Formatting Issues**
```bash
# Fix formatting automatically
cd backend && black . --line-length=120

# Check what would be formatted
cd backend && black . --line-length=120 --check
```

### **isort Import Issues**
```bash
# Fix import sorting automatically
cd backend && isort . --profile=black --line-length=120

# Check import sorting
cd backend && isort . --profile=black --line-length=120 --check-only
```

### **Flake8 Linting Issues**
```bash
# Check for linting issues
cd backend && flake8 . --max-line-length=120

# Common fixes:
# - Remove unused imports
# - Fix line length violations
# - Add missing docstrings
```

### **MyPy Type Issues**
```bash
# Check types
cd backend && mypy . --config-file=pyproject.toml

# Common fixes:
# - Add type annotations
# - Fix import issues
# - Resolve type conflicts
```

### **Frontend Issues**
```bash
# Fix linting issues
cd frontend && npm run lint:fix

# Check types
cd frontend && npm run type-check

# Verify build
cd frontend && npm run build
```

## 🔧 **Configuration Files**

### **`.pre-commit-config.yaml`**
Main configuration file defining all hooks and their settings.

### **`commitlint.config.js`**
Commit message format rules and validation.

### **`requirements-pre-commit.txt`**
Python dependencies for pre-commit tools.

### **`scripts/setup-pre-commit.sh`**
Automated setup script for all tools.

## 🎯 **Benefits**

1. **Prevents CI/CD Failures**: Catch issues before they reach the repository
2. **Consistent Code Quality**: Enforce standards across the team
3. **Faster Development**: Immediate feedback on code issues
4. **Better Commit History**: Meaningful and consistent commit messages
5. **Security**: Automatic security vulnerability scanning
6. **Documentation**: Enforce documentation standards

## 🆘 **Getting Help**

### **Pre-Commit Issues**
```bash
# Check pre-commit version
pre-commit --version

# Update pre-commit
pre-commit autoupdate

# Clean and reinstall hooks
pre-commit uninstall
pre-commit install --install-hooks
```

### **Hook-Specific Issues**
```bash
# Check hook configuration
pre-commit run --verbose

# Run specific hook with debug info
pre-commit run black --verbose
```

### **Emergency Override**
If you must commit without checks:
```bash
git commit -m "skip: emergency fix - will complete checks in follow-up" --no-verify
```

## 📚 **Additional Resources**

- [Pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [ESLint Documentation](https://eslint.org/)

---

**Remember**: Pre-commit hooks are your friend! They help maintain code quality and prevent embarrassing CI/CD failures. 🚀
