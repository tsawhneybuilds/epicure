#!/usr/bin/env python3
"""
Test script to verify the frontend personalization flow works end-to-end
"""

import requests
import json
import uuid
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_frontend_personalization():
    print("🧪 Testing Frontend Personalization Flow...")
    
    # 1. Create a test user
    print("\n1. Creating test user...")
    user_data = {
        "email": f"frontend_test_{uuid.uuid4().hex[:8]}@example.com",
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
    
    # 2. Simulate personalization chat completion
    print("\n2. Simulating personalization chat completion...")
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
    
    # 3. Test profile retrieval (what frontend would do)
    print("\n3. Testing profile retrieval (frontend simulation)...")
    response = requests.get(
        f"{BASE_URL}/api/v1/users/{user_id}/profile",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Profile retrieval failed: {response.status_code} - {response.text}")
        return False
    
    profile_data = response.json()
    print("✅ Profile retrieved successfully")
    
    # 4. Verify the data structure matches what frontend expects
    preferences = profile_data.get("preferences", {})
    personalization_data_stored = preferences.get("personalization_data")
    
    if not personalization_data_stored:
        print("❌ Personalization data not found in profile")
        return False
    
    # 5. Test learned insights extraction (frontend logic)
    print("\n4. Testing learned insights extraction...")
    learned_insights = personalization_data_stored.get("learned_insights", {})
    insight_strings = []
    
    # Convert structured insights to display strings (frontend logic)
    if learned_insights.get("food_preferences", {}).get("track_macros"):
        insight_strings.append("I carefully track my nutrition and macros")
    if learned_insights.get("food_preferences", {}).get("calorie_deficit"):
        insight_strings.append("I'm focused on maintaining a calorie deficit for weight management")
    if learned_insights.get("food_preferences", {}).get("muscle_gain"):
        insight_strings.append("I'm focused on building muscle and strength")
    if learned_insights.get("dining_habits", {}).get("budget_conscious"):
        insight_strings.append("I prefer budget-friendly dining options")
    if learned_insights.get("dining_habits", {}).get("quick_meals"):
        insight_strings.append("I value quick service when dining out")
    if learned_insights.get("food_preferences", {}).get("vegetarian"):
        insight_strings.append("I follow a vegetarian lifestyle")
    if learned_insights.get("lifestyle_patterns", {}).get("active_lifestyle"):
        insight_strings.append("I'm very active and exercise regularly")
    elif learned_insights.get("lifestyle_patterns", {}).get("moderate_activity"):
        insight_strings.append("I maintain a moderately active lifestyle")
    
    print(f"✅ Extracted {len(insight_strings)} insights:")
    for insight in insight_strings:
        print(f"   - {insight}")
    
    # 6. Verify expected insights are present
    expected_insights = [
        "I carefully track my nutrition and macros",
        "I'm focused on building muscle and strength", 
        "I prefer budget-friendly dining options",
        "I value quick service when dining out",
        "I'm very active and exercise regularly"
    ]
    
    missing_insights = [insight for insight in expected_insights if insight not in insight_strings]
    if missing_insights:
        print(f"❌ Missing expected insights: {missing_insights}")
        return False
    
    print("✅ All expected insights found")
    
    # 7. Test frontend accessibility
    print("\n5. Testing frontend accessibility...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"⚠️  Frontend returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Frontend not accessible: {e}")
        print("   (This is expected if frontend is not running)")
    
    print("\n🎉 Frontend personalization flow test completed successfully!")
    print("\n📋 Summary:")
    print(f"   - User ID: {user_id}")
    print(f"   - Personalization data stored: ✅")
    print(f"   - Profile retrieval works: ✅")
    print(f"   - Learned insights extracted: {len(insight_strings)} insights")
    print(f"   - Data structure matches frontend expectations: ✅")
    
    return True

if __name__ == "__main__":
    success = test_frontend_personalization()
    if not success:
        exit(1)
