#!/usr/bin/env python3
"""
Test the API endpoint to see if location data is being returned correctly
"""

import requests
import json

def test_api_location_data():
    """Test API endpoint for location data"""
    print("🔍 Testing API Endpoint for Location Data")
    print("=" * 50)
    
    try:
        # Test the conversational AI search endpoint
        print("\n🍕 Testing Conversational AI Search for Pizza")
        print("-" * 40)
        
        url = "http://localhost:8000/api/v1/ai/search"
        payload = {
            "message": "I want pizza",
            "context": {
                "location": {"lat": 40.7580, "lng": -73.9855}
            }
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            menu_items = data.get('menu_items', [])
            
            print(f"✅ API returned {len(menu_items)} menu items")
            
            # Check for Nolita Pizza
            nolita_items = [item for item in menu_items if 'nolita' in item.get('restaurant', {}).get('name', '').lower()]
            
            if nolita_items:
                print(f"\n✅ Found {len(nolita_items)} Nolita Pizza items in API response:")
                for item in nolita_items:
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                    print(f"    Location: lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
                    print(f"    Has coordinates: {restaurant.get('lat') is not None and restaurant.get('lng') is not None}")
            else:
                print("❌ No Nolita Pizza items found in API response")
            
            # Check all items for location data
            print(f"\n📍 Location Data Analysis for All {len(menu_items)} API Items:")
            print("-" * 40)
            
            with_coords = [item for item in menu_items if item.get('restaurant', {}).get('lat') is not None and item.get('restaurant', {}).get('lng') is not None]
            without_coords = [item for item in menu_items if item.get('restaurant', {}).get('lat') is None or item.get('restaurant', {}).get('lng') is None]
            
            print(f"Items with coordinates: {len(with_coords)}")
            print(f"Items without coordinates: {len(without_coords)}")
            
            if without_coords:
                print("\n❌ Items WITHOUT coordinates in API response:")
                for item in without_coords[:5]:  # Show first 5
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                    print(f"    lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
            
            # Show sample coordinates
            if with_coords:
                print(f"\n✅ Sample coordinates from {len(with_coords)} API items:")
                for item in with_coords[:5]:  # Show first 5
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                    print(f"    lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
            
            # Test direct menu items search
            print(f"\n🍕 Testing Direct Menu Items Search")
            print("-" * 40)
            
            direct_url = "http://localhost:8000/api/v1/menu-items/search"
            direct_payload = {
                "query": "pizza",
                "location": {"lat": 40.7580, "lng": -73.9855},
                "filters": {}
            }
            
            direct_response = requests.post(direct_url, json=direct_payload)
            
            if direct_response.status_code == 200:
                direct_data = direct_response.json()
                direct_items = direct_data.get('menu_items', [])
                
                print(f"✅ Direct search returned {len(direct_items)} menu items")
                
                # Check for Nolita Pizza in direct search
                direct_nolita = [item for item in direct_items if 'nolita' in item.get('restaurant', {}).get('name', '').lower()]
                
                if direct_nolita:
                    print(f"✅ Found {len(direct_nolita)} Nolita Pizza items in direct search:")
                    for item in direct_nolita:
                        restaurant = item.get('restaurant', {})
                        print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                        print(f"    Location: lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
                else:
                    print("❌ No Nolita Pizza items found in direct search")
            else:
                print(f"❌ Direct search failed: {direct_response.status_code}")
                print(direct_response.text)
        
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
        
        print("\n✅ API location data test complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_location_data()
