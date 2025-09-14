#!/usr/bin/env python3
"""
Test the complete frontend workflow using the proper recommendation engine
Simulates: Account setup -> Personalization -> First search -> Conversational AI -> Swipeable results
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontendWorkflowTester:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.user_id = f"frontend_user_{int(time.time())}"
        self.chat_history = []
        
    def test_backend_health(self) -> bool:
        """Test 1: Backend health check"""
        logger.info("🔍 Step 1: Testing backend health...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Backend is running")
                return True
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {str(e)}")
            return False
    
    def test_ai_recommendation_engine(self) -> bool:
        """Test 2: Direct AI recommendation engine test"""
        logger.info("🔍 Step 2: Testing AI recommendation engine directly...")
        try:
            request = {
                "message": "I want high protein meals for post-workout recovery",
                "user_id": self.user_id,
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "post_workout"
                },
                "chat_history": []
            }
            
            response = requests.post(
                f"{self.base_url}/ai/recommend",
                json=request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ AI recommendation engine working")
                
                # Check AI response
                ai_response = data.get("ai_response", "")
                logger.info(f"AI Response: {ai_response}")
                
                # Check menu items
                menu_items = data.get("menu_items", [])
                logger.info(f"Menu items returned: {len(menu_items)}")
                
                if menu_items:
                    first_item = menu_items[0]
                    logger.info(f"First item: {first_item.get('name')}")
                    logger.info(f"Calories: {first_item.get('calories')}")
                    logger.info(f"Protein: {first_item.get('protein')}")
                    
                    # Verify real data
                    if first_item.get('calories', 0) > 0:
                        logger.info("✅ Real nutrition data from recommendation engine")
                        return True
                    else:
                        logger.warning("⚠️ Zero nutrition data from recommendation engine")
                        return False
                else:
                    logger.error("❌ No menu items from recommendation engine")
                    return False
            else:
                logger.error(f"❌ AI recommendation engine failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ AI recommendation engine test failed: {str(e)}")
            return False
    
    def test_conversational_ai_with_recommendation_engine(self) -> bool:
        """Test 3: Conversational AI using the recommendation engine"""
        logger.info("🔍 Step 3: Testing conversational AI with recommendation engine...")
        try:
            # First conversational search
            request = {
                "message": "I want something healthy for lunch with chicken",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch"
                },
                "chat_history": [],
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Conversational AI with recommendation engine working")
                
                # Check AI response
                ai_response = data.get("ai_response", "")
                logger.info(f"AI Response: {ai_response}")
                
                # Check if it's using the recommendation engine (should be more sophisticated)
                if len(ai_response) > 50 and ("chicken" in ai_response.lower() or "healthy" in ai_response.lower()):
                    logger.info("✅ AI response is contextual and specific (using recommendation engine)")
                else:
                    logger.warning("⚠️ AI response seems generic")
                
                # Check menu items
                menu_items = data.get("menu_items", [])
                logger.info(f"Menu items returned: {len(menu_items)}")
                
                if menu_items:
                    first_item = menu_items[0]
                    logger.info(f"First item: {first_item.get('name')}")
                    logger.info(f"Calories: {first_item.get('calories')}")
                    logger.info(f"Protein: {first_item.get('protein')}")
                    
                    # Verify real data
                    if first_item.get('calories', 0) > 0:
                        logger.info("✅ Real nutrition data from conversational AI")
                        
                        # Store chat history for follow-up
                        self.chat_history = data.get("chat_history", [])
                        return True
                    else:
                        logger.warning("⚠️ Zero nutrition data from conversational AI")
                        return False
                else:
                    logger.error("❌ No menu items from conversational AI")
                    return False
            else:
                logger.error(f"❌ Conversational AI failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Conversational AI test failed: {str(e)}")
            return False
    
    def test_swipeable_results_quality(self) -> bool:
        """Test 4: Verify results are suitable for swipeable interface"""
        logger.info("🔍 Step 4: Testing swipeable results quality...")
        try:
            # Test with a specific query that should return diverse, swipeable results
            request = {
                "message": "Show me pizza options",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "dinner"
                },
                "chat_history": [],
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get("menu_items", [])
                logger.info(f"Swipeable results test returned {len(menu_items)} items")
                
                if menu_items:
                    # Check for diverse results suitable for swiping
                    item_names = [item.get('name', '') for item in menu_items]
                    item_calories = [item.get('calories', 0) for item in menu_items]
                    item_prices = [item.get('price', 0) for item in menu_items]
                    
                    logger.info(f"Item names: {item_names[:5]}...")  # Show first 5
                    logger.info(f"Calories range: {min(item_calories)} - {max(item_calories)}")
                    logger.info(f"Price range: ${min(item_prices):.2f} - ${max(item_prices):.2f}")
                    
                    # Check if we have actual pizza items (not beverages)
                    pizza_items = [name for name in item_names if 'pizza' in name.lower()]
                    logger.info(f"Pizza items found: {len(pizza_items)}")
                    
                    if len(pizza_items) > 0:
                        logger.info("✅ Found actual pizza items (proper semantic search)")
                        
                        # Check for realistic nutrition data
                        if max(item_calories) > 400:  # Pizza should have more calories than beverages
                            logger.info("✅ Realistic nutrition data for pizza items")
                            return True
                        else:
                            logger.warning("⚠️ Nutrition data seems unrealistic for pizza")
                            return False
                    else:
                        logger.warning("⚠️ No pizza items found - semantic search not working properly")
                        return False
                else:
                    logger.error("❌ No menu items for swipeable test")
                    return False
            else:
                logger.error(f"❌ Swipeable results test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Swipeable results test failed: {str(e)}")
            return False
    
    def test_follow_up_conversation(self) -> bool:
        """Test 5: Follow-up conversation with recommendation engine"""
        logger.info("🔍 Step 5: Testing follow-up conversation...")
        try:
            # Follow-up search with chat history
            request = {
                "message": "Actually, make it vegetarian",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "dinner"
                },
                "chat_history": self.chat_history,
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Follow-up conversation working")
                
                # Check AI response
                ai_response = data.get("ai_response", "")
                logger.info(f"AI Response: {ai_response}")
                
                # Verify it understands the context change
                if "vegetarian" in ai_response.lower() or "vegetable" in ai_response.lower():
                    logger.info("✅ AI understood the context change")
                else:
                    logger.warning("⚠️ AI didn't understand context change")
                
                # Check menu items
                menu_items = data.get("menu_items", [])
                logger.info(f"Menu items returned: {len(menu_items)}")
                
                if menu_items:
                    first_item = menu_items[0]
                    logger.info(f"First item: {first_item.get('name')}")
                    logger.info(f"Calories: {first_item.get('calories')}")
                    logger.info(f"Protein: {first_item.get('protein')}")
                    
                    # Verify real data
                    if first_item.get('calories', 0) > 0:
                        logger.info("✅ Real nutrition data in follow-up")
                        return True
                    else:
                        logger.warning("⚠️ Zero nutrition data in follow-up")
                        return False
                else:
                    logger.error("❌ No menu items in follow-up")
                    return False
            else:
                logger.error(f"❌ Follow-up conversation failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Follow-up conversation test failed: {str(e)}")
            return False
    
    def run_complete_frontend_workflow_test(self) -> bool:
        """Run the complete frontend workflow test"""
        logger.info("🚀 Starting Complete Frontend Workflow Test with Recommendation Engine")
        logger.info("=" * 70)
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("AI Recommendation Engine", self.test_ai_recommendation_engine),
            ("Conversational AI with Recommendation Engine", self.test_conversational_ai_with_recommendation_engine),
            ("Swipeable Results Quality", self.test_swipeable_results_quality),
            ("Follow-up Conversation", self.test_follow_up_conversation)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                result = test_func()
                results[test_name] = result
                logger.info(f"{test_name}: {'✅ PASS' if result else '❌ FAIL'}")
            except Exception as e:
                logger.error(f"{test_name}: ❌ ERROR - {str(e)}")
                results[test_name] = False
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 Complete Frontend Workflow Test Results:")
        passed = 0
        total = len(tests)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
            if result:
                passed += 1
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 Complete frontend workflow test PASSED! Recommendation engine working perfectly!")
        else:
            logger.warning(f"⚠️ {total - passed} tests failed. Issues need to be fixed.")
        
        return passed == total

def main():
    """Run the complete frontend workflow test"""
    tester = FrontendWorkflowTester()
    success = tester.run_complete_frontend_workflow_test()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
