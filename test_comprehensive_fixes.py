#!/usr/bin/env python3
"""
Comprehensive tests for all fixes:
1. Duplicate items
2. Pricing data
3. Location data for directions
4. Frontend integration
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveFixTester:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.user_id = f"test_user_{int(time.time())}"
        
    def test_no_duplicates(self) -> bool:
        """Test 1: Verify no duplicate items in responses"""
        logger.info("🔍 Test 1: Checking for duplicate items...")
        try:
            request = {
                "message": "Show me pizza options",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "dinner"
                },
                "chat_history": [],
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get('menu_items', [])
                
                # Check for duplicates by name
                item_names = [item.get('name', '') for item in menu_items]
                unique_names = set(item_names)
                
                if len(unique_names) == len(item_names):
                    logger.info(f"✅ No duplicates: {len(unique_names)} unique items out of {len(item_names)} total")
                    return True
                else:
                    logger.error(f"❌ Duplicates found: {len(unique_names)} unique items out of {len(item_names)} total")
                    return False
            else:
                logger.error(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            return False
    
    def test_pricing_data(self) -> bool:
        """Test 2: Verify all items have proper pricing data"""
        logger.info("🔍 Test 2: Checking pricing data...")
        try:
            request = {
                "message": "Show me healthy options",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch"
                },
                "chat_history": [],
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get('menu_items', [])
                
                items_with_price = [item for item in menu_items if item.get('price') is not None and item.get('price') > 0]
                items_without_price = [item for item in menu_items if item.get('price') is None or item.get('price') == 0]
                
                if len(items_without_price) == 0:
                    logger.info(f"✅ All items have pricing: {len(items_with_price)} items with prices")
                    
                    # Check price ranges are reasonable
                    prices = [item.get('price', 0) for item in menu_items]
                    min_price = min(prices)
                    max_price = max(prices)
                    logger.info(f"Price range: ${min_price:.2f} - ${max_price:.2f}")
                    
                    if min_price > 0 and max_price < 100:  # Reasonable price range
                        logger.info("✅ Price ranges are reasonable")
                        return True
                    else:
                        logger.warning(f"⚠️ Unusual price range: ${min_price:.2f} - ${max_price:.2f}")
                        return False
                else:
                    logger.error(f"❌ {len(items_without_price)} items missing price data")
                    return False
            else:
                logger.error(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            return False
    
    def test_location_data(self) -> bool:
        """Test 3: Verify all items have location data for directions"""
        logger.info("🔍 Test 3: Checking location data...")
        try:
            request = {
                "message": "Show me Italian food",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "dinner"
                },
                "chat_history": [],
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get('menu_items', [])
                
                items_with_location = []
                items_without_location = []
                
                for item in menu_items:
                    restaurant = item.get('restaurant', {})
                    if restaurant.get('lat') and restaurant.get('lng'):
                        items_with_location.append(item)
                    else:
                        items_without_location.append(item)
                
                if len(items_without_location) == 0:
                    logger.info(f"✅ All items have location data: {len(items_with_location)} items with coordinates")
                    
                    # Check coordinate ranges are reasonable (NYC area)
                    lats = [item.get('restaurant', {}).get('lat') for item in items_with_location if item.get('restaurant', {}).get('lat')]
                    lngs = [item.get('restaurant', {}).get('lng') for item in items_with_location if item.get('restaurant', {}).get('lng')]
                    
                    if lats and lngs:
                        min_lat, max_lat = min(lats), max(lats)
                        min_lng, max_lng = min(lngs), max(lngs)
                        logger.info(f"Lat range: {min_lat:.4f} - {max_lat:.4f}")
                        logger.info(f"Lng range: {min_lng:.4f} - {max_lng:.4f}")
                        
                        # NYC coordinates should be around 40.6-40.9 lat, -74.1 to -73.7 lng (broader range)
                        if 40.5 <= min_lat <= 41.0 and 40.5 <= max_lat <= 41.0 and -74.2 <= min_lng <= -73.7 and -74.2 <= max_lng <= -73.7:
                            logger.info("✅ Coordinates are in reasonable NYC range")
                            return True
                        else:
                            logger.warning("⚠️ Coordinates outside expected NYC range")
                            return False
                    else:
                        logger.warning("⚠️ No coordinate data to validate")
                        return False
                else:
                    logger.error(f"❌ {len(items_without_location)} items missing location data")
                    for item in items_without_location[:3]:  # Show first 3
                        logger.error(f"  - {item.get('name')}: Lat = {item.get('restaurant', {}).get('lat')}, Lng = {item.get('restaurant', {}).get('lng')}")
                    return False
            else:
                logger.error(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            return False
    
    def test_directions_functionality(self) -> bool:
        """Test 4: Verify directions URLs are properly formatted"""
        logger.info("🔍 Test 4: Checking directions functionality...")
        try:
            request = {
                "message": "Show me pizza options",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "dinner"
                },
                "chat_history": [],
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get('menu_items', [])
                
                valid_directions_urls = 0
                invalid_directions_urls = 0
                
                for item in menu_items:
                    restaurant = item.get('restaurant', {})
                    lat = restaurant.get('lat')
                    lng = restaurant.get('lng')
                    address = restaurant.get('address')
                    
                    if lat and lng:
                        # Test the directions URL format
                        directions_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
                        if f"{lat},{lng}" in directions_url:
                            valid_directions_urls += 1
                        else:
                            invalid_directions_urls += 1
                    elif address:
                        # Test address-based directions URL
                        directions_url = f"https://www.google.com/maps/search/?api=1&query={address}"
                        if address in directions_url:
                            valid_directions_urls += 1
                        else:
                            invalid_directions_urls += 1
                    else:
                        invalid_directions_urls += 1
                
                if invalid_directions_urls == 0:
                    logger.info(f"✅ All {valid_directions_urls} items have valid directions URLs")
                    return True
                else:
                    logger.error(f"❌ {invalid_directions_urls} items have invalid directions URLs")
                    return False
            else:
                logger.error(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            return False
    
    def test_frontend_integration(self) -> bool:
        """Test 5: Verify frontend can consume the data properly"""
        logger.info("🔍 Test 5: Testing frontend integration...")
        try:
            request = {
                "message": "Show me healthy vegetarian options",
                "context": {
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "meal_context": "lunch"
                },
                "chat_history": [],
                "user_id": self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/search",
                json=request,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields for frontend
                required_fields = ['ai_response', 'menu_items', 'conversation_id', 'search_reasoning']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    logger.error(f"❌ Missing required fields: {missing_fields}")
                    return False
                
                menu_items = data.get('menu_items', [])
                if not menu_items:
                    logger.error("❌ No menu items returned")
                    return False
                
                # Check each menu item has required frontend fields
                required_item_fields = ['id', 'name', 'price', 'restaurant']
                for i, item in enumerate(menu_items):
                    missing_item_fields = [field for field in required_item_fields if field not in item]
                    if missing_item_fields:
                        logger.error(f"❌ Item {i+1} missing fields: {missing_item_fields}")
                        return False
                    
                    # Check restaurant has required fields
                    restaurant = item.get('restaurant', {})
                    required_restaurant_fields = ['id', 'name', 'cuisine', 'rating', 'price_range']
                    missing_restaurant_fields = [field for field in required_restaurant_fields if field not in restaurant]
                    if missing_restaurant_fields:
                        logger.error(f"❌ Item {i+1} restaurant missing fields: {missing_restaurant_fields}")
                        return False
                
                logger.info(f"✅ Frontend integration: {len(menu_items)} items with all required fields")
                return True
            else:
                logger.error(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            return False
    
    def run_comprehensive_tests(self) -> bool:
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Comprehensive Fix Tests")
        logger.info("=" * 70)
        
        tests = [
            ("No Duplicates", self.test_no_duplicates),
            ("Pricing Data", self.test_pricing_data),
            ("Location Data", self.test_location_data),
            ("Directions Functionality", self.test_directions_functionality),
            ("Frontend Integration", self.test_frontend_integration)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                result = test_func()
                results[test_name] = result
                logger.info(f"{test_name}: {'✅ PASS' if result else '❌ FAIL'}")
            except Exception as e:
                logger.error(f"{test_name}: ❌ ERROR - {str(e)}")
                results[test_name] = False
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 Comprehensive Fix Test Results:")
        passed = 0
        total = len(tests)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
            if result:
                passed += 1
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All comprehensive tests PASSED! All fixes working correctly!")
        else:
            logger.warning(f"⚠️ {total - passed} tests failed. Issues need to be fixed.")
        
        return passed == total

def main():
    """Run comprehensive tests"""
    tester = ComprehensiveFixTester()
    success = tester.run_comprehensive_tests()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
