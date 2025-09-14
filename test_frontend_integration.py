#!/usr/bin/env python3
"""
Comprehensive Frontend Integration Test
Simulates all frontend interactions and tests the complete flow
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:3003"

class FrontendIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = "test-user-123"
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        try:
            response = self.session.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_menu_items_search(self) -> bool:
        """Test menu items search endpoint"""
        try:
            payload = {
                "query": "healthy lunch options",
                "location": {"lat": 40.7580, "lng": -73.9855},
                "filters": {"max_price": 15, "dietary_restrictions": ["vegetarian"]},
                "limit": 5
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/menu-items/search",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get("menu_items", [])
                self.log_test("Menu Items Search", True, f"Found {len(menu_items)} items")
                return len(menu_items) > 0
            else:
                self.log_test("Menu Items Search", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Menu Items Search", False, f"Error: {str(e)}")
            return False
    
    def test_ai_recommendation(self) -> bool:
        """Test AI recommendation endpoint"""
        try:
            payload = {
                "message": "I want high protein meals for post-workout recovery",
                "user_id": self.user_id,
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "post_workout"
                }
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/ai/recommend",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("ai_response", "")
                menu_items = data.get("menu_items", [])
                self.log_test("AI Recommendation", True, f"AI response: {ai_response[:50]}..., Found {len(menu_items)} items")
                return len(menu_items) > 0
            else:
                self.log_test("AI Recommendation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Recommendation", False, f"Error: {str(e)}")
            return False
    
    def test_conversational_search(self) -> bool:
        """Test conversational search with chat history"""
        try:
            payload = {
                "message": "Show me vegan options under $12",
                "user_id": self.user_id,
                "chat_history": [
                    {"role": "user", "content": "I want healthy food"},
                    {"role": "assistant", "content": "I'll help you find healthy options!"}
                ],
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855}
                }
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/ai/search",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("ai_response", "")
                menu_items = data.get("menu_items", [])
                self.log_test("Conversational Search", True, f"AI response: {ai_response[:50]}..., Found {len(menu_items)} items")
                return len(menu_items) > 0
            else:
                self.log_test("Conversational Search", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Conversational Search", False, f"Error: {str(e)}")
            return False
    
    def test_swipe_interactions(self) -> bool:
        """Test swipe interaction recording"""
        try:
            # Test like action
            like_payload = {
                "user_id": self.user_id,
                "menu_item_id": "item-1",
                "action": "like",
                "search_query": "high protein meals",
                "position": 0,
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/menu-items/interactions/swipe",
                json=like_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # Test dislike action
                dislike_payload = {
                    "user_id": self.user_id,
                    "menu_item_id": "item-2",
                    "action": "dislike",
                    "search_query": "high protein meals",
                    "position": 1,
                    "timestamp": "2024-01-01T12:01:00Z"
                }
                
                response2 = self.session.post(
                    f"{API_BASE_URL}/menu-items/interactions/swipe",
                    json=dislike_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response2.status_code == 200:
                    self.log_test("Swipe Interactions", True, "Like and dislike actions recorded")
                    return True
                else:
                    self.log_test("Swipe Interactions", False, f"Dislike action failed: {response2.status_code}")
                    return False
            else:
                self.log_test("Swipe Interactions", False, f"Like action failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Swipe Interactions", False, f"Error: {str(e)}")
            return False
    
    def test_location_based_search(self) -> bool:
        """Test location-based search functionality"""
        try:
            # Test with different location
            payload = {
                "query": "quick lunch",
                "location": {"lat": 40.7128, "lng": -74.0060},  # Different location
                "filters": {"max_prep_time": 15},
                "limit": 3
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/menu-items/search",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get("menu_items", [])
                self.log_test("Location-based Search", True, f"Found {len(menu_items)} items for new location")
                return len(menu_items) > 0
            else:
                self.log_test("Location-based Search", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Location-based Search", False, f"Error: {str(e)}")
            return False
    
    def test_voice_input_simulation(self) -> bool:
        """Test voice input simulation (conversational search with voice context)"""
        try:
            payload = {
                "message": "I'm looking for something quick and healthy for breakfast",
                "user_id": self.user_id,
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "input_method": "voice",
                    "meal_context": "breakfast"
                }
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/ai/recommend",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("ai_response", "")
                menu_items = data.get("menu_items", [])
                self.log_test("Voice Input Simulation", True, f"AI response: {ai_response[:50]}..., Found {len(menu_items)} items")
                return len(menu_items) > 0
            else:
                self.log_test("Voice Input Simulation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Voice Input Simulation", False, f"Error: {str(e)}")
            return False
    
    def test_discover_food_flow(self) -> bool:
        """Test the complete discover food flow"""
        try:
            # Step 1: Initial search
            initial_payload = {
                "message": "Show me popular dishes nearby",
                "user_id": self.user_id,
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch"
                }
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/ai/recommend",
                json=initial_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get("menu_items", [])
                
                if len(menu_items) > 0:
                    # Step 2: Continue conversation
                    continue_payload = {
                        "message": "Actually, I prefer vegetarian options",
                        "user_id": self.user_id,
                        "chat_history": [
                            {"role": "user", "content": "Show me popular dishes nearby"},
                            {"role": "assistant", "content": data.get("ai_response", "")}
                        ],
                        "context": {
                            "location": {"lat": 40.7580, "lng": -73.9855}
                        }
                    }
                    
                    response2 = self.session.post(
                        f"{API_BASE_URL}/ai/search",
                        json=continue_payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response2.status_code == 200:
                        data2 = response2.json()
                        menu_items2 = data2.get("menu_items", [])
                        self.log_test("Discover Food Flow", True, f"Initial: {len(menu_items)} items, Refined: {len(menu_items2)} items")
                        return True
                    else:
                        self.log_test("Discover Food Flow", False, f"Continue conversation failed: {response2.status_code}")
                        return False
                else:
                    self.log_test("Discover Food Flow", False, "No initial menu items found")
                    return False
            else:
                self.log_test("Discover Food Flow", False, f"Initial search failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Discover Food Flow", False, f"Error: {str(e)}")
            return False
    
    def test_frontend_connectivity(self) -> bool:
        """Test if frontend is accessible"""
        try:
            response = self.session.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Connectivity", True, f"Frontend accessible at {FRONTEND_URL}")
                return True
            else:
                self.log_test("Frontend Connectivity", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Connectivity", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting Frontend Integration Tests...")
        print("=" * 60)
        
        # Test backend endpoints
        self.test_backend_health()
        self.test_menu_items_search()
        self.test_ai_recommendation()
        self.test_conversational_search()
        self.test_swipe_interactions()
        self.test_location_based_search()
        self.test_voice_input_simulation()
        self.test_discover_food_flow()
        
        # Test frontend connectivity
        self.test_frontend_connectivity()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 All tests passed! The system is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Check the details above.")
            
        return passed == total

def main():
    """Main test runner"""
    tester = FrontendIntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
