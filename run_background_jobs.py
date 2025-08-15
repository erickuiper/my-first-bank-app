#!/usr/bin/env python3
"""
Background Jobs Script for My First Bank App
Runs automated testing, linting, and Linear.app updates continuously
"""

import time
import subprocess
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_jobs.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_command(cmd, description):
    """Run a command and log the result"""
    try:
        logger.info(f"🔄 Running: {description}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"✅ Success: {description}")
        if result.stdout:
            logger.debug(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error in {description}: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['LINEAR_API_KEY', 'LINEAR_PROJECT_ID', 'LINEAR_TEAM_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        logger.warning("Linear.app integration will be skipped")
        return False
    
    logger.info("✅ Environment variables configured")
    return True

def run_backend_tests():
    """Run backend tests"""
    return run_command(
        ['docker-compose', 'exec', '-T', 'backend', 'pytest', '--tb=short'],
        "Backend tests"
    )

def run_backend_linting():
    """Run backend linting tools"""
    linting_commands = [
        (['docker-compose', 'exec', '-T', 'backend', 'black', '--check', '--diff', '--line-length=120', '.'], "Black formatting check"),
        (['docker-compose', 'exec', '-T', 'backend', 'isort', '--check-only', '--diff', '--profile=black', '--line-length=120', '.'], "isort import check"),
        (['docker-compose', 'exec', '-T', 'backend', 'flake8', '.', '--max-line-length=120', '--extend-ignore=E203,W503'], "Flake8 linting"),
    ]
    
    all_passed = True
    for cmd, desc in linting_commands:
        if not run_command(cmd, desc):
            all_passed = False
    
    return all_passed

def run_frontend_tests():
    """Run frontend tests"""
    return run_command(
        ['docker-compose', 'exec', '-T', 'frontend', 'npm', 'run', 'test'],
        "Frontend tests"
    )

def update_linear_app():
    """Update Linear.app project status"""
    if not check_environment():
        logger.info("⏭️ Skipping Linear.app update due to missing environment variables")
        return True
    
    return run_command(
        ['python', 'update_linear.py'],
        "Linear.app project update"
    )

def run_health_checks():
    """Run basic health checks"""
    health_commands = [
        (['docker-compose', 'ps'], "Service status check"),
        (['docker-compose', 'exec', '-T', 'postgres', 'pg_isready', '-U', 'postgres'], "Database health check"),
    ]
    
    all_healthy = True
    for cmd, desc in health_commands:
        if not run_command(cmd, desc):
            all_healthy = False
    
    return all_healthy

def run_iteration():
    """Run one complete iteration of background jobs"""
    logger.info("🚀 Starting new iteration")
    
    # Health checks
    if not run_health_checks():
        logger.warning("⚠️ Health checks failed, continuing with other tasks")
    
    # Backend quality checks
    backend_linting_ok = run_backend_linting()
    backend_tests_ok = run_backend_tests()
    
    # Frontend tests
    frontend_tests_ok = run_frontend_tests()
    
    # Update Linear.app
    linear_update_ok = update_linear_app()
    
    # Summary
    logger.info("📊 Iteration Summary:")
    logger.info(f"   Backend Linting: {'✅' if backend_linting_ok else '❌'}")
    logger.info(f"   Backend Tests: {'✅' if backend_tests_ok else '❌'}")
    logger.info(f"   Frontend Tests: {'✅' if frontend_tests_ok else '❌'}")
    logger.info(f"   Linear.app Update: {'✅' if linear_update_ok else '❌'}")
    
    return all([backend_linting_ok, backend_tests_ok, frontend_tests_ok, linear_update_ok])

def main():
    """Main function to run background jobs continuously"""
    logger.info("🚀 Starting My First Bank App Background Jobs")
    logger.info("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('docker-compose.yml'):
        logger.error("❌ docker-compose.yml not found. Please run this script from the project root.")
        return
    
    # Check if services are running
    try:
        subprocess.run(['docker-compose', 'ps'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ Docker Compose not available or services not running")
        logger.info("💡 Please start the services with: docker-compose up -d")
        return
    
    iteration_count = 0
    consecutive_failures = 0
    max_consecutive_failures = 3
    
    while True:
        try:
            iteration_count += 1
            logger.info(f"🔄 Iteration {iteration_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Run iteration
            success = run_iteration()
            
            if success:
                consecutive_failures = 0
                logger.info(f"✅ Iteration {iteration_count} completed successfully")
                wait_time = 300  # 5 minutes on success
            else:
                consecutive_failures += 1
                logger.warning(f"⚠️ Iteration {iteration_count} had issues (consecutive failures: {consecutive_failures})")
                
                if consecutive_failures >= max_consecutive_failures:
                    logger.error(f"❌ Too many consecutive failures ({consecutive_failures}). Stopping background jobs.")
                    break
                
                wait_time = 60  # 1 minute on failure
            
            logger.info(f"⏳ Waiting {wait_time} seconds before next iteration...")
            time.sleep(wait_time)
            
        except KeyboardInterrupt:
            logger.info("🛑 Background jobs stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error in main loop: {e}")
            consecutive_failures += 1
            
            if consecutive_failures >= max_consecutive_failures:
                logger.error(f"❌ Too many consecutive failures ({consecutive_failures}). Stopping background jobs.")
                break
            
            logger.info("⏳ Waiting 60 seconds before retry...")
            time.sleep(60)
    
    logger.info("🏁 Background jobs stopped")

if __name__ == "__main__":
    main()
