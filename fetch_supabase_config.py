#!/usr/bin/env python3
"""
Fetch Supabase project configuration using access token
This script will get all your API keys and update the .env file automatically
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_supabase_config():
    """Fetch Supabase project configuration and update .env file"""
    
    # Get access token from environment
    access_token = os.environ.get("SUPABASE_ACCESS_TOKEN")
    if not access_token:
        print("❌ SUPABASE_ACCESS_TOKEN not found in .env file")
        return False
    
    base_url = "https://api.supabase.com/v1"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Fetching your Supabase projects...")
    
    try:
        # Get all projects
        response = requests.get(f"{base_url}/projects", headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch projects: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        projects = response.json()
        print(f"✅ Found {len(projects)} projects")
        
        # Show available projects and let user choose
        if len(projects) == 0:
            print("❌ No projects found in this account")
            print("💡 You can create a new project using: python setup_supabase.py")
            return False
        
        print("📋 Available projects:")
        for i, project in enumerate(projects):
            status = project.get('status', 'unknown')
            print(f"   {i+1}. {project['name']} (ref: {project.get('ref', 'N/A')}) - {status}")
        
        # Auto-select if only one project, otherwise ask user
        if len(projects) == 1:
            target_project = projects[0]
            print(f"🎯 Using only project: {target_project['name']}")
        else:
            try:
                choice = input("\n📋 Choose project number (1-{}): ".format(len(projects)))
                project_index = int(choice) - 1
                if 0 <= project_index < len(projects):
                    target_project = projects[project_index]
                    print(f"🎯 Selected: {target_project['name']}")
                else:
                    print("❌ Invalid choice")
                    return False
            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid input or cancelled")
                return False
        
        project_id = target_project['id']
        project_ref = target_project.get('ref')
        
        if not project_ref:
            print("⚠️  Project reference not available yet (project might still be initializing)")
            print("🔄 Let's try to get the project details directly...")
            
            # Try to get more project details
            detail_response = requests.get(f"{base_url}/projects/{project_id}", headers=headers)
            if detail_response.status_code == 200:
                project_details = detail_response.json()
                project_ref = project_details.get('ref')
                if project_ref:
                    print(f"✅ Found project reference: {project_ref}")
                else:
                    print("❌ Project reference still not available. Project may need more time to initialize.")
                    return False
            else:
                print("❌ Could not fetch project details")
                return False
        
        print(f"🎯 Found target project: {target_project['name']} (ID: {project_id}, Ref: {project_ref})")
        
        # Get project config with API keys
        print("🔑 Fetching API keys...")
        config_response = requests.get(f"{base_url}/projects/{project_id}/config", headers=headers)
        
        if config_response.status_code != 200:
            print(f"❌ Failed to fetch project config: {config_response.status_code}")
            return False
        
        config = config_response.json()
        
        # Extract configuration
        supabase_url = f"https://{project_ref}.supabase.co"
        anon_key = config.get('anon_key')
        service_role_key = config.get('service_role_key')
        
        if not anon_key or not service_role_key:
            print("❌ Could not find API keys in project config")
            return False
        
        print("✅ Successfully retrieved all configuration!")
        print(f"   URL: {supabase_url}")
        print(f"   Anon Key: {anon_key[:20]}...")
        print(f"   Service Key: {service_role_key[:20]}...")
        
        # Update .env file
        print("📝 Updating .env file...")
        update_env_file(supabase_url, anon_key, service_role_key)
        
        return True
        
    except Exception as e:
        print(f"❌ Error fetching configuration: {e}")
        return False

def update_env_file(supabase_url, anon_key, service_role_key):
    """Update .env file with the fetched configuration"""
    
    try:
        # Read current .env file
        env_file = ".env"
        if not os.path.exists(env_file):
            print("❌ .env file not found")
            return False
        
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update the relevant lines
        updated_lines = []
        for line in lines:
            if line.startswith('SUPABASE_URL='):
                updated_lines.append(f'SUPABASE_URL={supabase_url}\n')
            elif line.startswith('SUPABASE_ANON_KEY='):
                updated_lines.append(f'SUPABASE_ANON_KEY={anon_key}\n')
            elif line.startswith('SUPABASE_SERVICE_ROLE_KEY='):
                updated_lines.append(f'SUPABASE_SERVICE_ROLE_KEY={service_role_key}\n')
            else:
                updated_lines.append(line)
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ .env file updated successfully!")
        print("\n🎉 Your Supabase configuration is now complete!")
        print("\n📋 Next steps:")
        print("1. Add your other API keys (Groq, Hugging Face) to .env")
        print("2. Run: python test_supabase_connection.py")
        print("3. Run: python -c 'from supabase_setup import *' to run SQL setup")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Fetching Supabase Configuration")
    print("=" * 50)
    
    if fetch_supabase_config():
        print("\n✅ Configuration fetch completed successfully!")
    else:
        print("\n❌ Configuration fetch failed!")
        sys.exit(1)
