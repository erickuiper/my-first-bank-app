#!/usr/bin/env python3
"""
Script to create a new project in Linear.app for My First Bank App
"""

import os
import requests
import json

LINEAR_API_KEY = os.getenv('LINEAR_API_KEY')
LINEAR_TEAM_ID = os.getenv('LINEAR_TEAM_ID')
LINEAR_API_URL = "https://api.linear.app/graphql"

def get_headers():
    """Get headers for Linear API requests"""
    return {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json",
    }

def create_project():
    """Create a new project for My First Bank App"""
    query = """
    mutation CreateProject($input: ProjectCreateInput!) {
        projectCreate(input: $input) {
            success
            project {
                id
                name
                description
                state
                url
            }
        }
    }
    """
    
    variables = {
        "input": {
            "name": "My First Bank App",
            "description": "A comprehensive banking application for children with FastAPI backend, React Native frontend, and automated CI/CD pipeline.",
            "teamIds": [LINEAR_TEAM_ID]
        }
    }
    
    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query, "variables": variables}
    )
    
    print(f"🔍 Response status: {response.status_code}")
    print(f"🔍 Response text: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"🔍 Parsed response: {json.dumps(data, indent=2)}")
            
            if data and data.get("data", {}).get("projectCreate", {}).get("success"):
                project = data["data"]["projectCreate"]["project"]
                print(f"✅ Project created successfully!")
                print(f"   Name: {project['name']}")
                print(f"   ID: {project['id']}")
                print(f"   URL: {project['url']}")
                print(f"   State: {project['state']}")
                return project
            else:
                print(f"❌ Failed to create project")
                if data and "errors" in data:
                    for error in data["errors"]:
                        print(f"   {error['message']}")
                return None
        except Exception as e:
            print(f"❌ Error parsing response: {e}")
            return None
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def create_initial_issues(project_id):
    """Create initial issues for the project"""
    issues = [
        {
            "title": "🚀 Project Setup Complete",
            "description": "Initial project setup with FastAPI backend, React Native frontend, and Docker Compose environment.",
            "priority": "HIGH",
            "state": "Done"
        },
        {
            "title": "✅ Backend Linting & Code Quality",
            "description": "All backend linting issues resolved. Tools configured for 120 character line length: Black, isort, Flake8, MyPy.",
            "priority": "HIGH",
            "state": "Done"
        },
        {
            "title": "✅ Frontend TypeScript Issues",
            "description": "Frontend TypeScript issues resolved. Deposit screens, authentication screens, and API service fixed.",
            "priority": "HIGH",
            "state": "Done"
        },
        {
            "title": "✅ CI/CD Pipeline Configuration",
            "description": "GitHub Actions pipeline updated with 120 character line length, fixed integration tests, and automated checks.",
            "priority": "HIGH",
            "state": "Done"
        },
        {
            "title": "🔄 Linear.app Integration",
            "description": "Automated Linear.app integration for project tracking and issue management.",
            "priority": "MEDIUM",
            "state": "In Progress"
        },
        {
            "title": "📋 Background Jobs Automation",
            "description": "Set up Cursor background jobs for automated testing, linting, and Linear.app updates.",
            "priority": "MEDIUM",
            "state": "In Progress"
        },
        {
            "title": "🧪 Test Coverage Improvement",
            "description": "Increase backend test coverage to 80%+ and add comprehensive frontend tests.",
            "priority": "MEDIUM",
            "state": "Todo"
        },
        {
            "title": "🚀 Production Deployment",
            "description": "Prepare for production deployment with monitoring, logging, and security hardening.",
            "priority": "LOW",
            "state": "Todo"
        }
    ]
    
    created_issues = []
    
    for issue_data in issues:
        issue = create_issue(project_id, issue_data)
        if issue:
            created_issues.append(issue)
    
    return created_issues

def create_issue(project_id, issue_data):
    """Create an issue in the project"""
    query = """
    mutation CreateIssue($input: IssueCreateInput!) {
        issueCreate(input: $input) {
            success
            issue {
                id
                title
                url
                state {
                    name
                }
            }
        }
    }
    """
    
    # Map state names to Linear.app state IDs
    state_mapping = {
        "Todo": "backlog",
        "In Progress": "inProgress", 
        "Done": "done"
    }
    
    variables = {
        "input": {
            "title": issue_data["title"],
            "description": issue_data["description"],
            "projectId": project_id,
            "teamId": LINEAR_TEAM_ID,
            "priority": issue_data["priority"],
            "stateId": state_mapping.get(issue_data["state"], "backlog")
        }
    }
    
    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query, "variables": variables}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("data", {}).get("issueCreate", {}).get("success"):
            issue = data["data"]["issueCreate"]["issue"]
            print(f"✅ Created issue: {issue['title']}")
            print(f"   URL: {issue['url']}")
            print(f"   State: {issue['state']['name']}")
            return issue
        else:
            errors = data.get("data", {}).get("issueCreate", {}).get("errors", [])
            print(f"❌ Failed to create issue '{issue_data['title']}':")
            for error in errors:
                print(f"   {error['message']}")
            return None
    else:
        print(f"❌ HTTP Error creating issue: {response.status_code}")
        return None

def main():
    """Main function to create project and issues"""
    if not LINEAR_API_KEY:
        print("❌ LINEAR_API_KEY environment variable not set")
        return
    
    if not LINEAR_TEAM_ID:
        print("❌ LINEAR_TEAM_ID environment variable not set")
        print("💡 Run 'python get_linear_info.py' first to get your team ID")
        return
    
    print("🚀 Creating Linear.app project for My First Bank App")
    print("=" * 60)
    
    # Create project
    project = create_project()
    if not project:
        print("❌ Failed to create project")
        return
    
    print(f"\n📋 Project created with ID: {project['id']}")
    print("🔧 Now creating initial issues...")
    print()
    
    # Create initial issues
    issues = create_initial_issues(project['id'])
    
    print(f"\n🎉 Project setup complete!")
    print(f"📊 Created {len(issues)} issues")
    print(f"🔗 Project URL: {project['url']}")
    
    # Show environment variable setup
    print(f"\n🔧 Add this to your .env file:")
    print(f"LINEAR_PROJECT_ID={project['id']}")
    print(f"LINEAR_TEAM_ID={LINEAR_TEAM_ID}")
    
    print(f"\n💡 You can now run 'python update_linear.py' to update the project!")

if __name__ == "__main__":
    main()
