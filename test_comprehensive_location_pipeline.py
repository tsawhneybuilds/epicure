#!/usr/bin/env python3
"""
Comprehensive test to verify the entire location data pipeline
from database to frontend display
"""

import requests
import json
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.supabase import get_supabase_client
from backend.app.services.menu_item_service import MenuItemService
from backend.app.models.menu_item import MenuItemSearchRequest

async def test_comprehensive_location_pipeline():
    """Test the complete location data pipeline"""
    print("🔍 Comprehensive Location Data Pipeline Test")
    print("=" * 60)
    
    try:
        # Test 1: Database Level - Raw Supabase Data
        print("\n🗄️ Test 1: Database Level - Raw Supabase Data")
        print("-" * 50)
        
        supabase = get_supabase_client()
        
        # Get Nolita Pizza from database
        nolita_query = supabase.table('restaurants').select('*').ilike('name', '%nolita pizza%').limit(1)
        nolita_result = nolita_query.execute()
        
        if nolita_result.data:
            restaurant = nolita_result.data[0]
            print(f"✅ Found restaurant: {restaurant.get('name')}")
            print(f"   Location field: {restaurant.get('location')}")
            
            # Parse PostGIS data
            location_hex = restaurant.get('location')
            if location_hex and len(location_hex) > 18:
                hex_data = location_hex[18:]
                binary_data = bytes.fromhex(hex_data)
                if len(binary_data) >= 16:
                    import struct
                    lng, lat = struct.unpack('<dd', binary_data[:16])
                    print(f"   Parsed coordinates: lat={lat:.6f}, lng={lng:.6f}")
                else:
                    print(f"   ❌ Insufficient binary data: {len(binary_data)} bytes")
            else:
                print(f"   ❌ Invalid hex data length: {len(location_hex) if location_hex else 0}")
        else:
            print("❌ Nolita Pizza not found in database")
            return
        
        # Test 2: Service Level - Menu Item Service
        print("\n🔧 Test 2: Service Level - Menu Item Service")
        print("-" * 50)
        
        service = MenuItemService()
        request = MenuItemSearchRequest(
            query="Nolita Pizza",
            location={"lat": 40.7580, "lng": -73.9855},
            filters={}
        )
        
        result = await service.search_menu_items(request)
        nolita_items = [item for item in result.menu_items if 'nolita' in item.restaurant.name.lower()]
        
        if nolita_items:
            print(f"✅ Service found {len(nolita_items)} Nolita Pizza items:")
            for item in nolita_items:
                print(f"   - {item.name} at {item.restaurant.name}")
                print(f"     Location: lat={item.restaurant.lat}, lng={item.restaurant.lng}")
                print(f"     Has coordinates: {item.restaurant.lat is not None and item.restaurant.lng is not None}")
        else:
            print("❌ Service did not find Nolita Pizza items")
        
        # Test 3: API Level - Direct Menu Items Search
        print("\n🌐 Test 3: API Level - Direct Menu Items Search")
        print("-" * 50)
        
        direct_url = "http://localhost:8000/api/v1/menu-items/search"
        direct_payload = {
            "query": "Nolita Pizza",
            "location": {"lat": 40.7580, "lng": -73.9855},
            "filters": {}
        }
        
        direct_response = requests.post(direct_url, json=direct_payload)
        
        if direct_response.status_code == 200:
            direct_data = direct_response.json()
            direct_items = direct_data.get('menu_items', [])
            print(f"✅ Direct API returned {len(direct_items)} items")
            
            nolita_api = [item for item in direct_items if 'nolita' in item.get('restaurant', {}).get('name', '').lower()]
            
            if nolita_api:
                print(f"✅ API found {len(nolita_api)} Nolita Pizza items:")
                for item in nolita_api:
                    restaurant = item.get('restaurant', {})
                    print(f"   - {item.get('name')} at {restaurant.get('name')}")
                    print(f"     Location: lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
                    print(f"     Has coordinates: {restaurant.get('lat') is not None and restaurant.get('lng') is not None}")
            else:
                print("❌ API did not find Nolita Pizza items")
        else:
            print(f"❌ Direct API failed: {direct_response.status_code}")
        
        # Test 4: API Level - Conversational AI Search
        print("\n🤖 Test 4: API Level - Conversational AI Search")
        print("-" * 50)
        
        ai_url = "http://localhost:8000/api/v1/ai/search"
        ai_payload = {
            "message": "I want pizza from Nolita Pizza",
            "context": {
                "location": {"lat": 40.7580, "lng": -73.9855}
            }
        }
        
        ai_response = requests.post(ai_url, json=ai_payload)
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            ai_items = ai_data.get('menu_items', [])
            print(f"✅ AI API returned {len(ai_items)} items")
            
            nolita_ai = [item for item in ai_items if 'nolita' in item.get('restaurant', {}).get('name', '').lower()]
            
            if nolita_ai:
                print(f"✅ AI API found {len(nolita_ai)} Nolita Pizza items:")
                for item in nolita_ai:
                    restaurant = item.get('restaurant', {})
                    print(f"   - {item.get('name')} at {restaurant.get('name')}")
                    print(f"     Location: lat={restaurant.get('lat')}, lng={restaurant.get('lng')}")
                    print(f"     Has coordinates: {restaurant.get('lat') is not None and restaurant.get('lng') is not None}")
            else:
                print("❌ AI API did not find Nolita Pizza items")
        else:
            print(f"❌ AI API failed: {ai_response.status_code}")
        
        # Test 5: Frontend Simulation - Check Data Structure
        print("\n💻 Test 5: Frontend Simulation - Data Structure Check")
        print("-" * 50)
        
        # Simulate what the frontend receives
        if direct_response.status_code == 200:
            frontend_data = direct_response.json()
            menu_items = frontend_data.get('menu_items', [])
            
            print(f"✅ Frontend would receive {len(menu_items)} items")
            
            # Check data structure for frontend compatibility
            for i, item in enumerate(menu_items[:3]):  # Check first 3 items
                restaurant = item.get('restaurant', {})
                print(f"\n   Item {i+1}: {item.get('name')}")
                print(f"   Restaurant: {restaurant.get('name')}")
                print(f"   Has lat: {restaurant.get('lat') is not None}")
                print(f"   Has lng: {restaurant.get('lng') is not None}")
                print(f"   Has address: {restaurant.get('address') is not None}")
                
                # Check if directions button would be shown
                has_coords = restaurant.get('lat') is not None and restaurant.get('lng') is not None
                has_address = restaurant.get('address') is not None
                directions_available = has_coords or has_address
                
                print(f"   Directions button available: {directions_available}")
                
                if has_coords:
                    print(f"   Google Maps URL: https://www.google.com/maps/dir/?api=1&destination={restaurant.get('lat')},{restaurant.get('lng')}")
        
        # Test 6: Sample Multiple Restaurants
        print("\n🏪 Test 6: Sample Multiple Restaurants")
        print("-" * 50)
        
        pizza_request = MenuItemSearchRequest(
            query="pizza",
            location={"lat": 40.7580, "lng": -73.9855},
            filters={}
        )
        
        pizza_result = await service.search_menu_items(pizza_request)
        
        print(f"✅ Pizza search returned {len(pizza_result.menu_items)} items")
        
        # Check location data for all items
        with_coords = [item for item in pizza_result.menu_items if item.restaurant.lat is not None and item.restaurant.lng is not None]
        without_coords = [item for item in pizza_result.menu_items if item.restaurant.lat is None or item.restaurant.lng is None]
        
        print(f"   Items with coordinates: {len(with_coords)}")
        print(f"   Items without coordinates: {len(without_coords)}")
        
        if without_coords:
            print("\n   ❌ Items WITHOUT coordinates:")
            for item in without_coords[:5]:
                print(f"     - {item.name} at {item.restaurant.name}")
        
        print(f"\n   ✅ Sample coordinates from {len(with_coords)} items:")
        for item in with_coords[:5]:
            print(f"     - {item.name} at {item.restaurant.name}")
            print(f"       lat={item.restaurant.lat:.6f}, lng={item.restaurant.lng:.6f}")
        
        print("\n✅ Comprehensive location pipeline test complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_location_pipeline())
