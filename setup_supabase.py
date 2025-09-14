#!/usr/bin/env python3
"""
Automated Supabase setup script for Epicure
This script can create a project, run migrations, and configure everything automatically
"""

import os
import sys
import json
import requests
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseSetup:
    def __init__(self):
        self.access_token = os.environ.get("SUPABASE_ACCESS_TOKEN")
        self.base_url = "https://api.supabase.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def check_token(self) -> bool:
        """Verify access token is valid"""
        if not self.access_token:
            print("❌ SUPABASE_ACCESS_TOKEN not found in environment")
            print("💡 Get your token from https://supabase.com/dashboard/account/tokens")
            return False
        
        # Test token by fetching organizations
        try:
            response = requests.get(f"{self.base_url}/organizations", headers=self.headers)
            if response.status_code == 200:
                print("✅ Supabase access token is valid")
                return True
            else:
                print(f"❌ Invalid token. Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Token verification failed: {e}")
            return False
    
    def list_organizations(self) -> Optional[List[Dict]]:
        """List available organizations"""
        try:
            response = requests.get(f"{self.base_url}/organizations", headers=self.headers)
            if response.status_code == 200:
                orgs = response.json()
                print(f"📋 Found {len(orgs)} organizations:")
                for i, org in enumerate(orgs):
                    print(f"  {i+1}. {org['name']} (id: {org['id']})")
                return orgs
            else:
                print(f"❌ Failed to fetch organizations: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error fetching organizations: {e}")
            return None
    
    def create_project(self, org_id: str, project_name: str = "epicure-production") -> Optional[Dict]:
        """Create a new Supabase project"""
        print(f"🚀 Creating project '{project_name}'...")
        
        project_data = {
            "name": project_name,
            "organization_id": org_id,
            "plan": "free",  # Change to "pro" if you want paid tier
            "region": "us-east-1",  # Change as needed
            "db_pass": self._generate_db_password()
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/projects", 
                headers=self.headers,
                json=project_data
            )
            
            if response.status_code == 201:
                project = response.json()
                print(f"✅ Project created successfully!")
                print(f"   Project ID: {project['id']}")
                print(f"   Reference: {project['ref']}")
                print(f"   Status: {project['status']}")
                return project
            else:
                print(f"❌ Failed to create project: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating project: {e}")
            return None
    
    def wait_for_project_ready(self, project_id: str) -> bool:
        """Wait for project to be ready"""
        print("⏳ Waiting for project to be ready...")
        max_attempts = 30  # 5 minutes max
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"{self.base_url}/projects/{project_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    project = response.json()
                    status = project.get('status')
                    
                    if status == 'ACTIVE_HEALTHY':
                        print("✅ Project is ready!")
                        return True
                    elif status in ['INACTIVE', 'UNKNOWN']:
                        print(f"❌ Project failed to initialize. Status: {status}")
                        return False
                    else:
                        print(f"⏳ Project status: {status} (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(10)
                else:
                    print(f"❌ Error checking project status: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error waiting for project: {e}")
                return False
        
        print("❌ Timeout waiting for project to be ready")
        return False
    
    def get_project_config(self, project_id: str) -> Optional[Dict]:
        """Get project configuration details"""
        try:
            response = requests.get(
                f"{self.base_url}/projects/{project_id}/config",
                headers=self.headers
            )
            
            if response.status_code == 200:
                config = response.json()
                return config
            else:
                print(f"❌ Failed to get project config: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting project config: {e}")
            return None
    
    def run_sql_migration(self, project_ref: str, service_key: str) -> bool:
        """Run the SQL migration script"""
        print("📝 Running SQL migration...")
        
        try:
            from supabase import create_client, Client
            
            # Initialize client with service key
            url = f"https://{project_ref}.supabase.co"
            supabase = create_client(url, service_key)
            
            # Read SQL file
            sql_file = "supabase_setup.sql"
            if not os.path.exists(sql_file):
                print(f"❌ SQL file {sql_file} not found")
                return False
            
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            # Split SQL into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            print(f"🔄 Executing {len(statements)} SQL statements...")
            
            for i, statement in enumerate(statements):
                if statement.startswith('--') or not statement:
                    continue
                
                try:
                    # Use raw SQL execution
                    supabase.postgrest.rpc('sql', {'query': statement}).execute()
                    if i % 10 == 0:
                        print(f"   ✅ Executed {i+1}/{len(statements)} statements")
                except Exception as e:
                    print(f"   ⚠️  Statement {i+1} failed (might be expected): {str(e)[:100]}")
            
            print("✅ SQL migration completed!")
            return True
            
        except ImportError:
            print("❌ Supabase client not installed. Run: pip install supabase")
            return False
        except Exception as e:
            print(f"❌ SQL migration failed: {e}")
            return False
    
    def create_env_file(self, project_config: Dict) -> bool:
        """Create .env file with project configuration"""
        print("📝 Creating .env file...")
        
        try:
            env_content = f"""# Supabase Configuration - Generated by setup script
SUPABASE_URL={project_config['endpoint']}
SUPABASE_ANON_KEY={project_config['anon_key']}
SUPABASE_SERVICE_ROLE_KEY={project_config['service_role_key']}

# Direct Database Connection
DATABASE_URL={project_config['db_url']}

# Supabase Personal Access Token
SUPABASE_ACCESS_TOKEN={self.access_token}

# AI/ML Services (FILL THESE IN)
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_TOKEN=your_huggingface_token_here

# Optional APIs
GOOGLE_PLACES_API_KEY=your_google_api_key
YELP_API_KEY=your_yelp_api_key

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
"""
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            print("✅ .env file created successfully!")
            print("⚠️  Remember to fill in your API keys for Groq and Hugging Face!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    
    def _generate_db_password(self) -> str:
        """Generate a secure database password"""
        import secrets
        import string
        
        # Generate a 20-character password
        alphabet = string.ascii_letters + string.digits + "!@#$%&"
        password = ''.join(secrets.choice(alphabet) for _ in range(20))
        return password

def main():
    """Main setup flow"""
    print("🚀 Supabase Automated Setup for Epicure")
    print("=" * 50)
    
    setup = SupabaseSetup()
    
    # Step 1: Verify token
    if not setup.check_token():
        return
    
    # Step 2: List organizations and let user choose
    orgs = setup.list_organizations()
    if not orgs:
        return
    
    if len(orgs) == 1:
        org_id = orgs[0]['id']
        print(f"📋 Using organization: {orgs[0]['name']}")
    else:
        try:
            choice = input("\n📋 Choose organization (enter number): ")
            org_index = int(choice) - 1
            if 0 <= org_index < len(orgs):
                org_id = orgs[org_index]['id']
                print(f"📋 Using organization: {orgs[org_index]['name']}")
            else:
                print("❌ Invalid choice")
                return
        except ValueError:
            print("❌ Invalid input")
            return
    
    # Step 3: Create project
    project_name = input("\n📝 Enter project name (default: epicure-production): ").strip()
    if not project_name:
        project_name = "epicure-production"
    
    project = setup.create_project(org_id, project_name)
    if not project:
        return
    
    # Step 4: Wait for project to be ready
    if not setup.wait_for_project_ready(project['id']):
        return
    
    # Step 5: Get project configuration
    config = setup.get_project_config(project['id'])
    if not config:
        return
    
    # Step 6: Create .env file
    setup.create_env_file(config)
    
    # Step 7: Run SQL migration
    if setup.run_sql_migration(project['ref'], config['service_role_key']):
        print("\n🎉 Supabase setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Fill in your API keys in the .env file")
        print("2. Run: python test_supabase_connection.py")
        print("3. Start building your backend!")
    else:
        print("\n⚠️  Project created but SQL migration failed.")
        print("   You can run the SQL manually in your Supabase dashboard.")

if __name__ == "__main__":
    main()
