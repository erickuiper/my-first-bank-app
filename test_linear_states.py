#!/usr/bin/env python3
"""
Test script to check Linear.app states and workflow
"""

import os
import requests
import json

LINEAR_API_KEY = os.getenv('LINEAR_API_KEY')
LINEAR_TEAM_ID = os.getenv('LINEAR_TEAM_ID')
LINEAR_PROJECT_ID = os.getenv('LINEAR_PROJECT_ID')
LINEAR_API_URL = "https://api.linear.app/graphql"

def get_headers():
    """Get headers for Linear API requests"""
    return {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json",
    }

def get_workflow_states():
    """Get available workflow states"""
    query = """
    query {
        workflowStates {
            nodes {
                id
                name
                type
                team {
                    id
                    name
                }
            }
        }
    }
    """
    
    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query}
    )
    
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
            return []
        return data.get("data", {}).get("workflowStates", {}).get("nodes", [])
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        return []

def test_create_simple_issue():
    """Test creating a simple issue"""
    query = """
    mutation CreateIssue($input: IssueCreateInput!) {
        issueCreate(input: $input) {
            success
            issue {
                id
                title
                url
            }
        }
    }
    """
    
    variables = {
        "input": {
            "title": "Test Issue - Project Status Update",
            "description": "This is a test issue to verify the Linear.app integration is working correctly.",
            "projectId": LINEAR_PROJECT_ID,
            "teamId": LINEAR_TEAM_ID
        }
    }
    
    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query, "variables": variables}
    )
    
    print(f"🔍 Test issue creation - Status: {response.status_code}")
    print(f"🔍 Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
            return False
        elif data.get("data", {}).get("issueCreate", {}).get("success"):
            issue = data["data"]["issueCreate"]["issue"]
            print(f"✅ Test issue created successfully!")
            print(f"   ID: {issue['id']}")
            print(f"   URL: {issue['url']}")
            return True
        else:
            print(f"❌ Issue creation failed")
            return False
    else:
        print(f"❌ HTTP Error")
        return False

def main():
    """Main function"""
    print("🔍 Testing Linear.app integration...")
    print("=" * 50)
    
    # Check environment variables
    print(f"LINEAR_API_KEY: {'✅ SET' if LINEAR_API_KEY else '❌ NOT SET'}")
    print(f"LINEAR_TEAM_ID: {'✅ SET' if LINEAR_TEAM_ID else '❌ NOT SET'}")
    print(f"LINEAR_PROJECT_ID: {'✅ SET' if LINEAR_PROJECT_ID else '❌ NOT SET'}")
    print()
    
    if not all([LINEAR_API_KEY, LINEAR_TEAM_ID, LINEAR_PROJECT_ID]):
        print("❌ Missing required environment variables")
        return
    
    # Get workflow states
    print("📋 Available Workflow States:")
    states = get_workflow_states()
    for state in states:
        if state.get('team', {}).get('id') == LINEAR_TEAM_ID:
            print(f"   ID: {state['id']}")
            print(f"   Name: {state['name']}")
            print(f"   Type: {state['type']}")
            print()
    
    # Test issue creation
    print("🧪 Testing Issue Creation:")
    success = test_create_simple_issue()
    
    if success:
        print("\n✅ Linear.app integration is working correctly!")
    else:
        print("\n❌ There are issues with the Linear.app integration")

if __name__ == "__main__":
    main()
