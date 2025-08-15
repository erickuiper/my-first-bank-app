#!/usr/bin/env python3
"""
Test script to verify Heroku deployment
Run this after deployment to ensure everything is working
"""

import os
import sys

import requests


def test_endpoint(base_url, endpoint, expected_status=200):
    """Test a specific endpoint"""
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {endpoint}: {response.status_code}")
            return True
        else:
            print(
                f"❌ {endpoint}: Expected {expected_status}, got {response.status_code}"
            )
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint}: Error - {e}")
        return False


def main():
    # Get the app URL from command line or environment
    if len(sys.argv) > 1:
        app_url = sys.argv[1]
    else:
        app_url = os.getenv("HEROKU_APP_URL")
        if not app_url:
            print(
                "❌ Please provide the Heroku app URL as an argument or set HEROKU_APP_URL environment variable"
            )
            print(
                "Usage: python test_deployment.py https://your-app-name.herokuapp.com"
            )
            sys.exit(1)

    # Ensure URL has proper format
    if not app_url.startswith("http"):
        app_url = f"https://{app_url}.herokuapp.com"

    print(f"🧪 Testing deployment at: {app_url}")
    print("=" * 50)

    # Test endpoints
    endpoints = [
        ("/", 200),
        ("/health", 200),
        ("/api/v1/", 404),  # Should return 404 for empty API endpoint
    ]

    success_count = 0
    total_count = len(endpoints)

    for endpoint, expected_status in endpoints:
        if test_endpoint(app_url, endpoint, expected_status):
            success_count += 1

    print("=" * 50)
    print(f"📊 Test Results: {success_count}/{total_count} passed")

    if success_count == total_count:
        print("🎉 All tests passed! Your deployment is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check your deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
