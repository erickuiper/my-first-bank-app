# Heroku Deployment Checklist

## Pre-Deployment Checklist

- [ ] **Heroku CLI installed** - `heroku --version`
- [ ] **Logged into Heroku** - `heroku login`
- [ ] **Git repository initialized** - `git status`
- [ ] **All changes committed** - `git add . && git commit -m "message"`
- [ ] **Backend directory is clean** - No unnecessary files
- [ ] **Environment variables documented** - See DEPLOYMENT.md

## Deployment Steps

### 1. Create Heroku App
```bash
cd backend
heroku create your-app-name
```

### 2. Add Database
```bash
heroku addons:create heroku-postgresql:mini
```

### 3. Set Environment Variables
```bash
heroku config:set SECRET_KEY="your-secure-secret-key"
heroku config:set DEBUG="false"
```

### 4. Deploy Application
```bash
heroku git:remote -a your-app-name
git push heroku main
```

### 5. Run Migrations
```bash
heroku run alembic upgrade head
```

## Post-Deployment Checklist

- [ ] **App is accessible** - `heroku open`
- [ ] **Health endpoint works** - `/health returns 200`
- [ ] **API endpoints accessible** - `/api/v1/ returns 404 (expected)`
- [ ] **Database connected** - No connection errors in logs
- [ ] **Environment variables set** - `heroku config`
- [ ] **Logs are clean** - `heroku logs --tail`

## Testing

### Run Test Script
```bash
python test_deployment.py https://your-app-name.herokuapp.com
```

### Manual Testing
- [ ] Visit root endpoint: `/`
- [ ] Check health endpoint: `/health`
- [ ] Verify CORS headers
- [ ] Test API endpoints (if any exist)

## Frontend Updates

- [ ] **Update API base URL** in `frontend/src/services/api.ts`
- [ ] **Replace placeholder** `your-backend-app-name` with actual app name
- [ ] **Test frontend** with new backend URL
- [ ] **Update CORS origins** in backend if needed

## Troubleshooting

### Common Issues
- [ ] **Build fails** - Check `heroku logs --tail`
- [ ] **Database connection** - Verify `DATABASE_URL` is set
- [ ] **CORS errors** - Check allowed origins in backend
- [ ] **Port binding** - Ensure app binds to `$PORT`

### Useful Commands
```bash
# View logs
heroku logs --tail

# Check app status
heroku ps

# Restart app
heroku restart

# Check environment
heroku config

# Run commands
heroku run python -c "print('Hello from Heroku!')"
```

## Security Checklist

- [ ] **SECRET_KEY is secure** - Long, random string
- [ ] **DEBUG is false** - Production setting
- [ ] **CORS is restricted** - Not allowing all origins
- [ ] **HTTPS enabled** - Heroku provides this automatically
- [ ] **No sensitive data** in code or logs

## Performance Checklist

- [ ] **Database connection pooling** - Consider implementing
- [ ] **Response times** - Monitor with `heroku logs`
- [ ] **Memory usage** - Check with `heroku ps`
- [ ] **Add-ons** - Only necessary ones enabled

## Monitoring Setup

- [ ] **Log monitoring** - Set up log aggregation
- [ ] **Performance monitoring** - Consider Heroku add-ons
- [ ] **Error tracking** - Set up error reporting
- [ ] **Uptime monitoring** - External service

## Backup Strategy

- [ ] **Database backups** - Heroku provides automatic backups
- [ ] **Code backups** - Git repository
- [ ] **Environment backup** - Document all config variables
- [ ] **Recovery plan** - Know how to restore from backup

## Cost Management

- [ ] **Database tier** - Start with `mini`, scale as needed
- [ ] **Dyno tier** - Free for development, paid for production
- [ ] **Add-ons** - Monitor usage and costs
- [ ] **Budget alerts** - Set up spending limits

## Next Steps

After successful deployment:
- [ ] Set up custom domain (optional)
- [ ] Configure CI/CD pipeline
- [ ] Set up staging environment
- [ ] Implement monitoring and alerting
- [ ] Plan for scaling
