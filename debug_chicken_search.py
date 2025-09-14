#!/usr/bin/env python3
"""
Debug script to test the exact scenario from the user's images
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_chicken_search():
    """Test the exact scenario: user wants chicken"""
    try:
        # Simulate the exact request from the frontend
        search_request = {
            "message": "i want chicken",
            "context": {
                "location": {"lat": 40.7580, "lng": -73.9855},
                "meal_context": "lunch",
                "timestamp": "2024-01-15T12:00:00Z"
            },
            "chat_history": [
                {"role": "user", "content": "i want healthy food for lunch"},
                {"role": "assistant", "content": "Great choice! I've curated healthy menu items with balanced nutrition and clean ingredients."},
                {"role": "user", "content": "Actually, I want something with more protein"},
                {"role": "assistant", "content": "Perfect! I found high-protein options that align with your fitness goals."},
                {"role": "user", "content": "Can you show me vegetarian options instead?"},
                {"role": "assistant", "content": "Excellent! I'm showing you delicious vegetarian options with rich flavors."},
                {"role": "user", "content": "Actually, I want something quick and cheap"},
                {"role": "assistant", "content": "I understand you're in a rush! Here are quick-prep options with short wait times."},
                {"role": "user", "content": "What about Asian food?"},
                {"role": "assistant", "content": "I've found some amazing dishes based on your preferences!"}
            ],
            "user_id": "demo-user-123"
        }
        
        logger.info("🔍 Testing chicken search request...")
        logger.info(f"Request: {json.dumps(search_request, indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/api/v1/ai/search",
            json=search_request,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ API Response received")
            logger.info(f"Response keys: {list(data.keys())}")
            
            # Check AI response
            ai_response = data.get("ai_response", "")
            logger.info(f"AI Response: {ai_response}")
            
            # Check menu items
            menu_items = data.get("menu_items", [])
            logger.info(f"Menu items count: {len(menu_items)}")
            
            # Check if any menu items contain chicken
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
            
            # Check if the response acknowledges the chicken request
            if "chicken" in ai_response.lower():
                logger.info("✅ AI response acknowledges chicken request")
            else:
                logger.warning("⚠️ AI response doesn't mention chicken")
            
            return data
            
        else:
            logger.error(f"❌ API call failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return None

if __name__ == "__main__":
    test_chicken_search()
