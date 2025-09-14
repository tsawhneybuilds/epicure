#!/usr/bin/env python3
"""
Supabase Integration Test Suite
Tests direct database operations and verifies data integrity
"""

import os
import sys
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)

from app.core.supabase import get_supabase_client
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseTestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.start_time = datetime.now()
        self.test_data = {}  # Store test data for cleanup
    
    def add_result(self, test_name: str, success: bool, error: str = None, test_data: Dict = None):
        if success:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            print(f"❌ {test_name}")
            if error:
                print(f"   Error: {error}")
                self.errors.append(f"{test_name}: {error}")
        
        if test_data:
            self.test_data[test_name] = test_data
    
    def summary(self):
        total = self.passed + self.failed
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"\n{'='*60}")
        print(f"SUPABASE TEST SUMMARY")
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

class SupabaseIntegrationTest:
    def __init__(self):
        self.results = SupabaseTestResults()
        self.client = None
        self.test_users = []
        self.test_profiles = []
        self.test_interactions = []
    
    def setup_client(self) -> bool:
        """Initialize Supabase client"""
        print("\n🔧 Setting up Supabase client...")
        
        try:
            # Check configuration
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                self.results.add_result("Client Setup", False, "Missing Supabase configuration")
                return False
            
            self.client = get_supabase_client()
            
            # Test connection
            result = self.client.table('users').select('id').limit(1).execute()
            
            self.results.add_result("Client Setup", True)
            return True
            
        except Exception as e:
            self.results.add_result("Client Setup", False, str(e))
            return False
    
    def test_user_table_operations(self) -> bool:
        """Test basic user table operations"""
        print("\n🧪 Testing user table operations...")
        
        try:
            # Test 1: Create user
            test_user_id = str(uuid.uuid4())
            test_email = f"db_test_{uuid.uuid4().hex[:8]}@example.com"
            
            user_data = {
                "id": test_user_id,
                "email": test_email,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table('users').insert(user_data).execute()
            
            if not result.data:
                self.results.add_result("User Table - Create", False, "No data returned from insert")
                return False
            
            self.test_users.append(test_user_id)
            
            # Test 2: Read user
            read_result = self.client.table('users').select('*').eq('id', test_user_id).execute()
            
            if not read_result.data or len(read_result.data) != 1:
                self.results.add_result("User Table - Read", False, "User not found or multiple results")
                return False
            
            if read_result.data[0]['email'] != test_email:
                self.results.add_result("User Table - Read", False, "Email mismatch")
                return False
            
            # Test 3: Update user
            update_data = {"updated_at": datetime.now().isoformat()}
            update_result = self.client.table('users').update(update_data).eq('id', test_user_id).execute()
            
            if not update_result.data:
                self.results.add_result("User Table - Update", False, "Update failed")
                return False
            
            # Test 4: Query by email
            email_result = self.client.table('users').select('*').eq('email', test_email).execute()
            
            if not email_result.data or len(email_result.data) != 1:
                self.results.add_result("User Table - Query by Email", False, "Email query failed")
                return False
            
            self.results.add_result("User Table Operations", True, test_data={"user_id": test_user_id})
            return True
            
        except Exception as e:
            self.results.add_result("User Table Operations", False, str(e))
            return False
    
    def test_user_profile_operations(self) -> bool:
        """Test user profile table operations"""
        print("\n🧪 Testing user profile operations...")
        
        try:
            # Create a user first
            test_user_id = str(uuid.uuid4())
            test_email = f"profile_test_{uuid.uuid4().hex[:8]}@example.com"
            
            user_data = {
                "id": test_user_id,
                "email": test_email
            }
            
            self.client.table('users').insert(user_data).execute()
            self.test_users.append(test_user_id)
            
            # Test 1: Create profile
            profile_data = {
                "user_id": test_user_id,
                "age": 25,
                "height_cm": 170,
                "weight_kg": 65.0,
                "gender": "female",
                "activity_level": "moderate",
                "goals": ["weight_loss", "muscle_tone"],
                "dietary_restrictions": ["vegetarian"],
                "allergies": ["nuts"],
                "budget_usd_per_meal": 15.0,
                "max_walk_time_minutes": 10,
                "profile_extensions": {
                    "budgetFriendly": True,
                    "healthPriority": "high",
                    "spiceTolerance": "medium",
                    "preferredCuisines": ["italian", "mediterranean"]
                },
                "schema_version": 1
            }
            
            profile_result = self.client.table('user_profiles').insert(profile_data).execute()
            
            if not profile_result.data:
                self.results.add_result("User Profile - Create", False, "Profile creation failed")
                return False
            
            self.test_profiles.append(test_user_id)
            
            # Test 2: Read profile
            read_result = self.client.table('user_profiles').select('*').eq('user_id', test_user_id).execute()
            
            if not read_result.data or len(read_result.data) != 1:
                self.results.add_result("User Profile - Read", False, "Profile not found")
                return False
            
            profile = read_result.data[0]
            
            # Verify data integrity
            if (profile['age'] != 25 or 
                profile['height_cm'] != 170 or 
                profile['weight_kg'] != 65.0 or
                profile['gender'] != 'female'):
                self.results.add_result("User Profile - Data Integrity", False, "Profile data mismatch")
                return False
            
            # Test 3: Update profile
            update_data = {
                "age": 26,
                "weight_kg": 64.0,
                "goals": ["weight_loss", "muscle_tone", "endurance"],
                "profile_extensions": {
                    "budgetFriendly": True,
                    "healthPriority": "high",
                    "spiceTolerance": "high",
                    "preferredCuisines": ["italian", "mediterranean", "thai"]
                }
            }
            
            update_result = self.client.table('user_profiles').update(update_data).eq('user_id', test_user_id).execute()
            
            if not update_result.data:
                self.results.add_result("User Profile - Update", False, "Profile update failed")
                return False
            
            # Test 4: Verify update
            verify_result = self.client.table('user_profiles').select('*').eq('user_id', test_user_id).execute()
            updated_profile = verify_result.data[0]
            
            if (updated_profile['age'] != 26 or 
                updated_profile['weight_kg'] != 64.0 or
                len(updated_profile['goals']) != 3):
                self.results.add_result("User Profile - Update Verification", False, "Update not reflected")
                return False
            
            # Test 5: Query with JSONB extensions
            jsonb_result = self.client.table('user_profiles').select('*').contains('profile_extensions', {'healthPriority': 'high'}).execute()
            
            if not jsonb_result.data:
                self.results.add_result("User Profile - JSONB Query", False, "JSONB query failed")
                return False
            
            self.results.add_result("User Profile Operations", True, test_data={"user_id": test_user_id})
            return True
            
        except Exception as e:
            self.results.add_result("User Profile Operations", False, str(e))
            return False
    
    def test_user_interactions_operations(self) -> bool:
        """Test user interactions table operations"""
        print("\n🧪 Testing user interactions operations...")
        
        try:
            # Create a user first
            test_user_id = str(uuid.uuid4())
            test_email = f"interaction_test_{uuid.uuid4().hex[:8]}@example.com"
            
            user_data = {
                "id": test_user_id,
                "email": test_email
            }
            
            self.client.table('users').insert(user_data).execute()
            self.test_users.append(test_user_id)
            
            # Get an existing restaurant from the database (prefer real restaurants over test restaurant)
            restaurants_result = self.client.table('restaurants').select('id, name').neq('id', '00000000-0000-0000-0000-000000000000').limit(1).execute()
            if not restaurants_result.data:
                # Fallback to test restaurant if no real restaurants exist
                restaurants_result = self.client.table('restaurants').select('id, name').eq('id', '00000000-0000-0000-0000-000000000000').execute()
                if not restaurants_result.data:
                    self.results.add_result("User Interactions - Restaurant Lookup", False, "No restaurants found in database")
                    return False
            
            test_restaurant_id = restaurants_result.data[0]['id']
            restaurant_name = restaurants_result.data[0]['name']
            print(f"Using restaurant: {restaurant_name} ({test_restaurant_id})")
            
            # Test 1: Create interactions
            interactions_data = [
                {
                    "user_id": test_user_id,
                    "restaurant_id": test_restaurant_id,
                    "interaction_type": "like",
                    "context": {
                        "search_query": "healthy food",
                        "position": 1,
                        "timestamp": datetime.now().isoformat()
                    }
                },
                {
                    "user_id": test_user_id,
                    "restaurant_id": test_restaurant_id,
                    "interaction_type": "dislike",
                    "context": {
                        "search_query": "fast food",
                        "position": 2,
                        "timestamp": datetime.now().isoformat()
                    }
                },
                {
                    "user_id": test_user_id,
                    "restaurant_id": test_restaurant_id,
                    "interaction_type": "view",
                    "context": {
                        "search_query": "italian food",
                        "position": 3,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            ]
            
            for interaction in interactions_data:
                result = self.client.table('user_interactions').insert(interaction).execute()
                if result.data:
                    self.test_interactions.append(result.data[0]['id'])
            
            # Test 2: Query interactions by user
            user_interactions = self.client.table('user_interactions').select('*').eq('user_id', test_user_id).execute()
            
            if not user_interactions.data or len(user_interactions.data) != 3:
                self.results.add_result("User Interactions - Query by User", False, f"Expected 3 interactions, got {len(user_interactions.data) if user_interactions.data else 0}")
                return False
            
            # Test 3: Query by interaction type
            likes = self.client.table('user_interactions').select('*').eq('user_id', test_user_id).eq('interaction_type', 'like').execute()
            
            if not likes.data or len(likes.data) != 1:
                self.results.add_result("User Interactions - Query by Type", False, f"Expected 1 like, got {len(likes.data) if likes.data else 0}")
                return False
            
            # Test 4: Query with JSONB context
            context_query = self.client.table('user_interactions').select('*').eq('user_id', test_user_id).contains('context', {'search_query': 'healthy food'}).execute()
            
            if not context_query.data or len(context_query.data) != 1:
                self.results.add_result("User Interactions - JSONB Context", False, f"Expected 1 result, got {len(context_query.data) if context_query.data else 0}")
                return False
            
            # Test 5: Aggregate queries
            stats_query = self.client.table('user_interactions').select('interaction_type').eq('user_id', test_user_id).execute()
            
            if not stats_query.data:
                self.results.add_result("User Interactions - Stats Query", False, "Stats query failed")
                return False
            
            interaction_types = [item['interaction_type'] for item in stats_query.data]
            expected_types = ['like', 'dislike', 'view']
            
            if not all(t in interaction_types for t in expected_types):
                self.results.add_result("User Interactions - Stats Verification", False, f"Missing interaction types: {interaction_types}")
                return False
            
            self.results.add_result("User Interactions Operations", True, test_data={"user_id": test_user_id})
            return True
            
        except Exception as e:
            self.results.add_result("User Interactions Operations", False, str(e))
            return False
    
    def test_row_level_security(self) -> bool:
        """Test Row Level Security policies"""
        print("\n🧪 Testing Row Level Security...")
        
        try:
            # Create two users
            user1_id = str(uuid.uuid4())
            user2_id = str(uuid.uuid4())
            
            user1_data = {"id": user1_id, "email": f"rls_test_1_{uuid.uuid4().hex[:8]}@example.com"}
            user2_data = {"id": user2_id, "email": f"rls_test_2_{uuid.uuid4().hex[:8]}@example.com"}
            
            self.client.table('users').insert(user1_data).execute()
            self.client.table('users').insert(user2_data).execute()
            self.test_users.extend([user1_id, user2_id])
            
            # Create profiles for both users
            profile1_data = {
                "user_id": user1_id,
                "age": 25,
                "gender": "female",
                "goals": ["weight_loss"]
            }
            
            profile2_data = {
                "user_id": user2_id,
                "age": 30,
                "gender": "male",
                "goals": ["muscle_gain"]
            }
            
            self.client.table('user_profiles').insert(profile1_data).execute()
            self.client.table('user_profiles').insert(profile2_data).execute()
            self.test_profiles.extend([user1_id, user2_id])
            
            # Test 1: Query profiles (should work with service role)
            all_profiles = self.client.table('user_profiles').select('*').execute()
            
            if not all_profiles.data or len(all_profiles.data) < 2:
                self.results.add_result("RLS - Service Role Access", False, "Service role should access all profiles")
                return False
            
            # Test 2: Test with anon client (should be restricted)
            try:
                from app.core.supabase import get_supabase_anon_client
                anon_client = get_supabase_anon_client()
                
                # This should fail or return empty due to RLS
                anon_profiles = anon_client.table('user_profiles').select('*').execute()
                
                # With RLS enabled, this should return empty or fail
                if anon_profiles.data and len(anon_profiles.data) > 0:
                    self.results.add_result("RLS - Anon Client Restriction", False, "Anon client should not access user profiles")
                    return False
                
                self.results.add_result("RLS - Anon Client Restriction", True)
                
            except Exception as e:
                # If anon client fails, that's actually good for security
                self.results.add_result("RLS - Anon Client Restriction", True)
            
            self.results.add_result("Row Level Security", True)
            return True
            
        except Exception as e:
            self.results.add_result("Row Level Security", False, str(e))
            return False
    
    def test_database_constraints(self) -> bool:
        """Test database constraints and foreign keys"""
        print("\n🧪 Testing database constraints...")
        
        try:
            # Test 1: Foreign key constraint - try to create profile for non-existent user
            fake_user_id = str(uuid.uuid4())
            profile_data = {
                "user_id": fake_user_id,
                "age": 25,
                "gender": "female"
            }
            
            try:
                result = self.client.table('user_profiles').insert(profile_data).execute()
                if result.data:
                    self.results.add_result("Database Constraints - Foreign Key", False, "Should fail with non-existent user")
                    return False
            except Exception:
                # Expected to fail
                pass
            
            # Test 2: Unique constraint - try to create duplicate user
            test_user_id = str(uuid.uuid4())
            test_email = f"constraint_test_{uuid.uuid4().hex[:8]}@example.com"
            
            user_data = {
                "id": test_user_id,
                "email": test_email
            }
            
            # Create first user
            result1 = self.client.table('users').insert(user_data).execute()
            if not result1.data:
                self.results.add_result("Database Constraints - Unique Email", False, "First user creation failed")
                return False
            
            self.test_users.append(test_user_id)
            
            # Try to create duplicate
            duplicate_data = {
                "id": str(uuid.uuid4()),
                "email": test_email  # Same email
            }
            
            try:
                result2 = self.client.table('users').insert(duplicate_data).execute()
                if result2.data:
                    self.results.add_result("Database Constraints - Unique Email", False, "Should fail with duplicate email")
                    return False
            except Exception:
                # Expected to fail
                pass
            
            # Test 3: Not null constraints (user_id is required)
            try:
                null_profile = {
                    # Missing user_id - this should fail
                }
                result = self.client.table('user_profiles').insert(null_profile).execute()
                if result.data:
                    self.results.add_result("Database Constraints - Not Null", False, "Should fail with missing user_id")
                    return False
            except Exception:
                # Expected to fail
                pass
            
            self.results.add_result("Database Constraints", True)
            return True
            
        except Exception as e:
            self.results.add_result("Database Constraints", False, str(e))
            return False
    
    def test_performance_queries(self) -> bool:
        """Test performance with larger datasets"""
        print("\n🧪 Testing performance queries...")
        
        try:
            # Create multiple users and profiles for performance testing
            test_users = []
            test_profiles = []
            
            for i in range(10):
                user_id = str(uuid.uuid4())
                email = f"perf_test_{i}_{uuid.uuid4().hex[:8]}@example.com"
                
                user_data = {
                    "id": user_id,
                    "email": email
                }
                
                profile_data = {
                    "user_id": user_id,
                    "age": 20 + (i % 20),
                    "gender": "female" if i % 2 == 0 else "male",
                    "goals": ["goal1", "goal2"] if i % 3 == 0 else ["goal3"],
                    "profile_extensions": {
                        "test_field": f"value_{i}",
                        "numeric_field": i * 10
                    }
                }
                
                self.client.table('users').insert(user_data).execute()
                self.client.table('user_profiles').insert(profile_data).execute()
                
                test_users.append(user_id)
                test_profiles.append(user_id)
            
            self.test_users.extend(test_users)
            self.test_profiles.extend(test_profiles)
            
            # Test 1: Bulk query
            start_time = datetime.now()
            all_profiles = self.client.table('user_profiles').select('*').execute()
            query_time = (datetime.now() - start_time).total_seconds()
            
            if not all_profiles.data or len(all_profiles.data) < 10:
                self.results.add_result("Performance - Bulk Query", False, f"Expected at least 10 profiles, got {len(all_profiles.data) if all_profiles.data else 0}")
                return False
            
            # Test 2: Filtered query
            start_time = datetime.now()
            female_profiles = self.client.table('user_profiles').select('*').eq('gender', 'female').execute()
            filter_time = (datetime.now() - start_time).total_seconds()
            
            if not female_profiles.data:
                self.results.add_result("Performance - Filtered Query", False, "No female profiles found")
                return False
            
            # Test 3: JSONB query
            start_time = datetime.now()
            jsonb_profiles = self.client.table('user_profiles').select('*').contains('profile_extensions', {'test_field': 'value_5'}).execute()
            jsonb_time = (datetime.now() - start_time).total_seconds()
            
            if not jsonb_profiles.data:
                self.results.add_result("Performance - JSONB Query", False, "JSONB query failed")
                return False
            
            # Performance thresholds (adjust based on your setup)
            if query_time > 2.0:
                self.results.add_result("Performance - Query Speed", False, f"Bulk query too slow: {query_time:.2f}s")
                return False
            
            if filter_time > 1.0:
                self.results.add_result("Performance - Filter Speed", False, f"Filtered query too slow: {filter_time:.2f}s")
                return False
            
            if jsonb_time > 1.5:
                self.results.add_result("Performance - JSONB Speed", False, f"JSONB query too slow: {jsonb_time:.2f}s")
                return False
            
            self.results.add_result("Performance Queries", True, test_data={
                "query_time": query_time,
                "filter_time": filter_time,
                "jsonb_time": jsonb_time,
                "total_profiles": len(all_profiles.data)
            })
            return True
            
        except Exception as e:
            self.results.add_result("Performance Queries", False, str(e))
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Clean up interactions first (due to foreign keys)
            for interaction_id in self.test_interactions:
                try:
                    self.client.table('user_interactions').delete().eq('id', interaction_id).execute()
                except:
                    pass
            
            # Clean up profiles
            for user_id in self.test_profiles:
                try:
                    self.client.table('user_profiles').delete().eq('user_id', user_id).execute()
                except:
                    pass
            
            # Clean up users
            for user_id in self.test_users:
                try:
                    self.client.table('users').delete().eq('id', user_id).execute()
                except:
                    pass
            
            print(f"Cleaned up {len(self.test_users)} users, {len(self.test_profiles)} profiles, {len(self.test_interactions)} interactions")
            
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def run_all_tests(self) -> bool:
        """Run all Supabase integration tests"""
        print("🚀 Starting Supabase Integration Tests")
        print("=" * 60)
        
        # Setup
        if not self.setup_client():
            return False
        
        # Run all test suites
        test_methods = [
            self.test_user_table_operations,
            self.test_user_profile_operations,
            self.test_user_interactions_operations,
            self.test_row_level_security,
            self.test_database_constraints,
            self.test_performance_queries
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                test_name = test_method.__name__.replace("test_", "").replace("_", " ").title()
                self.results.add_result(test_name, False, f"Test exception: {str(e)}")
        
        # Cleanup
        self.cleanup_test_data()
        
        # Show results
        return self.results.summary()

def main():
    """Main test runner"""
    print("🧪 Supabase Integration Test Suite")
    print("Testing direct database operations and data integrity")
    print("=" * 60)
    
    test_suite = SupabaseIntegrationTest()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All Supabase tests passed! Database integration is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some Supabase tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
