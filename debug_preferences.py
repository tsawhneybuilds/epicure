#!/usr/bin/env python3
"""
Debug script to see what preferences are extracted for chicken request
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_preferences_extraction():
    """Test what preferences are extracted for chicken request"""
    try:
        # Test the AI service directly
        ai_request = {
            "message": "i want chicken",
            "context": {
                "location": {"lat": 40.7580, "lng": -73.9855},
                "meal_context": "lunch"
            }
        }
        
        logger.info("🔍 Testing AI preferences extraction...")
        
        response = requests.post(
            "http://localhost:8000/api/v1/ai/extract-preferences",
            json=ai_request,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Preferences extracted successfully")
            logger.info(f"Extracted preferences: {json.dumps(data, indent=2)}")
            return data
        else:
            logger.error(f"❌ Preferences extraction failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return None

if __name__ == "__main__":
    test_preferences_extraction()
