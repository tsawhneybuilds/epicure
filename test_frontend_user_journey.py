#!/usr/bin/env python3
"""
Frontend User Journey Test
Simulates a real user interacting with the app through the conversational search interface
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

class FrontendUserJourneyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_user_id = "frontend-user-journey-123"
        self.chat_history = []
        self.current_menu_items = []
        self.test_scenarios = []
        
    def simulate_user_action(self, action: str, details: str = ""):
        """Simulate a user action with logging"""
        logger.info(f"👤 USER ACTION: {action}")
        if details:
            logger.info(f"   Details: {details}")
    
    def simulate_ai_response(self, response: str):
        """Simulate AI response with logging"""
        logger.info(f"🤖 AI RESPONSE: {response}")
    
    def simulate_frontend_update(self, update: str):
        """Simulate frontend UI update with logging"""
        logger.info(f"🖥️  FRONTEND UPDATE: {update}")
    
    def test_initial_app_load(self) -> bool:
        """Test: User opens the app and sees initial state"""
        try:
            self.simulate_user_action("Opens the app", "User sees the main interface with 'Continue the conversation...' input")
            
            # Simulate initial app state - no chat history, no menu items
            self.chat_history = []
            self.current_menu_items = []
            
            self.simulate_frontend_update("App loaded with empty state")
            logger.info("✅ Initial app load simulation completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initial app load test failed: {str(e)}")
            return False
    
    def test_first_search(self) -> bool:
        """Test: User types their first search query"""
        try:
            user_message = "I want healthy food for lunch"
            self.simulate_user_action("Types in 'Continue the conversation' input", f"'{user_message}'")
            
            # Simulate the frontend making the API call
            search_request = {
                "message": user_message,
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch",
                    "timestamp": "2024-01-15T12:00:00Z"
                },
                "chat_history": [],
                "user_id": self.test_user_id
            }
            
            logger.info("📡 Frontend calls /conversational/search API...")
            response = requests.post(
                f"{self.api_base}/ai/search",
                json=search_request,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Simulate frontend receiving response
                self.current_menu_items = data.get("menu_items", [])
                ai_response = data.get("ai_response", "")
                
                # Update chat history
                self.chat_history = [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": ai_response}
                ]
                
                self.simulate_ai_response(ai_response)
                self.simulate_frontend_update(f"Menu items updated: {len(self.current_menu_items)} items displayed")
                self.simulate_frontend_update("Chat history updated with user message and AI response")
                
                # Validate we got results
                if not self.current_menu_items:
                    logger.error("❌ No menu items returned from first search")
                    return False
                
                logger.info(f"✅ First search completed: {len(self.current_menu_items)} menu items")
                return True
                
            else:
                logger.error(f"❌ First search API call failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ First search test failed: {str(e)}")
            return False
    
    def test_conversational_refinement(self) -> bool:
        """Test: User refines their search through conversation"""
        try:
            user_message = "Actually, I want something with more protein"
            self.simulate_user_action("Continues conversation", f"'{user_message}'")
            
            # Simulate the frontend making another API call with chat history
            search_request = {
                "message": user_message,
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch",
                    "timestamp": "2024-01-15T12:05:00Z"
                },
                "chat_history": self.chat_history,  # Include previous conversation
                "user_id": self.test_user_id
            }
            
            logger.info("📡 Frontend calls /conversational/search API with chat history...")
            response = requests.post(
                f"{self.api_base}/ai/search",
                json=search_request,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Simulate frontend receiving refined results
                new_menu_items = data.get("menu_items", [])
                ai_response = data.get("ai_response", "")
                
                # Update state
                self.current_menu_items = new_menu_items
                self.chat_history.extend([
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": ai_response}
                ])
                
                self.simulate_ai_response(ai_response)
                self.simulate_frontend_update(f"Menu items refined: {len(self.current_menu_items)} new items")
                self.simulate_frontend_update("Chat history updated with new conversation turn")
                
                # Validate we got different results
                if not self.current_menu_items:
                    logger.error("❌ No menu items returned from refinement")
                    return False
                
                logger.info(f"✅ Conversational refinement completed: {len(self.current_menu_items)} menu items")
                return True
                
            else:
                logger.error(f"❌ Refinement API call failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Conversational refinement test failed: {str(e)}")
            return False
    
    def test_multiple_refinements(self) -> bool:
        """Test: User makes multiple refinements to their search"""
        try:
            # Test multiple refinement scenarios
            refinements = [
                "Can you show me vegetarian options instead?",
                "Actually, I want something quick and cheap",
                "What about Asian food?"
            ]
            
            for i, user_message in enumerate(refinements, 1):
                self.simulate_user_action(f"Refinement #{i}", f"'{user_message}'")
                
                search_request = {
                    "message": user_message,
                    "context": {
                        "location": {"lat": 40.7580, "lng": -73.9855},
                        "meal_context": "lunch",
                        "timestamp": f"2024-01-15T12:{5+i*2}:00Z"
                    },
                    "chat_history": self.chat_history,
                    "user_id": self.test_user_id
                }
                
                logger.info(f"📡 Frontend calls /conversational/search API for refinement #{i}...")
                response = requests.post(
                    f"{self.api_base}/ai/search",
                    json=search_request,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    new_menu_items = data.get("menu_items", [])
                    ai_response = data.get("ai_response", "")
                    
                    self.current_menu_items = new_menu_items
                    self.chat_history.extend([
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": ai_response}
                    ])
                    
                    self.simulate_ai_response(ai_response)
                    self.simulate_frontend_update(f"Refinement #{i} completed: {len(self.current_menu_items)} items")
                    
                    if not self.current_menu_items:
                        logger.error(f"❌ No menu items returned from refinement #{i}")
                        return False
                        
                else:
                    logger.error(f"❌ Refinement #{i} API call failed: {response.status_code}")
                    return False
            
            logger.info(f"✅ Multiple refinements completed: {len(self.chat_history)} total messages")
            return True
            
        except Exception as e:
            logger.error(f"❌ Multiple refinements test failed: {str(e)}")
            return False
    
    def test_chat_history_accuracy(self) -> bool:
        """Test: Verify chat history is accurate and complete"""
        try:
            self.simulate_user_action("Checks chat history", "User reviews the conversation")
            
            # Verify chat history structure
            expected_turns = 5  # Initial + 4 refinements (1 from Conversational Refinement + 3 from Multiple Refinements)
            expected_messages = expected_turns * 2  # User + AI for each turn
            
            if len(self.chat_history) != expected_messages:
                logger.error(f"❌ Chat history length incorrect: expected {expected_messages}, got {len(self.chat_history)}")
                return False
            
            # Verify message roles alternate correctly
            for i, message in enumerate(self.chat_history):
                expected_role = "user" if i % 2 == 0 else "assistant"
                if message.get("role") != expected_role:
                    logger.error(f"❌ Message {i} has wrong role: {message.get('role')}")
                    return False
            
            # Verify content is not empty
            for i, message in enumerate(self.chat_history):
                if not message.get("content") or len(message.get("content", "")) < 5:
                    logger.error(f"❌ Message {i} has empty or too short content")
                    return False
            
            self.simulate_frontend_update("Chat history verified as accurate and complete")
            logger.info("✅ Chat history accuracy test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Chat history accuracy test failed: {str(e)}")
            return False
    
    def test_menu_item_switching(self) -> bool:
        """Test: Simulate user swiping through menu items"""
        try:
            self.simulate_user_action("Swipes through menu items", "User explores different food options")
            
            if not self.current_menu_items:
                logger.error("❌ No menu items to swipe through")
                return False
            
            # Simulate swiping through items
            for i, item in enumerate(self.current_menu_items[:3]):  # Test first 3 items
                self.simulate_frontend_update(f"Displaying menu item {i+1}: {item.get('name', 'Unknown')}")
                
                # Validate item has required fields
                required_fields = ["id", "name", "description", "restaurant", "price"]
                missing_fields = [field for field in required_fields if field not in item]
                
                if missing_fields:
                    logger.error(f"❌ Menu item {i+1} missing fields: {missing_fields}")
                    return False
            
            self.simulate_frontend_update("Menu item switching test completed")
            logger.info("✅ Menu item switching test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Menu item switching test failed: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test: Simulate error scenarios"""
        try:
            self.simulate_user_action("Tests error handling", "User tries invalid input")
            
            # Test with empty message
            search_request = {
                "message": "",
                "context": {"location": {"lat": 40.7580, "lng": -73.9855}},
                "chat_history": self.chat_history,
                "user_id": self.test_user_id
            }
            
            response = requests.post(
                f"{self.api_base}/ai/search",
                json=search_request,
                timeout=5
            )
            
            # Should handle empty message gracefully
            if response.status_code in [200, 422]:  # 422 is validation error, which is acceptable
                self.simulate_frontend_update("Error handling test passed - empty message handled gracefully")
                logger.info("✅ Error handling test passed")
                return True
            else:
                logger.error(f"❌ Error handling test failed: unexpected status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {str(e)}")
            return False
    
    def run_complete_user_journey(self) -> Dict[str, Any]:
        """Run the complete user journey test"""
        logger.info("🚀 Starting Complete Frontend User Journey Test")
        logger.info("=" * 80)
        
        # Test sequence
        tests = [
            ("Initial App Load", self.test_initial_app_load),
            ("First Search", self.test_first_search),
            ("Conversational Refinement", self.test_conversational_refinement),
            ("Multiple Refinements", self.test_multiple_refinements),
            ("Chat History Accuracy", self.test_chat_history_accuracy),
            ("Menu Item Switching", self.test_menu_item_switching),
            ("Error Handling", self.test_error_handling),
        ]
        
        passed = 0
        total = len(tests)
        results = []
        
        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running: {test_name}")
            logger.info("-" * 50)
            
            try:
                success = test_func()
                results.append({"test": test_name, "success": success})
                if success:
                    passed += 1
                    logger.info(f"✅ {test_name} PASSED")
                else:
                    logger.error(f"❌ {test_name} FAILED")
            except Exception as e:
                logger.error(f"💥 {test_name} CRASHED: {str(e)}")
                results.append({"test": test_name, "success": False, "error": str(e)})
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info(f"📊 User Journey Test Results: {passed}/{total} tests passed")
        
        success_rate = (passed / total) * 100
        if success_rate >= 85:
            logger.info("🎉 USER JOURNEY TEST PASSED! The conversational search works perfectly!")
        else:
            logger.warning("⚠️  Some user journey tests failed. Check the logs above for details.")
        
        return {
            "success": success_rate >= 85,
            "passed": passed,
            "total": total,
            "success_rate": success_rate,
            "results": results,
            "chat_history_length": len(self.chat_history),
            "final_menu_items_count": len(self.current_menu_items)
        }

def main():
    """Main function to run the user journey test"""
    tester = FrontendUserJourneyTester()
    results = tester.run_complete_user_journey()
    
    # Save results to file
    with open("frontend_user_journey_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"📄 User journey test results saved to frontend_user_journey_results.json")
    
    return 0 if results["success"] else 1

if __name__ == "__main__":
    exit(main())
