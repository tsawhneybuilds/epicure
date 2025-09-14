#!/usr/bin/env python3
"""
Test script to verify the personalization flow works end-to-end
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def test_personalization_flow():
    print("🧪 Testing Personalization Flow...")
    
    # 1. Create a test user
    print("\n1. Creating test user...")
    user_data = {
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "apple_id": None
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/users/create", json=user_data)
    if response.status_code != 200:
        print(f"❌ User creation failed: {response.status_code} - {response.text}")
        return False
    
    user_info = response.json()
    user_id = user_info["user_id"]
    auth_token = user_info["auth_token"]
    print(f"✅ User created: {user_id}")
    
    # 2. Test personalization endpoint
    print("\n2. Testing personalization data storage...")
    personalization_data = {
        "learned_insights": {
            "lifestyle_patterns": {
                "active_lifestyle": True,
                "moderate_activity": False
            },
            "food_preferences": {
                "track_macros": True,
                "calorie_deficit": False,
                "muscle_gain": True,
                "vegetarian": False
            },
            "dining_habits": {
                "quick_meals": True,
                "budget_conscious": True
            },
            "health_goals": {
                "weight_loss": False,
                "muscle_gain": True,
                "macro_tracking": True
            },
            "confidence_scores": {
                "lifestyle_patterns": 0.8,
                "food_preferences": 0.9,
                "dining_habits": 0.7,
                "health_goals": 0.9
            },
            "source": "conversation"
        },
        "conversation_points": [
            {
                "role": "user",
                "content": "I want to build muscle and track my macros",
                "timestamp": "2024-01-15T10:00:00Z"
            },
            {
                "role": "ai", 
                "content": "Great! I'll help you find high-protein options.",
                "timestamp": "2024-01-15T10:00:01Z"
            }
        ],
        "interaction_patterns": {
            "goals_mentioned": ["Muscle gain", "Track macros"],
            "data_collected": {
                "trackMacros": True,
                "muscleGain": True,
                "budgetFriendly": True,
                "quickService": True
            }
        },
        "fallback_questions_asked": [
            "What are your main fitness goals?",
            "Do you track your nutrition?"
        ]
    }
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(
        f"{BASE_URL}/api/v1/users/{user_id}/personalization",
        json=personalization_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Personalization storage failed: {response.status_code} - {response.text}")
        return False
    
    print("✅ Personalization data stored successfully")
    
    # 3. Retrieve user profile to verify data is stored
    print("\n3. Retrieving user profile to verify storage...")
    response = requests.get(
        f"{BASE_URL}/api/v1/users/{user_id}/profile",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Profile retrieval failed: {response.status_code} - {response.text}")
        return False
    
    profile_data = response.json()
    print("✅ Profile retrieved successfully")
    
    # 4. Check if personalization data is in profile extensions
    preferences = profile_data.get("preferences", {})
    personalization_stored = preferences.get("personalization_data")
    
    if personalization_stored:
        print("✅ Personalization data found in profile extensions")
        print(f"   - Learned insights: {personalization_stored.get('learned_insights', {}).get('source', 'N/A')}")
        print(f"   - Conversation points: {len(personalization_stored.get('conversation_points', []))} messages")
        print(f"   - Goals mentioned: {personalization_stored.get('interaction_patterns', {}).get('goals_mentioned', [])}")
    else:
        print("❌ Personalization data not found in profile extensions")
        print(f"   Available keys: {list(preferences.keys())}")
        return False
    
    # 5. Test that learned insights are properly structured
    learned_insights = personalization_stored.get("learned_insights", {})
    if learned_insights.get("food_preferences", {}).get("track_macros"):
        print("✅ Macro tracking preference correctly stored")
    else:
        print("❌ Macro tracking preference not found")
        return False
    
    if learned_insights.get("food_preferences", {}).get("muscle_gain"):
        print("✅ Muscle gain preference correctly stored")
    else:
        print("❌ Muscle gain preference not found")
        return False
    
    print("\n🎉 Personalization flow test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_personalization_flow()
    if not success:
        exit(1)
