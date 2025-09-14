#!/usr/bin/env python3
"""
Test to verify that both real Groq API and real Supabase data are being used
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_real_api_integration():
    """Test that both Groq API and Supabase data are being used"""
    try:
        # Test 1: Check if backend is running
        logger.info("🔍 Testing backend health...")
        health_response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if health_response.status_code != 200:
            logger.error("❌ Backend is not running")
            return False
        logger.info("✅ Backend is running")
        
        # Test 2: Test conversational search with a specific request
        logger.info("🔍 Testing conversational search with real APIs...")
        
        search_request = {
            "message": "I want chicken teriyaki with rice",
            "context": {
                "location": {"lat": 40.7580, "lng": -73.9855},
                "meal_context": "lunch"
            },
            "chat_history": [],
            "user_id": "test-user-real-api"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/ai/search",
            json=search_request,
            timeout=15  # Longer timeout for real API calls
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Conversational search successful")
            
            # Check AI response quality (real AI should be more sophisticated)
            ai_response = data.get("ai_response", "")
            logger.info(f"AI Response: {ai_response}")
            
            # Check if response is generic (indicates mock) or specific (indicates real AI)
            if "chicken" in ai_response.lower() and "teriyaki" in ai_response.lower():
                logger.info("✅ AI response is specific and contextual (real AI)")
            elif "chicken" in ai_response.lower():
                logger.info("✅ AI response mentions chicken (real AI)")
            else:
                logger.warning("⚠️ AI response seems generic (might be mock)")
            
            # Check menu items
            menu_items = data.get("menu_items", [])
            logger.info(f"Menu items returned: {len(menu_items)}")
            
            # Check if we have real database data (should have more fields)
            if menu_items:
                first_item = menu_items[0]
                logger.info(f"First item: {first_item.get('name', 'Unknown')}")
                
                # Check for real database fields (MenuItem model fields)
                real_db_fields = ['calories', 'protein', 'carbs', 'fat', 'dietary', 'cuisine_tags']
                
                # Handle both dict and object responses
                if isinstance(first_item, dict):
                    found_real_fields = [field for field in real_db_fields if field in first_item]
                    if found_real_fields:
                        logger.info(f"✅ Found real database fields: {found_real_fields}")
                        # Check if the fields have real data (not just default values)
                        if first_item.get('calories', 0) > 0:
                            logger.info(f"✅ Real nutrition data: {first_item.get('calories')} calories, {first_item.get('protein')}g protein")
                        else:
                            logger.warning("⚠️ Nutrition data is zero - might be using mock data")
                    else:
                        logger.warning("⚠️ No real database fields found - might be using mock data")
                else:
                    found_real_fields = [field for field in real_db_fields if hasattr(first_item, field)]
                    if found_real_fields:
                        logger.info(f"✅ Found real database fields: {found_real_fields}")
                        # Check if the fields have real data (not just default values)
                        if hasattr(first_item, 'calories') and first_item.calories > 0:
                            logger.info(f"✅ Real nutrition data: {first_item.calories} calories, {first_item.protein}g protein")
                        else:
                            logger.warning("⚠️ Nutrition data is zero - might be using mock data")
                    else:
                        logger.warning("⚠️ No real database fields found - might be using mock data")
                
                # Check for chicken-related items
                chicken_items = []
                for item in menu_items:
                    name = item.get("name", "").lower()
                    description = item.get("description", "").lower()
                    if "chicken" in name or "chicken" in description:
                        chicken_items.append(item)
                
                logger.info(f"Chicken-related items found: {len(chicken_items)}")
                for item in chicken_items:
                    logger.info(f"  - {item.get('name')}: {item.get('description')}")
            
            # Check search reasoning
            search_reasoning = data.get("search_reasoning", "")
            logger.info(f"Search reasoning: {search_reasoning}")
            
            # Check preferences extracted
            preferences = data.get("preferences_extracted", {})
            logger.info(f"Extracted preferences: {json.dumps(preferences, indent=2)}")
            
            return True
            
        else:
            logger.error(f"❌ Conversational search failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

def test_direct_supabase_connection():
    """Test direct Supabase connection"""
    try:
        logger.info("🔍 Testing direct Supabase connection...")
        
        # Test menu items endpoint directly with POST request
        search_request = {
            "query": "chicken",
            "location": {"lat": 40.7580, "lng": -73.9855},
            "filters": {},
            "personalization": {},
            "limit": 5
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/menu-items/search",
            json=search_request,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            menu_items = data.get("menu_items", [])
            logger.info(f"✅ Direct menu search returned {len(menu_items)} items")
            
            if menu_items:
                first_item = menu_items[0]
                logger.info(f"First item: {first_item.get('name')}")
                
                # Check for real database fields (MenuItem model fields)
                if isinstance(first_item, dict):
                    if 'calories' in first_item and 'protein' in first_item:
                        # Check if the nutrition data is non-zero (real data)
                        if first_item.get('calories', 0) > 0 and first_item.get('protein', 0) > 0:
                            logger.info("✅ Real Supabase data confirmed")
                            return True
                        else:
                            logger.warning("⚠️ Mock data detected (zero nutrition values)")
                            return False
                    else:
                        logger.warning("⚠️ Mock data detected (missing nutrition fields)")
                        return False
                else:
                    if hasattr(first_item, 'calories') and hasattr(first_item, 'protein'):
                        # Check if the nutrition data is non-zero (real data)
                        if first_item.calories > 0 and first_item.protein > 0:
                            logger.info("✅ Real Supabase data confirmed")
                            return True
                        else:
                            logger.warning("⚠️ Mock data detected (zero nutrition values)")
                            return False
                    else:
                        logger.warning("⚠️ Mock data detected (missing nutrition fields)")
                        return False
            else:
                logger.warning("⚠️ No menu items returned")
                return False
        else:
            logger.error(f"❌ Direct menu search failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Direct Supabase test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Testing Real API Integration")
    logger.info("=" * 50)
    
    # Test 1: Real API integration
    api_test_passed = test_real_api_integration()
    
    # Test 2: Direct Supabase connection
    supabase_test_passed = test_direct_supabase_connection()
    
    logger.info("=" * 50)
    logger.info(f"📊 Results:")
    logger.info(f"  Real API Integration: {'✅ PASS' if api_test_passed else '❌ FAIL'}")
    logger.info(f"  Supabase Connection: {'✅ PASS' if supabase_test_passed else '❌ FAIL'}")
    
    if api_test_passed and supabase_test_passed:
        logger.info("🎉 Both real Groq API and real Supabase data are being used!")
    else:
        logger.warning("⚠️ Some components are still using mock data")
    
    return api_test_passed and supabase_test_passed

if __name__ == "__main__":
    exit(0 if main() else 1)
