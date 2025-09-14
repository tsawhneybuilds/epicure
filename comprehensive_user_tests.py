#!/usr/bin/env python3
"""
Comprehensive test suite for user creation, login, and Supabase integration
Tests all user-related endpoints and database operations
"""

import requests
import json
import uuid
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_TIMEOUT = 30

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.start_time = datetime.now()
    
    def add_result(self, test_name: str, success: bool, error: str = None):
        if success:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            print(f"❌ {test_name}")
            if error:
                print(f"   Error: {error}")
                self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "0%")
        print(f"Duration: {duration:.2f}s")
        
        if self.errors:
            print(f"\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        return self.failed == 0

class UserTestSuite:
    def __init__(self):
        self.results = TestResults()
        self.test_users = []  # Store created users for cleanup
        self.auth_tokens = {}  # Store auth tokens by user_id
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Tuple[bool, Dict, int]:
        """Make HTTP request and return success, response data, and status code"""
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=TEST_TIMEOUT
            )
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            return response.ok, response_data, response.status_code
            
        except requests.exceptions.Timeout:
            return False, {"error": "Request timeout"}, 408
        except requests.exceptions.ConnectionError:
            return False, {"error": "Connection failed - is the server running?"}, 503
        except Exception as e:
            return False, {"error": str(e)}, 500
    
    def test_server_health(self) -> bool:
        """Test if the server is running and accessible"""
        print("\n🔍 Testing server health...")
        
        success, data, status = self.make_request("GET", "/health")
        
        if success:
            self.results.add_result("Server Health Check", True)
            return True
        else:
            self.results.add_result("Server Health Check", False, f"Status {status}: {data}")
            return False
    
    def test_user_creation_basic(self) -> bool:
        """Test basic user creation with email"""
        print("\n🧪 Testing basic user creation...")
        
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        payload = {"email": test_email}
        
        success, data, status = self.make_request("POST", "/users/create", payload)
        
        if success and "user_id" in data and "auth_token" in data:
            user_id = data["user_id"]
            auth_token = data["auth_token"]
            self.test_users.append(user_id)
            self.auth_tokens[user_id] = auth_token
            
            # Validate UUID format
            try:
                uuid.UUID(user_id)
                self.results.add_result("Basic User Creation", True)
                return True
            except ValueError:
                self.results.add_result("Basic User Creation", False, "Invalid user_id format")
                return False
        else:
            self.results.add_result("Basic User Creation", False, f"Status {status}: {data}")
            return False
    
    def test_user_creation_apple_id(self) -> bool:
        """Test user creation with Apple ID"""
        print("\n🧪 Testing user creation with Apple ID...")
        
        apple_id = f"apple_{uuid.uuid4().hex[:8]}@icloud.com"
        payload = {"apple_id": apple_id}
        
        success, data, status = self.make_request("POST", "/users/create", payload)
        
        if success and "user_id" in data and "auth_token" in data:
            user_id = data["user_id"]
            auth_token = data["auth_token"]
            self.test_users.append(user_id)
            self.auth_tokens[user_id] = auth_token
            
            self.results.add_result("Apple ID User Creation", True)
            return True
        else:
            self.results.add_result("Apple ID User Creation", False, f"Status {status}: {data}")
            return False
    
    def test_duplicate_user_creation(self) -> bool:
        """Test that duplicate user creation fails appropriately"""
        print("\n🧪 Testing duplicate user creation...")
        
        test_email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
        payload = {"email": test_email}
        
        # Create first user
        success1, data1, status1 = self.make_request("POST", "/users/create", payload)
        
        if not success1:
            self.results.add_result("Duplicate User Creation", False, f"First creation failed: {data1}")
            return False
        
        user_id = data1["user_id"]
        self.test_users.append(user_id)
        self.auth_tokens[user_id] = data1["auth_token"]
        
        # Try to create duplicate
        success2, data2, status2 = self.make_request("POST", "/users/create", payload)
        
        if not success2 and status2 == 400:
            self.results.add_result("Duplicate User Creation", True)
            return True
        else:
            self.results.add_result("Duplicate User Creation", False, f"Expected 400, got {status2}: {data2}")
            return False
    
    def test_user_login_email(self) -> bool:
        """Test user login with email"""
        print("\n🧪 Testing user login with email...")
        
        # First create a user
        test_email = f"login_{uuid.uuid4().hex[:8]}@example.com"
        create_payload = {"email": test_email}
        
        success, data, status = self.make_request("POST", "/users/create", create_payload)
        
        if not success:
            self.results.add_result("User Login (Email)", False, f"User creation failed: {data}")
            return False
        
        user_id = data["user_id"]
        self.test_users.append(user_id)
        
        # Now test login
        login_payload = {"email": test_email}
        success, data, status = self.make_request("POST", "/users/login", login_payload)
        
        if success and "user_id" in data and "auth_token" in data:
            if data["user_id"] == user_id:
                self.results.add_result("User Login (Email)", True)
                return True
            else:
                self.results.add_result("User Login (Email)", False, "User ID mismatch")
                return False
        else:
            self.results.add_result("User Login (Email)", False, f"Status {status}: {data}")
            return False
    
    def test_user_login_apple_id(self) -> bool:
        """Test user login with Apple ID"""
        print("\n🧪 Testing user login with Apple ID...")
        
        # First create a user
        apple_id = f"login_apple_{uuid.uuid4().hex[:8]}@icloud.com"
        create_payload = {"apple_id": apple_id}
        
        success, data, status = self.make_request("POST", "/users/create", create_payload)
        
        if not success:
            self.results.add_result("User Login (Apple ID)", False, f"User creation failed: {data}")
            return False
        
        user_id = data["user_id"]
        self.test_users.append(user_id)
        
        # Now test login
        login_payload = {"apple_id": apple_id}
        success, data, status = self.make_request("POST", "/users/login", login_payload)
        
        if success and "user_id" in data and "auth_token" in data:
            if data["user_id"] == user_id:
                self.results.add_result("User Login (Apple ID)", True)
                return True
            else:
                self.results.add_result("User Login (Apple ID)", False, "User ID mismatch")
                return False
        else:
            self.results.add_result("User Login (Apple ID)", False, f"Status {status}: {data}")
            return False
    
    def test_invalid_login(self) -> bool:
        """Test login with non-existent user"""
        print("\n🧪 Testing invalid login...")
        
        fake_email = f"nonexistent_{uuid.uuid4().hex[:8]}@example.com"
        payload = {"email": fake_email}
        
        success, data, status = self.make_request("POST", "/users/login", payload)
        
        if not success and status == 404:
            self.results.add_result("Invalid Login", True)
            return True
        else:
            self.results.add_result("Invalid Login", False, f"Expected 404, got {status}: {data}")
            return False
    
    def test_profile_operations(self) -> bool:
        """Test complete profile CRUD operations"""
        print("\n🧪 Testing profile operations...")
        
        # Create a user first
        test_email = f"profile_{uuid.uuid4().hex[:8]}@example.com"
        create_payload = {"email": test_email}
        
        success, data, status = self.make_request("POST", "/users/create", create_payload)
        
        if not success:
            self.results.add_result("Profile Operations", False, f"User creation failed: {data}")
            return False
        
        user_id = data["user_id"]
        auth_token = data["auth_token"]
        self.test_users.append(user_id)
        self.auth_tokens[user_id] = auth_token
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test 1: Get empty profile
        success, data, status = self.make_request("GET", f"/users/{user_id}/profile", headers=headers)
        
        if not success:
            self.results.add_result("Profile Operations - Get", False, f"Status {status}: {data}")
            return False
        
        # Test 2: Update profile
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
        
        success, data, status = self.make_request("PUT", f"/users/{user_id}/profile", update_payload, headers)
        
        if not success:
            self.results.add_result("Profile Operations - Update", False, f"Status {status}: {data}")
            return False
        
        # Test 3: Get updated profile
        success, data, status = self.make_request("GET", f"/users/{user_id}/profile", headers=headers)
        
        if not success:
            self.results.add_result("Profile Operations - Get Updated", False, f"Status {status}: {data}")
            return False
        
        # Test 4: Update preferences
        preferences_payload = {
            "preferences": {
                "budgetFriendly": True,
                "healthPriority": "high",
                "quickService": False,
                "spiceTolerance": "medium"
            }
        }
        
        success, data, status = self.make_request("PATCH", f"/users/{user_id}/preferences", preferences_payload, headers)
        
        if not success:
            self.results.add_result("Profile Operations - Preferences", False, f"Status {status}: {data}")
            return False
        
        self.results.add_result("Profile Operations", True)
        return True
    
    def test_interaction_operations(self) -> bool:
        """Test user interaction operations"""
        print("\n🧪 Testing interaction operations...")
        
        # Create a user first
        test_email = f"interaction_{uuid.uuid4().hex[:8]}@example.com"
        create_payload = {"email": test_email}
        
        success, data, status = self.make_request("POST", "/users/create", create_payload)
        
        if not success:
            self.results.add_result("Interaction Operations", False, f"User creation failed: {data}")
            return False
        
        user_id = data["user_id"]
        auth_token = data["auth_token"]
        self.test_users.append(user_id)
        self.auth_tokens[user_id] = auth_token
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test 1: Record swipe interaction
        # Get a real restaurant ID from the database
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
            from app.core.supabase import get_supabase_client
            
            supabase_client = get_supabase_client()
            restaurants_result = supabase_client.table('restaurants').select('id, name').limit(1).execute()
            
            if restaurants_result.data and len(restaurants_result.data) > 0:
                real_restaurant_id = restaurants_result.data[0]['id']
                restaurant_name = restaurants_result.data[0]['name']
                print(f"Using real restaurant: {real_restaurant_id} ({restaurant_name})")
            else:
                # Fallback to test restaurant if no real restaurants exist
                real_restaurant_id = "00000000-0000-0000-0000-000000000000"
                print("No real restaurants found, using test restaurant ID")
        except Exception as e:
            # Fallback to test restaurant if there's any error
            real_restaurant_id = "00000000-0000-0000-0000-000000000000"
            print(f"Error getting restaurant ID: {e}, using test restaurant ID")
        
        # Test record swipe with real restaurant ID
        swipe_payload = {
            "restaurant_id": real_restaurant_id,
            "action": "like",
            "context": {
                "search_query": "healthy food",
                "position": 1,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        success, data, status = self.make_request("POST", f"/users/{user_id}/interactions/swipe", swipe_payload, headers)
        
        if not success:
            self.results.add_result("Interaction Operations - Swipe", False, f"Status {status}: {data}")
            return False
        
        # Test 2: Record another interaction
        swipe_payload2 = {
            "restaurant_id": real_restaurant_id,  # Use the same restaurant ID
            "action": "dislike",
            "context": {
                "search_query": "fast food",
                "position": 2
            }
        }
        
        success, data, status = self.make_request("POST", f"/users/{user_id}/interactions/swipe", swipe_payload2, headers)
        
        if not success:
            self.results.add_result("Interaction Operations - Multiple Swipes", False, f"Status {status}: {data}")
            return False
        
        # Test 3: Get user stats
        success, data, status = self.make_request("GET", f"/users/{user_id}/stats", headers=headers)
        
        if not success:
            self.results.add_result("Interaction Operations - Stats", False, f"Status {status}: {data}")
            return False
        
        # Verify stats make sense
        if "likes" in data and "dislikes" in data and "total_interactions" in data:
            if data["likes"] >= 1 and data["dislikes"] >= 1:
                self.results.add_result("Interaction Operations", True)
                return True
            else:
                self.results.add_result("Interaction Operations", False, f"Unexpected stats: {data}")
                return False
        else:
            self.results.add_result("Interaction Operations", False, f"Missing stats fields: {data}")
            return False
    
    def test_authentication_security(self) -> bool:
        """Test authentication and authorization security"""
        print("\n🧪 Testing authentication security...")
        
        # Create a user
        test_email = f"security_{uuid.uuid4().hex[:8]}@example.com"
        create_payload = {"email": test_email}
        
        success, data, status = self.make_request("POST", "/users/create", create_payload)
        
        if not success:
            self.results.add_result("Authentication Security", False, f"User creation failed: {data}")
            return False
        
        user_id = data["user_id"]
        auth_token = data["auth_token"]
        self.test_users.append(user_id)
        self.auth_tokens[user_id] = auth_token
        
        # Test 1: Access profile without auth token
        success, data, status = self.make_request("GET", f"/users/{user_id}/profile")
        
        if not success and status == 401:
            self.results.add_result("Security - No Auth Token", True)
        else:
            self.results.add_result("Security - No Auth Token", False, f"Expected 401, got {status}: {data}")
            return False
        
        # Test 2: Access profile with invalid auth token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        success, data, status = self.make_request("GET", f"/users/{user_id}/profile", headers=invalid_headers)
        
        if not success and status == 401:
            self.results.add_result("Security - Invalid Auth Token", True)
        else:
            self.results.add_result("Security - Invalid Auth Token", False, f"Expected 401, got {status}: {data}")
            return False
        
        # Test 3: Access another user's profile
        other_user_id = str(uuid.uuid4())
        valid_headers = {"Authorization": f"Bearer {auth_token}"}
        success, data, status = self.make_request("GET", f"/users/{other_user_id}/profile", headers=valid_headers)
        
        if not success and status == 403:
            self.results.add_result("Security - Cross-User Access", True)
        else:
            self.results.add_result("Security - Cross-User Access", False, f"Expected 403, got {status}: {data}")
            return False
        
        self.results.add_result("Authentication Security", True)
        return True
    
    def test_edge_cases(self) -> bool:
        """Test edge cases and error handling"""
        print("\n🧪 Testing edge cases...")
        
        # Test 1: Empty email
        payload = {"email": ""}
        success, data, status = self.make_request("POST", "/users/create", payload)
        
        if not success:
            self.results.add_result("Edge Cases - Empty Email", True)
        else:
            self.results.add_result("Edge Cases - Empty Email", False, f"Should fail but got {status}: {data}")
            return False
        
        # Test 2: Invalid email format
        payload = {"email": "not-an-email"}
        success, data, status = self.make_request("POST", "/users/create", payload)
        
        if not success:
            self.results.add_result("Edge Cases - Invalid Email", True)
        else:
            self.results.add_result("Edge Cases - Invalid Email", False, f"Should fail but got {status}: {data}")
            return False
        
        # Test 3: Missing required fields
        payload = {}
        success, data, status = self.make_request("POST", "/users/create", payload)
        
        if not success:
            self.results.add_result("Edge Cases - Missing Fields", True)
        else:
            self.results.add_result("Edge Cases - Missing Fields", False, f"Should fail but got {status}: {data}")
            return False
        
        # Test 4: Very long email
        long_email = "a" * 300 + "@example.com"
        payload = {"email": long_email}
        success, data, status = self.make_request("POST", "/users/create", payload)
        
        if not success:
            self.results.add_result("Edge Cases - Long Email", True)
        else:
            self.results.add_result("Edge Cases - Long Email", False, f"Should fail but got {status}: {data}")
            return False
        
        self.results.add_result("Edge Cases", True)
        return True
    
    def cleanup_test_users(self):
        """Clean up test users from database"""
        print("\n🧹 Cleaning up test users...")
        
        if not self.test_users:
            print("No test users to clean up")
            return
        
        # Note: In a real test environment, you might want to clean up the database
        # For now, we'll just log the users that were created
        print(f"Created {len(self.test_users)} test users:")
        for user_id in self.test_users:
            print(f"  - {user_id}")
        
        print("Note: Test users are not automatically cleaned up.")
        print("In production, implement proper test data cleanup.")
    
    def run_all_tests(self) -> bool:
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive User Tests")
        print("=" * 60)
        
        # Check server health first
        if not self.test_server_health():
            print("\n❌ Server is not accessible. Please start the backend server first.")
            print("Run: cd backend && python main.py")
            return False
        
        # Run all test suites
        test_methods = [
            self.test_user_creation_basic,
            self.test_user_creation_apple_id,
            self.test_duplicate_user_creation,
            self.test_user_login_email,
            self.test_user_login_apple_id,
            self.test_invalid_login,
            self.test_profile_operations,
            self.test_interaction_operations,
            self.test_authentication_security,
            self.test_edge_cases
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                test_name = test_method.__name__.replace("test_", "").replace("_", " ").title()
                self.results.add_result(test_name, False, f"Test exception: {str(e)}")
        
        # Cleanup
        self.cleanup_test_users()
        
        # Show results
        return self.results.summary()

def main():
    """Main test runner"""
    print("🧪 Comprehensive User Creation & Login Test Suite")
    print("Testing real Supabase integration with database operations")
    print("=" * 60)
    
    test_suite = UserTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! User system is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
