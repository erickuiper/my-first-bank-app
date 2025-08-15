#!/bin/bash

# Heroku Deployment Script
# This script automates the deployment process to Heroku

set -e  # Exit on any error

echo "🚀 Starting Heroku deployment..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first:"
    echo "   macOS: brew tap heroku/brew && brew install heroku"
    echo "   Linux: curl https://cli-assets.heroku.com/install.sh | sh"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run 'heroku login' first."
    exit 1
fi

# Get app name from command line argument or prompt
if [ -z "$1" ]; then
    echo "📝 Enter your Heroku app name:"
    read APP_NAME
else
    APP_NAME=$1
fi

echo "📱 Deploying to app: $APP_NAME"

# Check if app exists, create if it doesn't
if ! heroku apps:info --app $APP_NAME &> /dev/null; then
    echo "🆕 Creating new Heroku app: $APP_NAME"
    heroku create $APP_NAME
else
    echo "✅ App $APP_NAME already exists"
fi

# Add PostgreSQL database if not already added
if ! heroku addons:info heroku-postgresql --app $APP_NAME &> /dev/null; then
    echo "🗄️ Adding PostgreSQL database..."
    heroku addons:create heroku-postgresql:mini --app $APP_NAME
else
    echo "✅ PostgreSQL database already exists"
fi

# Set environment variables
echo "🔧 Setting environment variables..."
heroku config:set SECRET_KEY="$(openssl rand -base64 32)" --app $APP_NAME
heroku config:set DEBUG="false" --app $APP_NAME

# Show current configuration
echo "📋 Current configuration:"
heroku config --app $APP_NAME

# Deploy the application
echo "🚀 Deploying application..."
git add .
git commit -m "Deploy to Heroku" || echo "No changes to commit"

# Add Heroku remote if not already added
if ! git remote | grep -q heroku; then
    echo "🔗 Adding Heroku remote..."
    heroku git:remote -a $APP_NAME
fi

# Push to Heroku
echo "📤 Pushing to Heroku..."
git push heroku main || git push heroku master

# Run database migrations
echo "🗄️ Running database migrations..."
heroku run alembic upgrade head --app $APP_NAME

# Open the app
echo "🌐 Opening app in browser..."
heroku open --app $APP_NAME

echo "✅ Deployment complete!"
echo "🔗 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📊 View logs with: heroku logs --tail --app $APP_NAME"
echo "🔧 Manage your app at: https://dashboard.heroku.com/apps/$APP_NAME"
