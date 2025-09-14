#!/usr/bin/env python3
"""
Test the PostGIS location parsing in the menu item service
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.menu_item_service import MenuItemService
from backend.app.models.menu_item import MenuItemSearchRequest

async def test_location_parsing():
    """Test location parsing in menu item service"""
    print("🔍 Testing Location Parsing in Menu Item Service")
    print("=" * 50)
    
    try:
        service = MenuItemService()
        
        # Test search for pizza (should include Nolita Pizza)
        print("\n🍕 Testing Pizza Search (should include Nolita Pizza)")
        print("-" * 40)
        
        request = MenuItemSearchRequest(
            query="pizza",
            location={"lat": 40.7580, "lng": -73.9855},
            filters={}
        )
        
        result = await service.search_menu_items(request)
        
        print(f"Found {len(result.menu_items)} menu items")
        
        # Check for Nolita Pizza specifically
        nolita_items = [item for item in result.menu_items if 'nolita' in item.restaurant.name.lower()]
        
        if nolita_items:
            print(f"\n✅ Found {len(nolita_items)} Nolita Pizza items:")
            for item in nolita_items:
                print(f"  - {item.name} at {item.restaurant.name}")
                print(f"    Location: lat={item.restaurant.lat}, lng={item.restaurant.lng}")
                print(f"    Has coordinates: {item.restaurant.lat is not None and item.restaurant.lng is not None}")
        else:
            print("❌ No Nolita Pizza items found")
        
        # Check all items for location data
        print(f"\n📍 Location Data Analysis for All {len(result.menu_items)} Items:")
        print("-" * 40)
        
        with_coords = [item for item in result.menu_items if item.restaurant.lat is not None and item.restaurant.lng is not None]
        without_coords = [item for item in result.menu_items if item.restaurant.lat is None or item.restaurant.lng is None]
        
        print(f"Items with coordinates: {len(with_coords)}")
        print(f"Items without coordinates: {len(without_coords)}")
        
        if without_coords:
            print("\n❌ Items WITHOUT coordinates:")
            for item in without_coords[:5]:  # Show first 5
                print(f"  - {item.name} at {item.restaurant.name}")
                print(f"    lat={item.restaurant.lat}, lng={item.restaurant.lng}")
        
        # Show sample coordinates
        if with_coords:
            print(f"\n✅ Sample coordinates from {len(with_coords)} items:")
            for item in with_coords[:5]:  # Show first 5
                print(f"  - {item.name} at {item.restaurant.name}")
                print(f"    lat={item.restaurant.lat:.6f}, lng={item.restaurant.lng:.6f}")
        
        print("\n✅ Location parsing test complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_location_parsing())
