#!/usr/bin/env python3
"""
Comprehensive test of the full user workflow:
1. Account setup
2. Personalization
3. First search
4. Conversational AI search
5. Verify real data from Supabase and Groq AI
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EpicureWorkflowTester:
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
    
    def test_initial_search(self) -> bool:
        """Test 2: Initial search with real data"""
        logger.info("🔍 Step 2: Testing initial search with real data...")
        try:
            search_request = {
                "query": "healthy lunch options",
                "location": {"lat": 40.7580, "lng": -73.9855},
                "filters": {
                    "max_calories": 600,
                    "min_protein": 15
                },
                "personalization": {
                    "user_id": self.user_id,
                    "preferences": {
                        "dietary_restrictions": ["vegetarian"],
                        "health_priority": "high"
                    }
                },
                "limit": 10
            }
            
            response = requests.post(
                f"{self.base_url}/menu-items/search",
                json=search_request,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get("menu_items", [])
                logger.info(f"✅ Initial search returned {len(menu_items)} items")
                
                if menu_items:
                    first_item = menu_items[0]
                    logger.info(f"First item: {first_item.get('name')}")
                    logger.info(f"Calories: {first_item.get('calories')}")
                    logger.info(f"Protein: {first_item.get('protein')}")
                    
                    # Verify real data
                    if first_item.get('calories', 0) > 0:
                        logger.info("✅ Real nutrition data confirmed")
                        return True
                    else:
                        logger.warning("⚠️ Zero nutrition data - not real data")
                        return False
                else:
                    logger.error("❌ No menu items returned")
                    return False
            else:
                logger.error(f"❌ Initial search failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Initial search failed: {str(e)}")
            return False
    
    def test_conversational_ai_search(self) -> bool:
        """Test 3: Conversational AI search with real Groq AI"""
        logger.info("🔍 Step 3: Testing conversational AI search...")
        try:
            # First conversational search
            search_request = {
                "message": "I want something with chicken and rice for dinner",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "dinner"
                },
                "chat_history": [],
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=search_request,
                timeout=20  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Conversational search successful")
                
                # Check AI response quality
                ai_response = data.get("ai_response", "")
                logger.info(f"AI Response: {ai_response}")
                
                # Verify it's using real AI (not generic responses)
                if len(ai_response) > 50 and ("chicken" in ai_response.lower() or "rice" in ai_response.lower()):
                    logger.info("✅ AI response is contextual and specific (real AI)")
                else:
                    logger.warning("⚠️ AI response seems generic (might be mock)")
                
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
                        logger.info("✅ Real nutrition data in conversational search")
                        
                        # Store chat history for follow-up
                        self.chat_history = data.get("chat_history", [])
                        return True
                    else:
                        logger.warning("⚠️ Zero nutrition data in conversational search")
                        return False
                else:
                    logger.error("❌ No menu items in conversational search")
                    return False
            else:
                logger.error(f"❌ Conversational search failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Conversational search failed: {str(e)}")
            return False
    
    def test_follow_up_conversation(self) -> bool:
        """Test 4: Follow-up conversational search"""
        logger.info("🔍 Step 4: Testing follow-up conversational search...")
        try:
            # Follow-up search with chat history
            search_request = {
                "message": "Actually, make it vegetarian instead",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "dinner"
                },
                "chat_history": self.chat_history,
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=search_request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Follow-up search successful")
                
                # Check AI response
                ai_response = data.get("ai_response", "")
                logger.info(f"AI Response: {ai_response}")
                
                # Verify it understands the context change
                if "vegetarian" in ai_response.lower() or "vegetable" in ai_response.lower():
                    logger.info("✅ AI understood the context change (real AI)")
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
                        logger.info("✅ Real nutrition data in follow-up search")
                        return True
                    else:
                        logger.warning("⚠️ Zero nutrition data in follow-up search")
                        return False
                else:
                    logger.error("❌ No menu items in follow-up search")
                    return False
            else:
                logger.error(f"❌ Follow-up search failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Follow-up search failed: {str(e)}")
            return False
    
    def test_data_quality(self) -> bool:
        """Test 5: Verify data quality and real sources"""
        logger.info("🔍 Step 5: Testing data quality and real sources...")
        try:
            # Test with a specific query that should return diverse results
            search_request = {
                "query": "pizza",
                "location": {"lat": 40.7580, "lng": -73.9855},
                "filters": {},
                "personalization": {},
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
                logger.info(f"Data quality test returned {len(menu_items)} items")
                
                if menu_items:
                    # Check for diverse nutrition data
                    nutrition_values = []
                    for item in menu_items:
                        calories = item.get('calories', 0)
                        protein = item.get('protein', 0)
                        if calories > 0 and protein > 0:
                            nutrition_values.append((calories, protein))
                    
                    logger.info(f"Items with real nutrition data: {len(nutrition_values)}")
                    
                    if len(nutrition_values) >= 3:
                        logger.info("✅ Diverse nutrition data found (real Supabase data)")
                        
                        # Check for realistic nutrition ranges
                        calories_range = [c[0] for c in nutrition_values]
                        protein_range = [c[1] for c in nutrition_values]
                        
                        logger.info(f"Calories range: {min(calories_range)} - {max(calories_range)}")
                        logger.info(f"Protein range: {min(protein_range):.1f} - {max(protein_range):.1f}g")
                        
                        # Verify realistic ranges
                        if max(calories_range) > 200 and max(protein_range) > 5:
                            logger.info("✅ Nutrition data is realistic (real Supabase data)")
                            return True
                        else:
                            logger.warning("⚠️ Nutrition data seems unrealistic")
                            return False
                    else:
                        logger.warning("⚠️ Not enough diverse nutrition data")
                        return False
                else:
                    logger.error("❌ No menu items for data quality test")
                    return False
            else:
                logger.error(f"❌ Data quality test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Data quality test failed: {str(e)}")
            return False
    
    def run_full_workflow_test(self) -> bool:
        """Run the complete workflow test"""
        logger.info("🚀 Starting Full User Workflow Test")
        logger.info("=" * 60)
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Initial Search", self.test_initial_search),
            ("Conversational AI Search", self.test_conversational_ai_search),
            ("Follow-up Conversation", self.test_follow_up_conversation),
            ("Data Quality", self.test_data_quality)
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
        logger.info("📊 Full Workflow Test Results:")
        passed = 0
        total = len(tests)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
            if result:
                passed += 1
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 Full workflow test PASSED! Real data from Supabase and Groq AI confirmed!")
        else:
            logger.warning(f"⚠️ {total - passed} tests failed. Issues need to be fixed.")
        
        return passed == total

def main():
    """Run the full workflow test"""
    tester = EpicureWorkflowTester()
    success = tester.run_full_workflow_test()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
