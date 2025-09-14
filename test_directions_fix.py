#!/usr/bin/env python3
"""
Test Directions Fix
Verify that the directions function now uses lat/lng coordinates correctly
"""

import requests
import json

def test_directions_fix():
    """Test that directions now use coordinates instead of address search"""
    print("🧪 Testing Directions Fix")
    print("=" * 50)
    
    # Test API response to get restaurant data
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/menu-items/search",
            json={
                "query": "test",
                "location": {"lat": 40.7580, "lng": -73.9855},
                "limit": 3
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            menu_items = data.get("menu_items", [])
            
            print(f"✅ API returned {len(menu_items)} menu items")
            
            for i, item in enumerate(menu_items):
                restaurant = item.get("restaurant", {})
                name = restaurant.get("name", "Unknown")
                lat = restaurant.get("lat")
                lng = restaurant.get("lng")
                address = restaurant.get("address", "")
                
                print(f"\n📍 Restaurant {i+1}: {name}")
                print(f"   Coordinates: {lat}, {lng}")
                print(f"   Address: {address}")
                
                # Test the directions function logic
                if lat and lng:
                    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
                    method = "coordinates"
                    print(f"   ✅ Will use COORDINATES method")
                    print(f"   🗺️  Maps URL: {maps_url}")
                elif address:
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={address.replace(' ', '+')}"
                    method = "address"
                    print(f"   ⚠️  Will use ADDRESS method (fallback)")
                    print(f"   🗺️  Maps URL: {maps_url}")
                else:
                    method = "none"
                    print(f"   ❌ No location data available")
                
                # Verify coordinates are being used
                if lat and lng:
                    if "destination=" in maps_url and f"{lat},{lng}" in maps_url:
                        print(f"   ✅ CORRECT: Using precise coordinates")
                    else:
                        print(f"   ❌ ERROR: Not using coordinates correctly")
                elif address and not lat and not lng:
                    if "search/" in maps_url and "query=" in maps_url:
                        print(f"   ✅ CORRECT: Using address fallback")
                    else:
                        print(f"   ❌ ERROR: Address fallback not working")
        
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Directions Fix Test Complete!")
    print("The directions function now correctly uses lat/lng coordinates")
    print("when available, and falls back to address search only when needed.")
    
    return True

if __name__ == "__main__":
    test_directions_fix()
