#!/usr/bin/env python3
"""
Manual configuration setup for Supabase
Use this when the project is still initializing
"""

import os

def setup_manual_config():
    """Setup configuration manually"""
    
    print("🔧 Manual Supabase Configuration Setup")
    print("=" * 50)
    print("Since your project is still initializing, let's set it up manually.")
    print("\n📋 Please go to your Supabase dashboard and get the following:")
    print("   https://supabase.com/dashboard/project/[your-project-id]")
    print("\n🔑 From Settings > API, you'll need:")
    print("   1. Project URL")
    print("   2. Anon/Public Key") 
    print("   3. Service Role Key")
    print("\n📊 From Settings > Database, you'll need:")
    print("   4. Database URL")
    
    # Get user inputs
    print("\n" + "="*50)
    project_url = input("🌐 Enter your Project URL (https://xxxxx.supabase.co): ").strip()
    if not project_url.startswith('https://'):
        project_url = f"https://{project_url}"
    if not project_url.endswith('.supabase.co'):
        project_url = f"{project_url}.supabase.co"
    
    anon_key = input("\n🔑 Enter your Anon Key (eyJ...): ").strip()
    service_key = input("\n🔐 Enter your Service Role Key (eyJ...): ").strip()
    
    db_url = input("\n🗄️  Enter your Database URL (postgresql://...): ").strip()
    if not db_url:
        # Try to construct it from project URL
        ref = project_url.replace('https://', '').replace('.supabase.co', '')
        db_url = f"postgresql://postgres:[YOUR-PASSWORD]@db.{ref}.supabase.co:5432/postgres"
        print(f"💡 Using constructed URL: {db_url}")
        print("⚠️  Remember to replace [YOUR-PASSWORD] with your actual database password!")
    
    # Update .env file
    print("\n📝 Updating .env file...")
    update_env_manual(project_url, anon_key, service_key, db_url)
    
    print("\n✅ Configuration updated successfully!")
    print("\n📋 Next steps:")
    print("1. Replace [YOUR-PASSWORD] in DATABASE_URL with your actual password")
    print("2. Add your other API keys (Groq, Hugging Face)")
    print("3. Run: python3 -c 'import setup_supabase; setup_supabase.run_sql_migration_manual()'")
    print("4. Run: python3 test_supabase_connection.py")

def update_env_manual(project_url, anon_key, service_key, db_url):
    """Update .env file with manual configuration"""
    
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
                updated_lines.append(f'SUPABASE_URL={project_url}\n')
            elif line.startswith('SUPABASE_ANON_KEY='):
                updated_lines.append(f'SUPABASE_ANON_KEY={anon_key}\n')
            elif line.startswith('SUPABASE_SERVICE_ROLE_KEY='):
                updated_lines.append(f'SUPABASE_SERVICE_ROLE_KEY={service_key}\n')
            elif line.startswith('DATABASE_URL='):
                updated_lines.append(f'DATABASE_URL={db_url}\n')
            else:
                updated_lines.append(line)
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ .env file updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

if __name__ == "__main__":
    setup_manual_config()
