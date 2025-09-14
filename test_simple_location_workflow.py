#!/usr/bin/env python3
"""
Simple test to verify location data is working correctly
"""

import requests
import json

def test_simple_location_workflow():
    """Simple test for location data"""
    print("🔍 Simple Location Data Test")
    print("=" * 40)
    
    try:
        # Test 1: Direct menu search for pizza
        print("\n🍕 Test 1: Direct Pizza Search")
        print("-" * 30)
        
        search_url = "http://localhost:8000/api/v1/menu-items/search"
        search_payload = {
            "query": "pizza",
            "location": {"lat": 40.7580, "lng": -73.9855},
            "filters": {}
        }
        
        response = requests.post(search_url, json=search_payload)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('menu_items', [])
            print(f"✅ Search returned {len(items)} items")
            
            # Check for Nolita Pizza
            nolita_items = [item for item in items if 'nolita' in item.get('restaurant', {}).get('name', '').lower()]
            
            if nolita_items:
                print(f"✅ Found {len(nolita_items)} Nolita Pizza items:")
                for item in nolita_items:
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                    print(f"    Location: lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
                    print(f"    Has coordinates: {restaurant.get('lat') is not None and restaurant.get('lng') is not None}")
            else:
                print("❌ No Nolita Pizza items found")
            
            # Check all items for location data
            with_coords = [item for item in items if item.get('restaurant', {}).get('lat') is not None and item.get('restaurant', {}).get('lng') is not None]
            without_coords = [item for item in items if item.get('restaurant', {}).get('lat') is None or item.get('restaurant', {}).get('lng') is None]
            
            print(f"\n📍 Location Summary:")
            print(f"  Items with coordinates: {len(with_coords)}")
            print(f"  Items without coordinates: {len(without_coords)}")
            
            if without_coords:
                print("\n❌ Items WITHOUT coordinates:")
                for item in without_coords[:3]:
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(response.text)
        
        # Test 2: Conversational AI search
        print("\n💬 Test 2: Conversational AI Search")
        print("-" * 30)
        
        ai_url = "http://localhost:8000/api/v1/ai/search"
        ai_payload = {
            "message": "I want pizza",
            "context": {
                "location": {"lat": 40.7580, "lng": -73.9855}
            }
        }
        
        ai_response = requests.post(ai_url, json=ai_payload)
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            ai_items = ai_data.get('menu_items', [])
            print(f"✅ AI search returned {len(ai_items)} items")
            
            # Check for Nolita Pizza
            ai_nolita = [item for item in ai_items if 'nolita' in item.get('restaurant', {}).get('name', '').lower()]
            
            if ai_nolita:
                print(f"✅ Found {len(ai_nolita)} Nolita Pizza items in AI search:")
                for item in ai_nolita:
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                    print(f"    Location: lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
            else:
                print("❌ No Nolita Pizza items found in AI search")
            
            # Check all items for location data
            ai_with_coords = [item for item in ai_items if item.get('restaurant', {}).get('lat') is not None and item.get('restaurant', {}).get('lng') is not None]
            ai_without_coords = [item for item in ai_items if item.get('restaurant', {}).get('lat') is None or item.get('restaurant', {}).get('lng') is None]
            
            print(f"\n📍 AI Search Location Summary:")
            print(f"  Items with coordinates: {len(ai_with_coords)}")
            print(f"  Items without coordinates: {len(ai_without_coords)}")
        else:
            print(f"❌ AI search failed: {ai_response.status_code}")
            print(ai_response.text)
        
        print("\n✅ Simple location test complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_location_workflow()
