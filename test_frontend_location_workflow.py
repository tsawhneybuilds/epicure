#!/usr/bin/env python3
"""
Test the complete frontend workflow to ensure location data flows through correctly
"""

import requests
import json
import time

def test_frontend_workflow():
    """Test complete frontend workflow with location data"""
    print("🔍 Testing Complete Frontend Workflow with Location Data")
    print("=" * 60)
    
    try:
        # Step 1: Create user
        print("\n👤 Step 1: Creating User")
        print("-" * 30)
        
        create_user_url = "http://localhost:8000/api/v1/users/create"
        create_user_payload = {
            "email": "test@example.com",
            "name": "Test User"
        }
        
        user_response = requests.post(create_user_url, json=create_user_payload)
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            user_id = user_data.get('user_id')
            print(f"✅ User created: {user_id}")
        else:
            print(f"❌ User creation failed: {user_response.status_code}")
            return
        
        # Step 2: Initial search for pizza
        print("\n🍕 Step 2: Initial Pizza Search")
        print("-" * 30)
        
        initial_search_url = "http://localhost:8000/api/v1/menu-items/search"
        initial_search_payload = {
            "query": "pizza",
            "location": {"lat": 40.7580, "lng": -73.9855},
            "filters": {}
        }
        
        initial_response = requests.post(initial_search_url, json=initial_search_payload)
        
        if initial_response.status_code == 200:
            initial_data = initial_response.json()
            initial_items = initial_data.get('menu_items', [])
            print(f"✅ Initial search returned {len(initial_items)} items")
            
            # Check for Nolita Pizza in initial search
            nolita_initial = [item for item in initial_items if 'nolita' in item.get('restaurant', {}).get('name', '').lower()]
            
            if nolita_initial:
                print(f"✅ Found {len(nolita_initial)} Nolita Pizza items in initial search:")
                for item in nolita_initial:
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                    print(f"    Location: lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
                    print(f"    Has coordinates: {restaurant.get('lat') is not None and restaurant.get('lng') is not None}")
            else:
                print("❌ No Nolita Pizza items found in initial search")
        else:
            print(f"❌ Initial search failed: {initial_response.status_code}")
            return
        
        # Step 3: Simulate some swipes
        print("\n👆 Step 3: Simulating Swipes")
        print("-" * 30)
        
        swipe_url = f"http://localhost:8000/api/v1/menu-items/interactions/swipe"
        
        # Like a few items
        for i, item in enumerate(initial_items[:3]):
            swipe_payload = {
                "menu_item_id": item.get('id'),
                "action": "like"
            }
            
            swipe_response = requests.post(swipe_url, json=swipe_payload)
            if swipe_response.status_code == 200:
                print(f"✅ Liked: {item.get('name', 'Unknown')}")
            else:
                print(f"❌ Swipe failed for: {item.get('name', 'Unknown')}")
        
        # Step 4: Conversational AI search
        print("\n💬 Step 4: Conversational AI Search")
        print("-" * 30)
        
        conversational_url = "http://localhost:8000/api/v1/ai/search"
        conversational_payload = {
            "message": "I want more pizza options",
            "context": {
                "location": {"lat": 40.7580, "lng": -73.9855},
                "user_id": user_id
            }
        }
        
        conversational_response = requests.post(conversational_url, json=conversational_payload)
        
        if conversational_response.status_code == 200:
            conversational_data = conversational_response.json()
            conversational_items = conversational_data.get('menu_items', [])
            print(f"✅ Conversational search returned {len(conversational_items)} items")
            
            # Check for Nolita Pizza in conversational search
            nolita_conversational = [item for item in conversational_items if 'nolita' in item.get('restaurant', {}).get('name', '').lower()]
            
            if nolita_conversational:
                print(f"✅ Found {len(nolita_conversational)} Nolita Pizza items in conversational search:")
                for item in nolita_conversational:
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                    print(f"    Location: lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
                    print(f"    Has coordinates: {restaurant.get('lat') is not None and restaurant.get('lng') is not None}")
            else:
                print("❌ No Nolita Pizza items found in conversational search")
            
            # Check all items for location data
            print(f"\n📍 Location Data Analysis for All {len(conversational_items)} Conversational Items:")
            print("-" * 50)
            
            with_coords = [item for item in conversational_items if item.get('restaurant', {}).get('lat') is not None and item.get('restaurant', {}).get('lng') is not None]
            without_coords = [item for item in conversational_items if item.get('restaurant', {}).get('lat') is None or item.get('restaurant', {}).get('lng') is None]
            
            print(f"Items with coordinates: {len(with_coords)}")
            print(f"Items without coordinates: {len(without_coords)}")
            
            if without_coords:
                print("\n❌ Items WITHOUT coordinates in conversational search:")
                for item in without_coords[:5]:  # Show first 5
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                    print(f"    lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
            
            # Show sample coordinates
            if with_coords:
                print(f"\n✅ Sample coordinates from {len(with_coords)} conversational items:")
                for item in with_coords[:5]:  # Show first 5
                    restaurant = item.get('restaurant', {})
                    print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                    print(f"    lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
        else:
            print(f"❌ Conversational search failed: {conversational_response.status_code}")
            print(conversational_response.text)
        
        # Step 5: Test specific search for Nolita Pizza
        print("\n🍕 Step 5: Specific Nolita Pizza Search")
        print("-" * 30)
        
        nolita_search_payload = {
            "query": "Nolita Pizza",
            "location": {"lat": 40.7580, "lng": -73.9855},
            "filters": {}
        }
        
        nolita_search_response = requests.post(initial_search_url, json=nolita_search_payload)
        
        if nolita_search_response.status_code == 200:
            nolita_search_data = nolita_search_response.json()
            nolita_search_items = nolita_search_data.get('menu_items', [])
            print(f"✅ Nolita Pizza search returned {len(nolita_search_items)} items")
            
            # Check all items for location data
            for item in nolita_search_items:
                restaurant = item.get('restaurant', {})
                print(f"  - {item.get('name', 'Unknown')} at {restaurant.get('name', 'Unknown')}")
                print(f"    Location: lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
                print(f"    Has coordinates: {restaurant.get('lat') is not None and restaurant.get('lng') is not None}")
        else:
            print(f"❌ Nolita Pizza search failed: {nolita_search_response.status_code}")
        
        print("\n✅ Frontend workflow test complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_workflow()
