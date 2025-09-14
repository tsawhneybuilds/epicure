#!/usr/bin/env python3
"""
API Testing Script for Epicure Backend
Test all endpoints to ensure they work correctly
"""

import asyncio
import json
import httpx
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def test_endpoint(client: httpx.AsyncClient, method: str, url: str, data: Dict[Any, Any] = None):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=data)
        elif method == "PUT":
            response = await client.put(url, json=data)
        elif method == "PATCH":
            response = await client.patch(url, json=data)
        elif method == "DELETE":
            response = await client.delete(url)
        
        status_emoji = "✅" if response.status_code < 400 else "❌"
        print(f"{status_emoji} {method} {url} -> {response.status_code}")
        
        if response.status_code >= 400:
            print(f"   Error: {response.text[:100]}")
        else:
            # Show sample response data
            try:
                json_data = response.json()
                if isinstance(json_data, dict):
                    if "restaurants" in json_data:
                        print(f"   Found {len(json_data['restaurants'])} restaurants")
                    elif "message" in json_data:
                        print(f"   Message: {json_data['message']}")
                    elif "status" in json_data:
                        print(f"   Status: {json_data['status']}")
            except:
                print(f"   Response: {response.text[:50]}...")
        
        return response.status_code < 400
        
    except Exception as e:
        print(f"❌ {method} {url} -> Error: {e}")
        return False

async def test_all_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing Epicure Backend API")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test basic endpoints
        print("\n📍 Basic Endpoints")
        await test_endpoint(client, "GET", f"{BASE_URL}/")
        await test_endpoint(client, "GET", f"{BASE_URL}/health")
        
        # Test restaurant endpoints
        print("\n🍽️ Restaurant Endpoints")
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/restaurants/stats")
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/restaurants/categories")
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/restaurants/debug/mock-data")
        
        # Test restaurant search
        search_data = {
            "query": "healthy lunch",
            "location": {"lat": 40.7580, "lng": -73.9855},
            "filters": {"max_price": 3},
            "limit": 5
        }
        await test_endpoint(client, "POST", f"{BASE_URL}/api/v1/restaurants/search", search_data)
        
        # Test nearby restaurants
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/restaurants/nearby?lat=40.7580&lng=-73.9855&radius=2.0&limit=5")
        
        # Test user endpoints
        print("\n👤 User Endpoints")
        user_data = {"email": "test@example.com"}
        await test_endpoint(client, "POST", f"{BASE_URL}/api/v1/users/create", user_data)
        
        test_user_id = "test-user-123"
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/users/{test_user_id}/profile")
        
        profile_data = {"age": 28, "activity_level": "moderate"}
        await test_endpoint(client, "PUT", f"{BASE_URL}/api/v1/users/{test_user_id}/profile", profile_data)
        
        prefs_data = {"preferences": {"budgetFriendly": True}}
        await test_endpoint(client, "PATCH", f"{BASE_URL}/api/v1/users/{test_user_id}/preferences", prefs_data)
        
        swipe_data = {"restaurant_id": "123", "action": "like"}
        await test_endpoint(client, "POST", f"{BASE_URL}/api/v1/users/{test_user_id}/interactions/swipe", swipe_data)
        
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/users/{test_user_id}/interactions/liked")
        
        # Test chat endpoints
        print("\n💬 Chat Endpoints")
        chat_data = {
            "message": "I want healthy food for lunch under $15",
            "context": {"location": {"lat": 40.7580, "lng": -73.9855}, "meal_time": "lunch"}
        }
        await test_endpoint(client, "POST", f"{BASE_URL}/api/v1/chat/message", chat_data)
        
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/chat/{test_user_id}/history")
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/chat/debug/ai-status")
        
        pref_extract_data = {"message": "I'm vegan and want something spicy"}
        await test_endpoint(client, "POST", f"{BASE_URL}/api/v1/chat/extract-preferences", pref_extract_data)
        
        # Test health endpoints
        print("\n🏥 Health Endpoints")
        health_data = {
            "source": "apple_health",
            "data": {
                "basic_info": {"age": 28, "weight_kg": 70, "height_cm": 175},
                "activity": {"activity_level": "moderate"},
                "nutrition": {"avg_protein_g": 120}
            }
        }
        await test_endpoint(client, "POST", f"{BASE_URL}/api/v1/health/import", health_data)
        await test_endpoint(client, "POST", f"{BASE_URL}/api/v1/health/preview", health_data)
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/health/{test_user_id}/connections")
        await test_endpoint(client, "GET", f"{BASE_URL}/api/v1/health/debug/mock-health-data")

async def test_frontend_compatibility():
    """Test that responses match frontend TypeScript interfaces"""
    print("\n🔗 Frontend Compatibility Tests")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test restaurant search response format
        search_data = {
            "query": "test",
            "location": {"lat": 40.7580, "lng": -73.9855},
            "limit": 1
        }
        
        response = await client.post(f"{BASE_URL}/api/v1/restaurants/search", json=search_data)
        
        if response.status_code == 200:
            data = response.json()
            restaurants = data.get("restaurants", [])
            
            if restaurants:
                restaurant = restaurants[0]
                required_fields = ["id", "name", "cuisine", "image", "distance", "price", "rating"]
                
                print("🔍 Checking restaurant response format:")
                for field in required_fields:
                    if field in restaurant:
                        print(f"   ✅ {field}: {type(restaurant[field]).__name__}")
                    else:
                        print(f"   ❌ Missing field: {field}")
                
                # Check if response matches frontend interface
                frontend_compatible = all(field in restaurant for field in required_fields)
                status = "✅" if frontend_compatible else "❌"
                print(f"{status} Frontend compatibility: {'PASS' if frontend_compatible else 'FAIL'}")
            else:
                print("❌ No restaurants in response")
        else:
            print(f"❌ Search failed: {response.status_code}")

async def main():
    """Main test runner"""
    print("🚀 Starting API tests...")
    print("💡 Make sure the backend is running on http://localhost:8000")
    
    try:
        await test_all_endpoints()
        await test_frontend_compatibility()
        
        print("\n" + "=" * 50)
        print("🎉 API testing completed!")
        print("💡 Check the output above for any failed tests")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
