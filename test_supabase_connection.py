#!/usr/bin/env python3
"""
Test script for Supabase connection and setup verification
"""

import os
import sys
import json
import numpy as np
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase client not installed. Run: pip install supabase")
    sys.exit(1)

def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        print("📝 Make sure to copy env.template to .env and fill in your values")
        sys.exit(1)
    
    return create_client(url, key)

def test_basic_connection(supabase: Client) -> bool:
    """Test basic connection to Supabase"""
    try:
        # Try a simple query to check connection
        response = supabase.table('restaurants').select("count", count="exact").execute()
        print(f"✅ Basic connection successful! Found {response.count} restaurants")
        return True
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
        return False

def test_extensions(supabase: Client) -> bool:
    """Test that required extensions are enabled"""
    try:
        # Test vector extension
        supabase.rpc('pg_available_extensions').execute()
        print("✅ Database extensions accessible")
        return True
    except Exception as e:
        print(f"❌ Extensions test failed: {e}")
        return False

def test_vector_operations(supabase: Client) -> bool:
    """Test vector operations"""
    try:
        # Create a test restaurant first
        test_restaurant = {
            'name': 'Test Restaurant',
            'cuisine': 'Test Cuisine',
            'description': 'A test restaurant for vector operations',
            'description_embedding': np.random.rand(384).tolist()
        }
        
        restaurant_response = supabase.table('restaurants').insert(test_restaurant).execute()
        restaurant_id = restaurant_response.data[0]['id']
        print(f"✅ Created test restaurant: {restaurant_id}")
        
        # Test menu item vector insertion
        test_embedding = np.random.rand(384).tolist()
        test_item = {
            'name': 'Test Menu Item',
            'description': 'A delicious test item',
            'restaurant_id': restaurant_id,
            'embedding': test_embedding,
            'price': 12.99,
            'calories': 350
        }
        
        item_response = supabase.table('menu_items').insert(test_item).execute()
        item_id = item_response.data[0]['id']
        print(f"✅ Vector insertion successful! Item ID: {item_id}")
        
        # Test vector similarity search
        search_vector = np.random.rand(384).tolist()
        search_response = supabase.rpc('match_menu_items', {
            'query_embedding': search_vector,
            'match_threshold': 0.0,  # Low threshold for test
            'match_count': 5
        }).execute()
        
        print(f"✅ Vector search successful! Found {len(search_response.data)} similar items")
        
        # Clean up test data
        supabase.table('menu_items').delete().eq('id', item_id).execute()
        supabase.table('restaurants').delete().eq('id', restaurant_id).execute()
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector operations failed: {e}")
        return False

def test_geographic_operations(supabase: Client) -> bool:
    """Test geographic queries"""
    try:
        # Test nearby restaurants function
        response = supabase.rpc('nearby_restaurants', {
            'user_lat': 40.7128,  # NYC coordinates
            'user_lng': -74.0060,
            'radius_meters': 1000,
            'limit_count': 10
        }).execute()
        
        print(f"✅ Geographic search successful! Found {len(response.data)} nearby restaurants")
        return True
        
    except Exception as e:
        print(f"❌ Geographic operations failed: {e}")
        return False

def test_user_operations(supabase: Client) -> bool:
    """Test user-related operations"""
    try:
        # Create test user
        test_user = {
            'email': 'test@epicure.com',
            'apple_id': 'test_apple_id'
        }
        
        user_response = supabase.table('users').insert(test_user).execute()
        user_id = user_response.data[0]['id']
        print(f"✅ Created test user: {user_id}")
        
        # Create test profile
        test_profile = {
            'user_id': user_id,
            'age': 25,
            'dietary_restrictions': ['vegetarian'],
            'budget_usd_per_meal': 25.00,
            'profile_extensions': {'test_field': 'test_value'}
        }
        
        profile_response = supabase.table('user_profiles').insert(test_profile).execute()
        print("✅ User profile creation successful")
        
        # Test chat message
        test_message = {
            'user_id': user_id,
            'role': 'user',
            'content': 'I want something healthy for lunch',
            'metadata': {'intent': 'food_recommendation'}
        }
        
        message_response = supabase.table('chat_messages').insert(test_message).execute()
        print("✅ Chat message storage successful")
        
        # Clean up
        supabase.table('chat_messages').delete().eq('user_id', user_id).execute()
        supabase.table('user_profiles').delete().eq('user_id', user_id).execute()
        supabase.table('users').delete().eq('id', user_id).execute()
        print("✅ User test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ User operations failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Supabase Setup for Epicure")
    print("=" * 50)
    
    # Initialize client
    try:
        supabase = get_supabase_client()
    except SystemExit:
        return
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Extensions", test_extensions),
        ("Vector Operations", test_vector_operations),
        ("Geographic Operations", test_geographic_operations),
        ("User Operations", test_user_operations)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            success = test_func(supabase)
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your Supabase setup is ready for Epicure!")
    else:
        print("⚠️  Some tests failed. Check the errors above and your setup.")
        print("💡 Make sure you've run the SQL setup script in your Supabase dashboard.")

if __name__ == "__main__":
    main()
