#!/usr/bin/env python3
"""
Run SQL setup for Supabase database
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def run_sql_setup():
    """Run the SQL setup script"""
    
    print("🚀 Setting up Supabase Database Schema")
    print("=" * 50)
    
    # Get connection details
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    print(f"🔗 Connecting to: {url}")
    
    try:
        # Initialize client
        supabase = create_client(url, key)
        
        # Read SQL file
        sql_file = "supabase_setup.sql"
        if not os.path.exists(sql_file):
            print(f"❌ SQL file {sql_file} not found")
            return False
        
        print("📂 Reading SQL setup file...")
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Split into statements (simple approach)
        statements = []
        current_statement = ""
        
        for line in sql_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            
            current_statement += line + "\n"
            
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        print(f"🔄 Found {len(statements)} SQL statements to execute")
        
        # Execute statements one by one
        success_count = 0
        for i, statement in enumerate(statements):
            if not statement or statement.isspace():
                continue
                
            try:
                # Use direct SQL execution
                result = supabase.postgrest.rpc('query', {'sql': statement}).execute()
                success_count += 1
                
                if i % 5 == 0:
                    print(f"   ✅ Executed {success_count} statements...")
                    
            except Exception as e:
                error_msg = str(e)
                # Some errors are expected (like "already exists")
                if any(phrase in error_msg.lower() for phrase in ['already exists', 'duplicate', 'does not exist']):
                    print(f"   ⚠️  Statement {i+1}: {error_msg[:60]}... (expected)")
                else:
                    print(f"   ❌ Statement {i+1} failed: {error_msg[:100]}...")
        
        print(f"\n✅ SQL setup completed! {success_count} statements executed successfully")
        print("\n📋 Next steps:")
        print("1. Run: python3 test_supabase_connection.py")
        print("2. Your database is ready for the Epicure app!")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    run_sql_setup()
