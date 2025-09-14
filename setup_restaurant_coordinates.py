#!/usr/bin/env python3
"""
Setup restaurant coordinates in Supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Get Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Supabase credentials not found in environment variables")
        return None
    
    return create_client(url, key)

def setup_coordinates():
    """Add latitude and longitude columns to restaurants table"""
    supabase = get_supabase_client()
    if not supabase:
        return
    
    print("🔧 Adding latitude and longitude columns to restaurants table...")
    
    # Read and execute the SQL file
    with open('add_coordinates_to_supabase.sql', 'r') as f:
        sql_content = f.read()
    
    try:
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
        print("✅ Successfully added latitude and longitude columns")
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        # Try alternative approach - direct table operations
        print("🔄 Trying alternative approach...")
        
        # Check if columns exist
        try:
            result = supabase.table("restaurants").select("latitude, longitude").limit(1).execute()
            print("✅ Latitude and longitude columns already exist")
        except Exception as e2:
            print(f"❌ Columns don't exist and couldn't be created: {e2}")
            return

if __name__ == "__main__":
    setup_coordinates()
