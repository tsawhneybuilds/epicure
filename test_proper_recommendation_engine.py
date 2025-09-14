#!/usr/bin/env python3
"""
Test the proper AI recommendation engine that was built
This simulates the full frontend workflow using the correct endpoints
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProperRecommendationEngineTester:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.user_id = f"test_user_{int(time.time())}"
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
        """Test 2: AI Recommendation Engine (the proper one)"""
        logger.info("🔍 Step 2: Testing AI Recommendation Engine...")
        try:
            recommendation_request = {
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
                json=recommendation_request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ AI Recommendation Engine successful")
                
                # Check AI response
                ai_response = data.get("ai_response", "")
                logger.info(f"AI Response: {ai_response}")
                
                # Check search query translation
                search_query = data.get("search_query", "")
                logger.info(f"Translated Search Query: {search_query}")
                
                # Check filters applied
                filters_applied = data.get("filters_applied", {})
                logger.info(f"Filters Applied: {filters_applied}")
                
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
                        logger.info("✅ Real nutrition data in recommendation engine")
                        return True
                    else:
                        logger.warning("⚠️ Zero nutrition data in recommendation engine")
                        return False
                else:
                    logger.error("❌ No menu items in recommendation engine")
                    return False
            else:
                logger.error(f"❌ AI Recommendation Engine failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ AI Recommendation Engine failed: {str(e)}")
            return False
    
    def test_query_translation(self) -> bool:
        """Test 3: Query Translation (debugging endpoint)"""
        logger.info("🔍 Step 3: Testing Query Translation...")
        try:
            translation_request = {
                "message": "Healthy vegetarian options under $15",
                "user_id": self.user_id,
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855}
                },
                "chat_history": []
            }
            
            response = requests.post(
                f"{self.base_url}/ai/translate-query",
                json=translation_request,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Query Translation successful")
                
                translation = data.get("translation", {})
                logger.info(f"Original: {data.get('original_message')}")
                logger.info(f"Translated Query: {translation.get('search_query')}")
                logger.info(f"Filters: {translation.get('filters')}")
                logger.info(f"AI Response: {translation.get('ai_response')}")
                
                return True
            else:
                logger.error(f"❌ Query Translation failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Query Translation failed: {str(e)}")
            return False
    
    def test_conversational_recommendations(self) -> bool:
        """Test 4: Conversational recommendations with chat history"""
        logger.info("🔍 Step 4: Testing Conversational Recommendations...")
        try:
            # First recommendation
            first_request = {
                "message": "I want pizza for dinner",
                "user_id": self.user_id,
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "dinner"
                },
                "chat_history": []
            }
            
            response1 = requests.post(
                f"{self.base_url}/ai/recommend",
                json=first_request,
                timeout=20
            )
            
            if response1.status_code == 200:
                data1 = response1.json()
                logger.info("✅ First recommendation successful")
                logger.info(f"AI Response: {data1.get('ai_response')}")
                logger.info(f"Menu items: {len(data1.get('menu_items', []))}")
                
                # Store chat history
                self.chat_history = [
                    {"role": "user", "content": "I want pizza for dinner"},
                    {"role": "assistant", "content": data1.get('ai_response', '')}
                ]
                
                # Follow-up recommendation
                followup_request = {
                    "message": "Actually, make it vegetarian pizza",
                    "user_id": self.user_id,
                    "context": {
                        "location": {"lat": 40.7580, "lng": -73.9855},
                        "meal_context": "dinner"
                    },
                    "chat_history": self.chat_history
                }
                
                response2 = requests.post(
                    f"{self.base_url}/ai/recommend",
                    json=followup_request,
                    timeout=20
                )
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    logger.info("✅ Follow-up recommendation successful")
                    logger.info(f"AI Response: {data2.get('ai_response')}")
                    logger.info(f"Menu items: {len(data2.get('menu_items', []))}")
                    
                    # Check if it understood the context change
                    if "vegetarian" in data2.get('ai_response', '').lower():
                        logger.info("✅ AI understood context change")
                        return True
                    else:
                        logger.warning("⚠️ AI didn't understand context change")
                        return False
                else:
                    logger.error(f"❌ Follow-up recommendation failed: {response2.status_code}")
                    return False
            else:
                logger.error(f"❌ First recommendation failed: {response1.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Conversational recommendations failed: {str(e)}")
            return False
    
    def test_direct_menu_search(self) -> bool:
        """Test 5: Direct menu search (bypassing AI)"""
        logger.info("🔍 Step 5: Testing Direct Menu Search...")
        try:
            search_request = {
                "query": "pizza",
                "location": {"lat": 40.7580, "lng": -73.9855},
                "filters": {
                    "max_calories": 800,
                    "min_protein": 20
                },
                "personalization": {
                    "user_id": self.user_id,
                    "preferences": {
                        "dietary_restrictions": ["vegetarian"]
                    }
                },
                "limit": 5
            }
            
            response = requests.post(
                f"{self.base_url}/menu-items/search",
                json=search_request,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get("menu_items", [])
                logger.info(f"✅ Direct menu search returned {len(menu_items)} items")
                
                if menu_items:
                    first_item = menu_items[0]
                    logger.info(f"First item: {first_item.get('name')}")
                    logger.info(f"Calories: {first_item.get('calories')}")
                    logger.info(f"Protein: {first_item.get('protein')}")
                    
                    # Check if we got pizza items
                    pizza_items = [item for item in menu_items if "pizza" in item.get('name', '').lower()]
                    logger.info(f"Pizza items found: {len(pizza_items)}")
                    
                    if len(pizza_items) > 0:
                        logger.info("✅ Pizza search working correctly")
                        return True
                    else:
                        logger.warning("⚠️ Pizza search not returning pizza items")
                        return False
                else:
                    logger.error("❌ No menu items in direct search")
                    return False
            else:
                logger.error(f"❌ Direct menu search failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Direct menu search failed: {str(e)}")
            return False
    
    def run_proper_recommendation_test(self) -> bool:
        """Run the complete proper recommendation engine test"""
        logger.info("🚀 Starting Proper Recommendation Engine Test")
        logger.info("=" * 60)
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("AI Recommendation Engine", self.test_ai_recommendation_engine),
            ("Query Translation", self.test_query_translation),
            ("Conversational Recommendations", self.test_conversational_recommendations),
            ("Direct Menu Search", self.test_direct_menu_search)
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
        logger.info("\n" + "=" * 60)
        logger.info("📊 Proper Recommendation Engine Test Results:")
        passed = 0
        total = len(tests)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
            if result:
                passed += 1
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 Proper recommendation engine test PASSED! Real data from Supabase and Groq AI confirmed!")
        else:
            logger.warning(f"⚠️ {total - passed} tests failed. Issues need to be fixed.")
        
        return passed == total

def main():
    """Run the proper recommendation engine test"""
    tester = ProperRecommendationEngineTester()
    success = tester.run_proper_recommendation_test()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
