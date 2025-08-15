# 🚀 My First Bank App - Automation Workflow

## Overview
This document explains how to use the automated workflow that integrates Linear.app project management with Cursor background jobs for seamless development iterations.

## 🔄 **Automated Workflow Components**

### 1. **Linear.app Integration** (`update_linear.py`)
- Automatically updates project status based on development activities
- Creates issues for failed tests, linting violations, and other problems
- Tracks progress and milestone completion
- Reports coverage improvements and code quality metrics

### 2. **Background Jobs** (`run_background_jobs.py`)
- Runs continuously to monitor and update the project
- Executes automated testing and linting
- Updates Linear.app with progress
- Handles CI/CD pipeline monitoring

### 3. **Seamless Iterations**
- Background jobs run continuously without user intervention
- Linear.app updates happen automatically
- Development progress is tracked in real-time
- No manual status updates required

## 🛠️ **Setup Instructions**

### **Prerequisites**
- Docker and Docker Compose running
- Python 3.11+ with required dependencies
- Linear.app account and API access

### **Environment Variables**
Create or update your `.env` file with:
```bash
# Linear.app Integration
LINEAR_API_KEY=your_linear_api_key
LINEAR_PROJECT_ID=your_project_id
LINEAR_TEAM_ID=your_team_id

# Existing variables...
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bankapp
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### **Install Dependencies**
```bash
pip install -r requirements.txt
```

## 🚀 **Quick Start**

### **1. Start the Environment**
```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### **2. Test Linear.app Integration**
```bash
# Update Linear.app project status
python update_linear.py
```

### **3. Start Background Jobs**
```bash
# Run background jobs continuously
python run_background_jobs.py
```

## 📋 **Usage Examples**

### **Manual Linear.app Update**
```bash
# Update project status
python update_linear.py

# Run with specific environment variables
LINEAR_API_KEY=your_key LINEAR_PROJECT_ID=your_id python update_linear.py
```

### **Background Job Management**
```bash
# Start background jobs
python run_background_jobs.py

# Stop background jobs (Ctrl+C)

# View logs
tail -f background_jobs.log
```

### **Systemd Service (Persistent)**
```bash
# Create systemd service
sudo cp bankapp-automation.service /etc/systemd/system/

# Edit the service file to set correct paths
sudo nano /etc/systemd/system/bankapp-automation.service

# Enable and start service
sudo systemctl enable bankapp-automation
sudo systemctl start bankapp-automation

# Check status
sudo systemctl status bankapp-automation

# View logs
sudo journalctl -u bankapp-automation -f
```

## 🔧 **Configuration Options**

### **Background Job Intervals**
Edit `run_background_jobs.py` to adjust timing:
```python
# Success wait time (default: 5 minutes)
wait_time = 300

# Failure wait time (default: 1 minute)
wait_time = 60

# Maximum consecutive failures before stopping
max_consecutive_failures = 3
```

### **Logging Configuration**
The script automatically creates `background_jobs.log` with:
- Timestamp for each action
- Success/failure status
- Error details and stack traces
- Iteration summaries

### **Health Checks**
The script performs these checks before each iteration:
- Docker Compose service status
- Database connectivity
- Service health verification

## 📊 **What Gets Automated**

### **Every Iteration (5 minutes)**
1. **Health Checks**
   - Service status verification
   - Database connectivity test

2. **Backend Quality Checks**
   - Black formatting check (120 char line length)
   - isort import sorting check
   - Flake8 linting check

3. **Testing**
   - Backend unit tests
   - Frontend tests (if available)

4. **Linear.app Updates**
   - Project status updates
   - Issue creation for problems
   - Progress tracking

### **Automatic Issue Creation**
The system creates Linear.app issues for:
- Failed backend tests
- Linting violations
- Service health problems
- Coverage below targets
- CI/CD pipeline failures

## 🔍 **Monitoring and Troubleshooting**

### **Check Background Job Status**
```bash
# View current logs
tail -f background_jobs.log

# Check systemd service status
sudo systemctl status bankapp-automation

# View systemd logs
sudo journalctl -u bankapp-automation -f
```

### **Common Issues**

#### **Linear.app API Errors**
```bash
# Check environment variables
echo $LINEAR_API_KEY
echo $LINEAR_PROJECT_ID
echo $LINEAR_TEAM_ID

# Test API connection
python -c "
import os
import requests
key = os.getenv('LINEAR_API_KEY')
if key:
    response = requests.get('https://api.linear.app/graphql', 
                          headers={'Authorization': f'Bearer {key}'})
    print(f'API Status: {response.status_code}')
else:
    print('LINEAR_API_KEY not set')
"
```

#### **Background Job Failures**
```bash
# Check service status
sudo systemctl status bankapp-automation

# Restart service
sudo systemctl restart bankapp-automation

# View detailed logs
sudo journalctl -u bankapp-automation -f --since "1 hour ago"
```

#### **Docker Service Issues**
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Restart services
docker-compose restart
```

## 🎯 **Success Metrics**

### **Automation Goals**
- **95%+ of routine tasks** automated
- **Real-time progress tracking** in Linear.app
- **Zero manual status updates** required
- **Continuous monitoring** with alerts
- **Seamless development iterations**

### **Quality Targets**
- **80%+ test coverage** for backend
- **Zero linting violations** in CI/CD
- **All tests passing** before merge
- **Type safety** maintained across codebase
- **Performance benchmarks** met consistently

## 🔮 **Future Enhancements**

### **Planned Automation**
- **AI-powered code review** suggestions
- **Automatic dependency updates** with security scanning
- **Performance regression detection**
- **User behavior analytics** for UX improvements
- **Predictive issue detection**

### **Integration Improvements**
- **Slack/Discord notifications** for team updates
- **GitHub Apps** for enhanced automation
- **Custom dashboards** for stakeholders
- **API rate limiting** and optimization

## 📞 **Support**

### **Getting Help**
1. **Check logs**: `tail -f background_jobs.log`
2. **Verify environment**: Check `.env` file and variables
3. **Test manually**: Run `python update_linear.py` directly
4. **Check services**: `docker-compose ps` and `docker-compose logs`
5. **Create Linear.app issue**: For persistent problems

### **Useful Commands**
```bash
# Quick health check
docker-compose ps && echo "Services OK" || echo "Services need attention"

# Test Linear.app connection
python update_linear.py

# Run single iteration
python -c "from run_background_jobs import run_iteration; run_iteration()"

# Check background job logs
tail -n 50 background_jobs.log
```

---

**Remember**: The goal is to minimize manual intervention while maximizing development velocity and code quality. Let the automation handle the routine tasks while you focus on building great features! 🚀

## 📚 **Related Documentation**
- [Main Development Instructions](instructions_doc.md)
- [Linear.app API Documentation](https://developers.linear.app/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Systemd Service Documentation](https://systemd.io/)
