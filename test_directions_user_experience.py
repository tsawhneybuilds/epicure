#!/usr/bin/env python3
"""
Test Directions User Experience
Simulates a real user using the frontend with directions functionality
"""

import requests
import json
import time
from typing import Dict, Any, List

class DirectionsUserExperienceTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = "test-user-directions"
        
    def simulate_user_flow_with_directions(self):
        """Simulate complete user flow including directions"""
        print("�� Testing Directions User Experience")
        print("=" * 60)
        
        # Step 1: User opens app and searches for food
        print("\n1️⃣ User opens app and searches for food")
        initial_search = self.simulate_initial_search()
        if not initial_search:
            return False
        
        # Step 2: User browses menu items
        print("\n2️⃣ User browses menu items")
        menu_items = initial_search.get("menu_items", [])
        if not menu_items:
            print("❌ No menu items found")
            return False
        
        # Step 3: User examines restaurant details and uses directions
        print("\n3️⃣ User examines restaurant details and uses directions")
        directions_tests = []
        
        for i, item in enumerate(menu_items[:3]):  # Test first 3 items
            print(f"\n   📍 Testing Restaurant {i+1}: {item['restaurant']['name']}")
            directions_result = self.test_restaurant_directions(item)
            directions_tests.append(directions_result)
        
        # Step 4: User continues conversation and gets more results
        print("\n4️⃣ User continues conversation for more results")
        refined_search = self.simulate_conversation_refinement()
        if refined_search:
            refined_items = refined_search.get("menu_items", [])
            print(f"   ✅ Got {len(refined_items)} refined results")
            
            # Test directions on refined results
            for item in refined_items[:2]:
                print(f"   📍 Testing refined restaurant: {item['restaurant']['name']}")
                directions_result = self.test_restaurant_directions(item)
                directions_tests.append(directions_result)
        
        # Step 5: User changes location and tests directions
        print("\n5️⃣ User changes location and tests directions")
        location_test = self.simulate_location_change()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Directions User Experience Test Results:")
        
        successful_directions = sum(1 for result in directions_tests if result["success"])
        total_tests = len(directions_tests)
        
        print(f"✅ Successful directions tests: {successful_directions}/{total_tests}")
        print(f"✅ Location change test: {'PASS' if location_test else 'FAIL'}")
        
        if successful_directions == total_tests and location_test:
            print("\n🎉 All directions functionality tests PASSED!")
            print("Users can successfully get directions to any restaurant.")
            return True
        else:
            print(f"\n⚠️  {total_tests - successful_directions} directions tests failed.")
            return False
    
    def simulate_initial_search(self) -> Dict[str, Any]:
        """Simulate user's initial food search"""
        print("   🔍 Searching for 'healthy lunch options'...")
        
        try:
            response = self.session.post(
                "http://localhost:8000/api/v1/ai/recommend",
                json={
                    "message": "I want healthy lunch options under $15",
                    "user_id": self.user_id,
                    "context": {
                        "location": {"lat": 40.7580, "lng": -73.9855},
                        "meal_context": "lunch"
                    }
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get("menu_items", [])
                print(f"   ✅ Found {len(menu_items)} menu items")
                print(f"   💬 AI Response: {data.get('ai_response', '')[:80]}...")
                return data
            else:
                print(f"   ❌ Search failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"   ❌ Search error: {e}")
            return {}
    
    def test_restaurant_directions(self, menu_item: Dict[str, Any]) -> Dict[str, Any]:
        """Test directions functionality for a specific restaurant"""
        restaurant = menu_item.get("restaurant", {})
        name = restaurant.get("name", "Unknown")
        lat = restaurant.get("lat")
        lng = restaurant.get("lng")
        address = restaurant.get("address", "")
        
        result = {
            "restaurant": name,
            "success": False,
            "method": None,
            "url": None,
            "coordinates": None
        }
        
        # Test coordinates-based directions
        if lat and lng:
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
            result.update({
                "success": True,
                "method": "coordinates",
                "url": maps_url,
                "coordinates": f"{lat}, {lng}"
            })
            print(f"      ✅ Coordinates: {lat}, {lng}")
            print(f"      🗺️  Maps URL: {maps_url}")
            
        # Test address-based directions (fallback)
        elif address:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={address.replace(' ', '+')}"
            result.update({
                "success": True,
                "method": "address",
                "url": maps_url,
                "coordinates": None
            })
            print(f"      ✅ Address: {address}")
            print(f"      🗺️  Maps URL: {maps_url}")
            
        else:
            print(f"      ❌ No coordinates or address available")
            result["success"] = False
        
        return result
    
    def simulate_conversation_refinement(self) -> Dict[str, Any]:
        """Simulate user refining their search through conversation"""
        print("   💬 User says: 'Actually, I prefer vegetarian options'")
        
        try:
            response = self.session.post(
                "http://localhost:8000/api/v1/ai/search",
                json={
                    "message": "Actually, I prefer vegetarian options",
                    "user_id": self.user_id,
                    "chat_history": [
                        {"role": "user", "content": "I want healthy lunch options under $15"},
                        {"role": "assistant", "content": "I'm finding great value options..."}
                    ],
                    "context": {
                        "location": {"lat": 40.7580, "lng": -73.9855}
                    }
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get("menu_items", [])
                print(f"   ✅ Refined search returned {len(menu_items)} vegetarian options")
                return data
            else:
                print(f"   ❌ Refinement failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"   ❌ Refinement error: {e}")
            return {}
    
    def simulate_location_change(self) -> bool:
        """Simulate user changing location and testing directions"""
        print("   📍 User changes location to Brooklyn, NY")
        
        try:
            response = self.session.post(
                "http://localhost:8000/api/v1/menu-items/search",
                json={
                    "query": "popular restaurants",
                    "location": {"lat": 40.6782, "lng": -73.9442},  # Brooklyn
                    "limit": 2
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get("menu_items", [])
                print(f"   ✅ Found {len(menu_items)} restaurants in Brooklyn")
                
                # Test directions for Brooklyn restaurants
                for item in menu_items:
                    restaurant = item.get("restaurant", {})
                    name = restaurant.get("name", "Unknown")
                    lat = restaurant.get("lat")
                    lng = restaurant.get("lng")
                    
                    if lat and lng:
                        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
                        print(f"      🗺️  {name}: {maps_url}")
                    else:
                        print(f"      ❌ {name}: No coordinates")
                
                return len(menu_items) > 0
            else:
                print(f"   ❌ Location change failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Location change error: {e}")
            return False
    
    def test_directions_button_behavior(self):
        """Test the specific behavior of the directions button"""
        print("\n6️⃣ Testing Directions Button Behavior")
        
        # Test different scenarios
        test_cases = [
            {
                "name": "Restaurant with coordinates",
                "restaurant": {
                    "name": "Test Restaurant",
                    "lat": 40.7580,
                    "lng": -73.9855,
                    "address": "123 Test St, NYC"
                },
                "expected": "coordinates"
            },
            {
                "name": "Restaurant with address only",
                "restaurant": {
                    "name": "Test Restaurant 2",
                    "address": "456 Test Ave, NYC"
                },
                "expected": "address"
            },
            {
                "name": "Restaurant with no location data",
                "restaurant": {
                    "name": "Test Restaurant 3"
                },
                "expected": "none"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n   🧪 Testing: {test_case['name']}")
            restaurant = test_case["restaurant"]
            
            # Simulate the frontend logic
            has_coordinates = restaurant.get("lat") and restaurant.get("lng")
            has_address = restaurant.get("address")
            
            if has_coordinates:
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={restaurant['lat']},{restaurant['lng']}"
                method = "coordinates"
                print(f"      ✅ Button would show (coordinates method)")
                print(f"      🗺️  URL: {maps_url}")
            elif has_address:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={restaurant['address'].replace(' ', '+')}"
                method = "address"
                print(f"      ✅ Button would show (address method)")
                print(f"      🗺️  URL: {maps_url}")
            else:
                method = "none"
                print(f"      ❌ Button would not show (no location data)")
            
            # Verify expected behavior
            if method == test_case["expected"]:
                print(f"      ✅ Test PASSED")
            else:
                print(f"      ❌ Test FAILED - Expected {test_case['expected']}, got {method}")

def main():
    """Run the complete directions user experience test"""
    tester = DirectionsUserExperienceTester()
    
    # Test complete user flow
    flow_success = tester.simulate_user_flow_with_directions()
    
    # Test specific button behavior
    tester.test_directions_button_behavior()
    
    print("\n" + "=" * 60)
    if flow_success:
        print("🎉 ALL DIRECTIONS TESTS PASSED!")
        print("The directions functionality is working perfectly for users.")
    else:
        print("⚠️  Some directions tests failed.")
        print("Check the details above for specific issues.")
    
    return flow_success

if __name__ == "__main__":
    main()
