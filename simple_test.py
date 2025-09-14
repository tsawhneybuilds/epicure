#!/usr/bin/env python3
"""
Simple Supabase connection test
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_connection():
    """Test basic Supabase connection"""
    
    print("🧪 Testing Supabase Connection")
    print("=" * 40)
    
    # Get connection details
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"URL: {url}")
    print(f"Key: {key[:20]}..." if key else "Key: None")
    
    if not url or not key:
        print("❌ Missing environment variables")
        return False
    
    try:
        # Initialize client
        supabase = create_client(url, key)
        print("✅ Client created successfully")
        
        # Test basic query
        result = supabase.table('information_schema.tables').select('table_name').limit(5).execute()
        print(f"✅ Database query successful! Found {len(result.data)} tables")
        
        for table in result.data:
            print(f"   - {table['table_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
