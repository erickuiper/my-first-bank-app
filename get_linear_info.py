#!/usr/bin/env python3
"""
Helper script to get Linear.app project and team information
"""

import os
import requests
import json

LINEAR_API_KEY = os.getenv('LINEAR_API_KEY')
LINEAR_API_URL = "https://api.linear.app/graphql"

def get_headers():
    """Get headers for Linear API requests"""
    return {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json",
    }

def test_api_connection():
    """Test the API connection"""
    query = """
    query {
        viewer {
            id
            name
            email
        }
    }
    """
    
    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query}
    )
    
    print(f"🔍 API Test - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
            return False
        else:
            viewer = data.get("data", {}).get("viewer", {})
            print(f"✅ Connected as: {viewer.get('name', 'Unknown')} ({viewer.get('email', 'Unknown')})")
            return True
    else:
        print(f"❌ HTTP Error: {response.text}")
        return False

def get_teams():
    """Get all teams"""
    query = """
    query {
        teams {
            nodes {
                id
                name
                key
                description
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
            print(f"❌ GraphQL Errors in teams query: {data['errors']}")
            return []
        return data.get("data", {}).get("teams", {}).get("nodes", [])
    else:
        print(f"❌ HTTP Error getting teams: {response.status_code}")
        print(f"Response: {response.text}")
        return []

def get_projects():
    """Get all projects"""
    query = """
    query {
        projects {
            nodes {
                id
                name
                description
                state
                teams {
                    nodes {
                        id
                        name
                        key
                    }
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
            print(f"❌ GraphQL Errors in projects query: {data['errors']}")
            return []
        return data.get("data", {}).get("projects", {}).get("nodes", [])
    else:
        print(f"❌ HTTP Error getting projects: {response.status_code}")
        print(f"Response: {response.text}")
        return []

def get_issues():
    """Get recent issues to understand the project structure"""
    query = """
    query {
        issues(first: 10) {
            nodes {
                id
                title
                state {
                    name
                }
                team {
                    id
                    name
                    key
                }
                project {
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
            print(f"❌ GraphQL Errors in issues query: {data['errors']}")
            return []
        return data.get("data", {}).get("issues", {}).get("nodes", [])
    else:
        print(f"❌ HTTP Error getting issues: {response.status_code}")
        print(f"Response: {response.text}")
        return []

def main():
    """Main function to get Linear information"""
    if not LINEAR_API_KEY:
        print("❌ LINEAR_API_KEY environment variable not set")
        return
    
    print("🔍 Getting Linear.app information...")
    print("=" * 50)
    
    # Test API connection first
    if not test_api_connection():
        print("\n❌ Cannot connect to Linear.app API. Please check your API key.")
        return
    
    print("\n📋 Teams:")
    teams = get_teams()
    if teams:
        for team in teams:
            print(f"   ID: {team['id']}")
            print(f"   Name: {team['name']}")
            print(f"   Key: {team['key']}")
            if team.get('description'):
                print(f"   Description: {team['description']}")
            print()
    else:
        print("   No teams found or error occurred")
    
    print("📋 Projects:")
    projects = get_projects()
    if projects:
        for project in projects:
            print(f"   ID: {project['id']}")
            print(f"   Name: {project['name']}")
            print(f"   State: {project['state']}")
            if project.get('description'):
                print(f"   Description: {project['description']}")
                    if project.get('teams', {}).get('nodes'):
            teams = [f"{team['name']} ({team['key']})" for team in project['teams']['nodes']]
            print(f"   Teams: {', '.join(teams)}")
            print()
    else:
        print("   No projects found or error occurred")
    
    print("📋 Recent Issues:")
    issues = get_issues()
    if issues:
        for issue in issues:
            print(f"   Title: {issue['title']}")
            print(f"   State: {issue['state']['name']}")
            if issue.get('team'):
                print(f"   Team: {issue['team']['name']} ({issue['team']['key']})")
            if issue.get('project'):
                print(f"   Project: {issue['project']['name']}")
            print()
    else:
        print("   No issues found or error occurred")
    
    # Show environment variable setup
    print("🔧 Environment Variables Setup:")
    print("Add these to your .env file:")
    print()
    
    if teams:
        print(f"LINEAR_TEAM_ID={teams[0]['id']}")
    
    if projects:
        # Look for "My first bank app" or similar
        bank_app_project = None
        for project in projects:
            if 'bank' in project['name'].lower() or 'first' in project['name'].lower():
                bank_app_project = project
                break
        
        if bank_app_project:
            print(f"LINEAR_PROJECT_ID={bank_app_project['id']}")
        else:
            print(f"LINEAR_PROJECT_ID={projects[0]['id']}  # First project found")
    
    print()
    print("💡 Tip: Look for a project with 'bank' or 'first' in the name above")
    print("   If you don't see your project, you may need to create it in Linear.app first")

if __name__ == "__main__":
    main()
