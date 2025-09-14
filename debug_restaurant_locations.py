#!/usr/bin/env python3
"""
Debug script to check restaurant location data in Supabase
Focus on restaurants like Nolita Pizza that should have lat/lng
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.supabase import get_supabase_client
import json

async def debug_restaurant_locations():
    """Debug restaurant location data"""
    print("🔍 Debugging Restaurant Location Data")
    print("=" * 50)
    
    try:
        supabase = get_supabase_client()
        print("✅ Supabase connection successful")
        
        # Test 1: Check Nolita Pizza specifically
        print("\n📍 Test 1: Nolita Pizza Location Data")
        print("-" * 40)
        
        nolita_query = supabase.table('restaurants').select('*').ilike('name', '%nolita%')
        nolita_result = nolita_query.execute()
        
        if nolita_result.data:
            for restaurant in nolita_result.data:
                print(f"Restaurant: {restaurant.get('name', 'Unknown')}")
                print(f"Location field: {restaurant.get('location', 'None')}")
                print(f"Location type: {type(restaurant.get('location'))}")
                if restaurant.get('location'):
                    location_hex = restaurant.get('location')
                    print(f"Location hex length: {len(location_hex) if location_hex else 0}")
                    print(f"Location hex preview: {location_hex[:50] if location_hex else 'None'}...")
                print()
        else:
            print("❌ No Nolita Pizza found")
        
        # Test 2: Check all restaurants with location data
        print("\n📍 Test 2: All Restaurants with Location Data")
        print("-" * 40)
        
        all_restaurants = supabase.table('restaurants').select('name, location').execute()
        print(f"Total restaurants: {len(all_restaurants.data)}")
        
        with_location = [r for r in all_restaurants.data if r.get('location')]
        without_location = [r for r in all_restaurants.data if not r.get('location')]
        
        print(f"Restaurants with location: {len(with_location)}")
        print(f"Restaurants without location: {len(without_location)}")
        
        if without_location:
            print("\n❌ Restaurants WITHOUT location data:")
            for restaurant in without_location[:10]:  # Show first 10
                print(f"  - {restaurant.get('name', 'Unknown')}")
        
        # Test 3: Sample restaurants with location data
        print("\n📍 Test 3: Sample Restaurants with Location Data")
        print("-" * 40)
        
        for restaurant in with_location[:5]:  # Show first 5
            print(f"Restaurant: {restaurant.get('name', 'Unknown')}")
            location_hex = restaurant.get('location')
            print(f"Location hex: {location_hex[:50]}...")
            
            # Try to parse the PostGIS data
            try:
                if location_hex and len(location_hex) > 18:
                    hex_data = location_hex[18:]  # Remove PostGIS prefix
                    binary_data = bytes.fromhex(hex_data)
                    if len(binary_data) >= 16:
                        import struct
                        lng, lat = struct.unpack('<dd', binary_data[:16])
                        print(f"  Parsed coordinates: lat={lat:.6f}, lng={lng:.6f}")
                    else:
                        print(f"  ❌ Insufficient binary data: {len(binary_data)} bytes")
                else:
                    print(f"  ❌ Invalid hex data length: {len(location_hex) if location_hex else 0}")
            except Exception as e:
                print(f"  ❌ Parse error: {e}")
            print()
        
        # Test 4: Check menu items with restaurant data
        print("\n📍 Test 4: Menu Items with Restaurant Location Data")
        print("-" * 40)
        
        menu_query = supabase.table('menu_items').select('name, restaurants(name, location)').limit(10)
        menu_result = menu_query.execute()
        
        for item in menu_result.data:
            restaurant_data = item.get('restaurants', {})
            restaurant_name = restaurant_data.get('name', 'Unknown')
            location = restaurant_data.get('location')
            
            print(f"Menu item: {item.get('name', 'Unknown')}")
            print(f"Restaurant: {restaurant_name}")
            print(f"Has location: {'Yes' if location else 'No'}")
            
            if location:
                try:
                    if len(location) > 18:
                        hex_data = location[18:]
                        binary_data = bytes.fromhex(hex_data)
                        if len(binary_data) >= 16:
                            import struct
                            lng, lat = struct.unpack('<dd', binary_data[:16])
                            print(f"  Coordinates: lat={lat:.6f}, lng={lng:.6f}")
                except Exception as e:
                    print(f"  Parse error: {e}")
            print()
        
        print("✅ Location debugging complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_restaurant_locations())
