# Heroku Deployment Guide

This guide will walk you through deploying your FastAPI backend to Heroku.

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Ensure your project is in a Git repository

## Step 1: Install Heroku CLI

### macOS
```bash
brew tap heroku/brew && brew install heroku
```

### Linux
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

## Step 2: Login to Heroku

```bash
heroku login
```

## Step 3: Create a New Heroku App

Navigate to your backend directory and run:

```bash
cd backend
heroku create your-app-name
```

Replace `your-app-name` with a unique name for your app.

## Step 4: Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:mini
```

This will automatically set the `DATABASE_URL` environment variable.

## Step 5: Set Environment Variables

```bash
# Set a secure secret key
heroku config:set SECRET_KEY="your-super-secret-key-here-make-it-long-and-random"

# Set debug mode (optional, defaults to False)
heroku config:set DEBUG="false"

# View all config variables
heroku config
```

## Step 6: Deploy Your Application

### Option A: Deploy from Git (Recommended)

```bash
# Add Heroku remote
heroku git:remote -a your-app-name

# Commit your changes
git add .
git commit -m "Prepare for Heroku deployment"

# Push to Heroku
git push heroku main
```

### Option B: Deploy from GitHub

1. Connect your GitHub repository in the Heroku dashboard
2. Enable automatic deploys
3. Deploy manually or wait for automatic deployment

## Step 7: Run Database Migrations

```bash
# Run Alembic migrations
heroku run alembic upgrade head
```

## Step 8: Verify Deployment

```bash
# Open your app in the browser
heroku open

# Check the logs
heroku logs --tail

# Test the health endpoint
curl https://your-app-name.herokuapp.com/health
```

## Step 9: Update Frontend Configuration

Update your frontend API configuration to point to the new Heroku backend:

```typescript
// In frontend/src/services/api.ts
const API_BASE_URL = 'https://your-app-name.herokuapp.com/api/v1';
```

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Auto-set by Heroku | Yes |
| `SECRET_KEY` | JWT signing key | Random string | Yes |
| `DEBUG` | Debug mode | `false` | No |
| `PORT` | Port to bind to | Auto-set by Heroku | No |

## Troubleshooting

### Common Issues

1. **Build Fails**: Check the build logs with `heroku logs --tail`
2. **Database Connection**: Ensure `DATABASE_URL` is set correctly
3. **Port Binding**: The app must bind to `$PORT` (handled automatically)
4. **Dependencies**: Ensure all required packages are in `requirements.txt`

### Useful Commands

```bash
# View logs
heroku logs --tail

# Check app status
heroku ps

# Restart the app
heroku restart

# Run commands on the dyno
heroku run python manage.py shell

# Check environment variables
heroku config

# Scale the app
heroku ps:scale web=1
```

### Performance Optimization

1. **Database Connection Pooling**: Consider using connection pooling for better performance
2. **Caching**: Implement Redis caching for frequently accessed data
3. **Monitoring**: Use Heroku add-ons for monitoring and logging

## Security Considerations

1. **SECRET_KEY**: Use a strong, random secret key
2. **CORS**: Restrict CORS origins in production
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **HTTPS**: Heroku automatically provides HTTPS
5. **Environment Variables**: Never commit sensitive data to version control

## Cost Optimization

- **Database**: Start with the free tier (`mini`) and scale as needed
- **Dynos**: Use the free tier for development, paid tiers for production
- **Add-ons**: Only add necessary add-ons to avoid unexpected costs

## Next Steps

After successful deployment:

1. Set up monitoring and logging
2. Configure custom domain (optional)
3. Set up CI/CD pipeline
4. Implement backup strategies
5. Set up staging environment

## Support

- [Heroku Documentation](https://devcenter.heroku.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Heroku Support](https://help.heroku.com/)
