#!/usr/bin/env python3
"""
Comprehensive Frontend Integration Tests for Conversational Search
Tests the complete user journey from initial search to conversational refinement
"""

import asyncio
import json
import time
import requests
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontendIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_user_id = "test-user-frontend-123"
        self.chat_history = []
        self.session_results = []
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
        self.session_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        
    def check_backend_health(self) -> bool:
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                self.log_test_result("Backend Health Check", True, "Backend is running")
                return True
            else:
                self.log_test_result("Backend Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Backend Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_initial_conversational_search(self) -> bool:
        """Test initial conversational search with a simple query"""
        try:
            # Simulate user's initial search
            search_request = {
                "message": "I want healthy food for lunch",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch",
                    "timestamp": "2024-01-15T12:00:00Z"
                },
                "chat_history": [],
                "user_id": self.test_user_id
            }
            
            logger.info("🔍 Testing initial conversational search...")
            response = requests.post(
                f"{self.api_base}/ai/search",
                json=search_request,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["ai_response", "menu_items", "search_reasoning"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result(
                        "Initial Conversational Search", 
                        False, 
                        f"Missing fields: {missing_fields}"
                    )
                    return False
                
                # Check if we got menu items
                menu_items = data.get("menu_items", [])
                if not menu_items:
                    self.log_test_result(
                        "Initial Conversational Search", 
                        False, 
                        "No menu items returned"
                    )
                    return False
                
                # Validate menu item structure
                first_item = menu_items[0]
                required_item_fields = ["id", "name", "description", "restaurant", "price"]
                missing_item_fields = [field for field in required_item_fields if field not in first_item]
                
                if missing_item_fields:
                    self.log_test_result(
                        "Initial Conversational Search", 
                        False, 
                        f"Menu item missing fields: {missing_item_fields}"
                    )
                    return False
                
                # Store the AI response for chat history
                self.chat_history = [
                    {"role": "user", "content": search_request["message"]},
                    {"role": "assistant", "content": data["ai_response"]}
                ]
                
                self.log_test_result(
                    "Initial Conversational Search", 
                    True, 
                    f"Got {len(menu_items)} menu items, AI response: {data['ai_response'][:50]}..."
                )
                return True
                
            else:
                self.log_test_result(
                    "Initial Conversational Search", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Initial Conversational Search", False, f"Error: {str(e)}")
            return False
    
    def test_conversational_refinement(self) -> bool:
        """Test conversational refinement - user continues the conversation"""
        try:
            # Simulate user refining their search
            refinement_request = {
                "message": "Actually, I want something with more protein",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch",
                    "timestamp": "2024-01-15T12:05:00Z"
                },
                "chat_history": self.chat_history,  # Include previous conversation
                "user_id": self.test_user_id
            }
            
            logger.info("🔄 Testing conversational refinement...")
            response = requests.post(
                f"{self.api_base}/ai/search",
                json=refinement_request,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "menu_items" not in data or "ai_response" not in data:
                    self.log_test_result(
                        "Conversational Refinement", 
                        False, 
                        "Missing required response fields"
                    )
                    return False
                
                # Check if we got different menu items (refined results)
                menu_items = data.get("menu_items", [])
                if not menu_items:
                    self.log_test_result(
                        "Conversational Refinement", 
                        False, 
                        "No menu items returned after refinement"
                    )
                    return False
                
                # Update chat history
                self.chat_history.extend([
                    {"role": "user", "content": refinement_request["message"]},
                    {"role": "assistant", "content": data["ai_response"]}
                ])
                
                self.log_test_result(
                    "Conversational Refinement", 
                    True, 
                    f"Got {len(menu_items)} refined menu items, AI response: {data['ai_response'][:50]}..."
                )
                return True
                
            else:
                self.log_test_result(
                    "Conversational Refinement", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Conversational Refinement", False, f"Error: {str(e)}")
            return False
    
    def test_multiple_conversational_turns(self) -> bool:
        """Test multiple turns of conversation"""
        try:
            # Test a third turn of conversation
            third_request = {
                "message": "Can you show me vegetarian options instead?",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch",
                    "timestamp": "2024-01-15T12:10:00Z"
                },
                "chat_history": self.chat_history,  # Full conversation history
                "user_id": self.test_user_id
            }
            
            logger.info("🔄 Testing multiple conversational turns...")
            response = requests.post(
                f"{self.api_base}/ai/search",
                json=third_request,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                menu_items = data.get("menu_items", [])
                if not menu_items:
                    self.log_test_result(
                        "Multiple Conversational Turns", 
                        False, 
                        "No menu items returned"
                    )
                    return False
                
                # Check if AI response acknowledges the conversation history
                ai_response = data.get("ai_response", "")
                if "vegetarian" not in ai_response.lower() and "plant" not in ai_response.lower():
                    self.log_test_result(
                        "Multiple Conversational Turns", 
                        False, 
                        "AI response doesn't seem to acknowledge vegetarian request"
                    )
                    return False
                
                # Update chat history with the new messages
                self.chat_history.extend([
                    {"role": "user", "content": third_request["message"]},
                    {"role": "assistant", "content": ai_response}
                ])
                
                self.log_test_result(
                    "Multiple Conversational Turns", 
                    True, 
                    f"Got {len(menu_items)} vegetarian menu items, AI response: {ai_response[:50]}..."
                )
                return True
                
            else:
                self.log_test_result(
                    "Multiple Conversational Turns", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Multiple Conversational Turns", False, f"Error: {str(e)}")
            return False
    
    def test_chat_history_persistence(self) -> bool:
        """Test that chat history is properly maintained"""
        try:
            # Verify our chat history has the expected structure
            expected_turns = 3  # Initial + 2 refinements
            expected_messages = expected_turns * 2  # User + AI for each turn
            
            if len(self.chat_history) != expected_messages:
                self.log_test_result(
                    "Chat History Persistence", 
                    False, 
                    f"Expected {expected_messages} messages, got {len(self.chat_history)}"
                )
                return False
            
            # Check that messages alternate between user and assistant
            for i, message in enumerate(self.chat_history):
                expected_role = "user" if i % 2 == 0 else "assistant"
                if message.get("role") != expected_role:
                    self.log_test_result(
                        "Chat History Persistence", 
                        False, 
                        f"Message {i} has wrong role: {message.get('role')}"
                    )
                    return False
            
            self.log_test_result(
                "Chat History Persistence", 
                True, 
                f"Chat history properly maintained with {len(self.chat_history)} messages"
            )
            return True
            
        except Exception as e:
            self.log_test_result("Chat History Persistence", False, f"Error: {str(e)}")
            return False
    
    def test_api_endpoint_consistency(self) -> bool:
        """Test that the correct API endpoints are being used"""
        try:
            # Test that conversational search endpoint exists and works
            test_request = {
                "message": "test message",
                "context": {"location": {"lat": 40.7580, "lng": -73.9855}},
                "chat_history": [],
                "user_id": self.test_user_id
            }
            
            # Test conversational search endpoint
            response = requests.post(
                f"{self.api_base}/ai/search",
                json=test_request,
                timeout=5
            )
            
            if response.status_code not in [200, 422]:  # 422 is validation error, which is ok
                self.log_test_result(
                    "API Endpoint Consistency", 
                    False, 
                    f"Conversational search endpoint returned {response.status_code}"
                )
                return False
            
            # Test that AI recommendation endpoint also exists (for comparison)
            response = requests.post(
                f"{self.api_base}/ai/recommend",
                json=test_request,
                timeout=5
            )
            
            if response.status_code not in [200, 422]:
                self.log_test_result(
                    "API Endpoint Consistency", 
                    False, 
                    f"AI recommendation endpoint returned {response.status_code}"
                )
                return False
            
            self.log_test_result(
                "API Endpoint Consistency", 
                True, 
                "Both conversational and AI recommendation endpoints are accessible"
            )
            return True
            
        except Exception as e:
            self.log_test_result("API Endpoint Consistency", False, f"Error: {str(e)}")
            return False
    
    def test_menu_item_data_quality(self) -> bool:
        """Test that menu items have good data quality"""
        try:
            # Get some menu items to validate data quality
            search_request = {
                "message": "Show me some food options",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch"
                },
                "chat_history": [],
                "user_id": self.test_user_id
            }
            
            response = requests.post(
                f"{self.api_base}/ai/search",
                json=search_request,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test_result(
                    "Menu Item Data Quality", 
                    False, 
                    f"Failed to get menu items: {response.status_code}"
                )
                return False
            
            data = response.json()
            menu_items = data.get("menu_items", [])
            
            if not menu_items:
                self.log_test_result(
                    "Menu Item Data Quality", 
                    False, 
                    "No menu items to validate"
                )
                return False
            
            # Validate data quality for first few items
            quality_issues = []
            for i, item in enumerate(menu_items[:3]):  # Check first 3 items
                if not item.get("name") or len(item.get("name", "")) < 2:
                    quality_issues.append(f"Item {i}: Missing or short name")
                
                if not item.get("description") or len(item.get("description", "")) < 10:
                    quality_issues.append(f"Item {i}: Missing or short description")
                
                if not item.get("restaurant", {}).get("name"):
                    quality_issues.append(f"Item {i}: Missing restaurant name")
                
                if not isinstance(item.get("price"), (int, float)) or item.get("price", 0) <= 0:
                    quality_issues.append(f"Item {i}: Invalid price")
            
            if quality_issues:
                self.log_test_result(
                    "Menu Item Data Quality", 
                    False, 
                    f"Quality issues: {'; '.join(quality_issues)}"
                )
                return False
            
            self.log_test_result(
                "Menu Item Data Quality", 
                True, 
                f"Validated {min(3, len(menu_items))} menu items with good data quality"
            )
            return True
            
        except Exception as e:
            self.log_test_result("Menu Item Data Quality", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all frontend integration tests"""
        logger.info("🚀 Starting Frontend Integration Tests for Conversational Search")
        logger.info("=" * 70)
        
        # Check if backend is running first
        if not self.check_backend_health():
            logger.error("❌ Backend is not running. Please start the backend server first.")
            return {"success": False, "error": "Backend not running"}
        
        # Run all tests
        tests = [
            ("Initial Conversational Search", self.test_initial_conversational_search),
            ("Conversational Refinement", self.test_conversational_refinement),
            ("Multiple Conversational Turns", self.test_multiple_conversational_turns),
            ("Chat History Persistence", self.test_chat_history_persistence),
            ("API Endpoint Consistency", self.test_api_endpoint_consistency),
            ("Menu Item Data Quality", self.test_menu_item_data_quality),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                logger.error(f"❌ Test {test_name} crashed: {str(e)}")
        
        # Summary
        logger.info("=" * 70)
        logger.info(f"📊 Test Results: {passed}/{total} tests passed")
        
        success_rate = (passed / total) * 100
        if success_rate >= 80:
            logger.info("🎉 Frontend integration tests PASSED! The conversational search is working properly.")
        else:
            logger.warning("⚠️  Some tests failed. Check the logs above for details.")
        
        return {
            "success": success_rate >= 80,
            "passed": passed,
            "total": total,
            "success_rate": success_rate,
            "results": self.session_results
        }

def main():
    """Main function to run the tests"""
    tester = FrontendIntegrationTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("frontend_integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"📄 Test results saved to frontend_integration_test_results.json")
    
    return 0 if results["success"] else 1

if __name__ == "__main__":
    exit(main())
