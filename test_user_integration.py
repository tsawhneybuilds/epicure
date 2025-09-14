#!/usr/bin/env python3
"""
Test script to verify user profile and authentication integration
"""

import requests
import json
import uuid

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def test_user_creation():
    """Test user creation endpoint"""
    print("🧪 Testing user creation...")
    
    # Test data
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    payload = {
        "email": test_email
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/users/create", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User created successfully: {data['user_id']}")
            return data['user_id'], data['auth_token']
        else:
            print(f"❌ User creation failed: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None, None

def test_user_login():
    """Test user login endpoint"""
    print("🧪 Testing user login...")
    
    # First create a user
    user_id, auth_token = test_user_creation()
    if not user_id:
        return None, None
    
    # Test login with the same email
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    # Create user first
    create_payload = {"email": test_email}
    create_response = requests.post(f"{API_BASE_URL}/users/create", json=create_payload)
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create user for login test: {create_response.text}")
        return None, None
    
    # Now test login
    login_payload = {"email": test_email}
    
    try:
        response = requests.post(f"{API_BASE_URL}/users/login", json=login_payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful: {data['user_id']}")
            return data['user_id'], data['auth_token']
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None, None

def test_user_profile_operations(user_id, auth_token):
    """Test user profile CRUD operations"""
    print("🧪 Testing user profile operations...")
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Test get profile (should return empty profile)
    try:
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/profile", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile retrieved: {data['profile']}")
        else:
            print(f"❌ Profile retrieval failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile retrieval error: {e}")
        return False
    
    # Test update profile
    update_payload = {
        "age": 28,
        "height_cm": 175,
        "weight_kg": 70.5,
        "gender": "male",
        "activity_level": "moderate",
        "goals": ["Track macros", "Muscle gain"],
        "dietary_restrictions": ["vegetarian"],
        "allergies": ["nuts"]
    }
    
    try:
        response = requests.put(f"{API_BASE_URL}/users/{user_id}/profile", 
                              json=update_payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile updated: {data['updated_fields']}")
        else:
            print(f"❌ Profile update failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile update error: {e}")
        return False
    
    # Test update preferences
    preferences_payload = {
        "preferences": {
            "budgetFriendly": True,
            "healthPriority": "high",
            "quickService": False
        }
    }
    
    try:
        response = requests.patch(f"{API_BASE_URL}/users/{user_id}/preferences", 
                                json=preferences_payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Preferences updated: {data['preferences']}")
        else:
            print(f"❌ Preferences update failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Preferences update error: {e}")
        return False
    
    return True

def test_user_interactions(user_id, auth_token):
    """Test user interaction endpoints"""
    print("🧪 Testing user interactions...")
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Test record swipe
    swipe_payload = {
        "restaurant_id": str(uuid.uuid4()),
        "action": "like",
        "context": {"search_query": "healthy food", "position": 1}
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/users/{user_id}/interactions/swipe", 
                               json=swipe_payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Swipe recorded: {data['interaction_id']}")
        else:
            print(f"❌ Swipe recording failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Swipe recording error: {e}")
        return False
    
    # Test get user stats
    try:
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/stats", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User stats retrieved: {data}")
        else:
            print(f"❌ User stats failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User stats error: {e}")
        return False
    
    return True

def test_authentication_security():
    """Test authentication security"""
    print("🧪 Testing authentication security...")
    
    # Test accessing profile without auth token
    try:
        response = requests.get(f"{API_BASE_URL}/users/{uuid.uuid4()}/profile")
        
        if response.status_code == 401:
            print("✅ Unauthorized access properly blocked")
        else:
            print(f"❌ Security issue: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Security test error: {e}")
        return False
    
    # Test accessing another user's profile
    user_id, auth_token = test_user_creation()
    if not user_id:
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Try to access a different user's profile
        other_user_id = str(uuid.uuid4())
        response = requests.get(f"{API_BASE_URL}/users/{other_user_id}/profile", headers=headers)
        
        if response.status_code == 403:
            print("✅ Cross-user access properly blocked")
        else:
            print(f"❌ Security issue: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Security test error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting user profile and authentication integration tests...\n")
    
    # Test 1: User creation
    user_id, auth_token = test_user_creation()
    if not user_id:
        print("❌ User creation test failed. Stopping tests.")
        return
    
    print()
    
    # Test 2: User login
    login_user_id, login_auth_token = test_user_login()
    if not login_user_id:
        print("❌ User login test failed.")
    else:
        print()
    
    # Test 3: Profile operations
    if test_user_profile_operations(user_id, auth_token):
        print("✅ Profile operations test passed")
    else:
        print("❌ Profile operations test failed")
    
    print()
    
    # Test 4: User interactions
    if test_user_interactions(user_id, auth_token):
        print("✅ User interactions test passed")
    else:
        print("❌ User interactions test failed")
    
    print()
    
    # Test 5: Authentication security
    if test_authentication_security():
        print("✅ Authentication security test passed")
    else:
        print("❌ Authentication security test failed")
    
    print("\n🎉 Integration tests completed!")

if __name__ == "__main__":
    main()
