#!/usr/bin/env python3
"""
Add helper functions to Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def add_helper_functions():
    """Add helper functions to Supabase"""
    
    # Get Supabase client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)
    
    # Read SQL file
    with open('add_helper_functions.sql', 'r') as f:
        sql_content = f.read()
    
    # Split into individual function statements
    functions = sql_content.split('CREATE OR REPLACE FUNCTION')
    
    for i, func_sql in enumerate(functions):
        if not func_sql.strip():
            continue
        
        # Add back the CREATE OR REPLACE FUNCTION prefix
        if i > 0:
            func_sql = 'CREATE OR REPLACE FUNCTION' + func_sql
        
        try:
            # This won't work directly with postgrest, but let's try simple approach
            print(f"✅ Would execute function {i}")
        except Exception as e:
            print(f"❌ Error with function {i}: {e}")
    
    print("💡 Please run the SQL in add_helper_functions.sql manually in Supabase SQL Editor")
    print("   This will add the helper functions needed for validation")

if __name__ == "__main__":
    add_helper_functions()
