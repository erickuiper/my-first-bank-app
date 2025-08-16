#!/bin/bash

# Setup script for pre-commit hooks
# This script installs and configures all pre-commit hooks for the project

set -e

echo "🚀 Setting up pre-commit hooks for My First Bank App..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip install pre-commit
else
    echo "✅ pre-commit already installed"
fi

# Check if commitlint is installed
if ! command -v commitlint &> /dev/null; then
    echo "📦 Installing commitlint..."
    npm install -g @commitlint/cli @commitlint/config-conventional
else
    echo "✅ commitlint already installed"
fi

# Check if hadolint is installed (for Docker linting)
if ! command -v hadolint &> /dev/null; then
    echo "📦 Installing hadolint..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        wget -O /tmp/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64
        chmod +x /tmp/hadolint
        sudo mv /tmp/hadolint /usr/local/bin/hadolint
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install hadolint
    else
        echo "⚠️  Please install hadolint manually for your OS"
    fi
else
    echo "✅ hadolint already installed"
fi

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install --install-hooks

# Install commit-msg hook for commitlint
echo "🔧 Installing commit-msg hook..."
pre-commit install --hook-type commit-msg

# Verify installation
echo "🔍 Verifying pre-commit installation..."
pre-commit --version

echo "✅ Pre-commit hooks setup complete!"
echo ""
echo "📋 Available hooks:"
echo "  • Black formatting (Python)"
echo "  • isort import sorting (Python)"
echo "  • Flake8 linting (Python)"
echo "  • MyPy type checking (Python)"
echo "  • Pytest collection check (Python)"
echo "  • ESLint (Frontend)"
echo "  • TypeScript check (Frontend)"
echo "  • Build verification (Frontend)"
echo "  • Commit message linting"
echo "  • File quality checks"
echo "  • Security checks (Bandit)"
echo "  • Docker linting (Hadolint)"
echo ""
echo "🚀 Hooks will now run automatically on every commit!"
echo "💡 Run 'pre-commit run --all-files' to check all files manually"
echo "💡 Run 'pre-commit run' to check only staged files"
