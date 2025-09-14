#!/usr/bin/env python3
"""
Backend Endpoint Tests
Quick tests to verify the conversational AI endpoints are working
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_conversational_search_endpoint():
    """Test the conversational search endpoint"""
    try:
        logger.info("🧪 Testing /conversational/search endpoint...")
        
        request_data = {
            "message": "I want healthy food for lunch",
            "context": {
                "location": {"lat": 40.7580, "lng": -73.9855},
                "meal_context": "lunch"
            },
            "chat_history": [],
            "user_id": "test-user-123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/ai/search",
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Conversational search endpoint working")
            logger.info(f"   Response keys: {list(data.keys())}")
            logger.info(f"   Menu items: {len(data.get('menu_items', []))}")
            logger.info(f"   AI response: {data.get('ai_response', '')[:100]}...")
            return True
        else:
            logger.error(f"❌ Conversational search failed: {response.status_code}")
            logger.error(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Conversational search test failed: {str(e)}")
        return False

def test_ai_recommendation_endpoint():
    """Test the AI recommendation endpoint"""
    try:
        logger.info("🧪 Testing /ai/recommend endpoint...")
        
        request_data = {
            "message": "Show me some food options",
            "context": {
                "location": {"lat": 40.7580, "lng": -73.9855}
            },
            "chat_history": [],
            "user_id": "test-user-123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/ai/recommend",
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ AI recommendation endpoint working")
            logger.info(f"   Response keys: {list(data.keys())}")
            logger.info(f"   Menu items: {len(data.get('menu_items', []))}")
            return True
        else:
            logger.error(f"❌ AI recommendation failed: {response.status_code}")
            logger.error(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ AI recommendation test failed: {str(e)}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        logger.info("🧪 Testing /health endpoint...")
        
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        
        if response.status_code == 200:
            logger.info("✅ Health endpoint working")
            return True
        else:
            logger.error(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Health endpoint test failed: {str(e)}")
        return False

def main():
    """Run all endpoint tests"""
    logger.info("🚀 Testing Backend Endpoints")
    logger.info("=" * 50)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Conversational Search", test_conversational_search_endpoint),
        ("AI Recommendation", test_ai_recommendation_endpoint),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    logger.info("=" * 50)
    logger.info(f"📊 Results: {passed}/{len(tests)} endpoints working")
    
    if passed == len(tests):
        logger.info("🎉 All endpoints are working correctly!")
    else:
        logger.warning("⚠️  Some endpoints are not working. Check the logs above.")
    
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    exit(main())
