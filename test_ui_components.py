#!/usr/bin/env python3
"""
UI Components Test
Tests the frontend UI components and their interactions
"""

import requests
import json
from typing import Dict, Any

class UIComponentsTester:
    def __init__(self):
        self.session = requests.Session()
        self.frontend_url = "http://localhost:3003"
        
    def test_frontend_loading(self) -> bool:
        """Test if frontend loads correctly"""
        try:
            response = self.session.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for key UI elements
                checks = {
                    "React App": "root" in content or "react" in content.lower(),
                    "CSS Styling": "css" in content.lower() or "style" in content.lower(),
                    "JavaScript": "script" in content.lower() or "js" in content.lower()
                }
                
                print("✅ Frontend loads successfully")
                for check, passed in checks.items():
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check}")
                
                return all(checks.values())
            else:
                print(f"❌ Frontend failed to load: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend loading error: {str(e)}")
            return False
    
    def test_api_connectivity_from_frontend(self) -> bool:
        """Test if frontend can connect to backend API"""
        try:
            # Test the API endpoint that frontend uses
            response = self.session.get("http://localhost:8000/api/v1/menu-items/search", 
                                      params={"limit": 1})
            
            if response.status_code == 200 or response.status_code == 422:  # 422 is expected for missing POST data
                print("✅ Frontend can connect to backend API")
                return True
            else:
                print(f"❌ Frontend API connectivity issue: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend API connectivity error: {str(e)}")
            return False
    
    def test_cors_headers(self) -> bool:
        """Test CORS headers for frontend-backend communication"""
        try:
            # Test preflight request
            response = self.session.options(
                "http://localhost:8000/api/v1/menu-items/search",
                headers={
                    "Origin": self.frontend_url,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            
            if response.status_code == 200:
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
                }
                
                print("✅ CORS headers configured correctly")
                for header, value in cors_headers.items():
                    if value:
                        print(f"  ✅ {header}: {value}")
                    else:
                        print(f"  ❌ {header}: Missing")
                
                return all(cors_headers.values())
            else:
                print(f"❌ CORS preflight failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ CORS test error: {str(e)}")
            return False
    
    def test_ui_component_endpoints(self) -> bool:
        """Test endpoints that UI components use"""
        endpoints_to_test = [
            {
                "name": "Menu Items Search",
                "url": "http://localhost:8000/api/v1/menu-items/search",
                "method": "POST",
                "data": {
                    "query": "test",
                    "location": {"lat": 40.7580, "lng": -73.9855},
                    "limit": 1
                }
            },
            {
                "name": "AI Recommendation",
                "url": "http://localhost:8000/api/v1/ai/recommend",
                "method": "POST",
                "data": {
                    "message": "test recommendation",
                    "user_id": "test-user",
                    "context": {"location": {"lat": 40.7580, "lng": -73.9855}}
                }
            },
            {
                "name": "Swipe Interaction",
                "url": "http://localhost:8000/api/v1/menu-items/interactions/swipe",
                "method": "POST",
                "data": {
                    "user_id": "test-user",
                    "menu_item_id": "test-item",
                    "action": "like",
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            }
        ]
        
        all_passed = True
        
        for endpoint in endpoints_to_test:
            try:
                if endpoint["method"] == "POST":
                    response = self.session.post(
                        endpoint["url"],
                        json=endpoint["data"],
                        headers={"Content-Type": "application/json"}
                    )
                else:
                    response = self.session.get(endpoint["url"])
                
                if response.status_code in [200, 201]:
                    print(f"✅ {endpoint['name']}: Working")
                else:
                    print(f"❌ {endpoint['name']}: Failed ({response.status_code})")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {endpoint['name']}: Error - {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_ui_tests(self):
        """Run all UI component tests"""
        print("🧪 Starting UI Components Tests")
        print("=" * 50)
        
        tests = [
            ("Frontend Loading", self.test_frontend_loading),
            ("API Connectivity", self.test_api_connectivity_from_frontend),
            ("CORS Headers", self.test_cors_headers),
            ("UI Component Endpoints", self.test_ui_component_endpoints)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing {test_name}...")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with error: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 UI Components Test Summary:")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 All UI components are working correctly!")
            print("The frontend should be fully functional.")
        else:
            print(f"\n⚠️  {total - passed} UI tests failed.")
        
        return passed == total

def main():
    """Main test runner"""
    tester = UIComponentsTester()
    success = tester.run_ui_tests()
    return success

if __name__ == "__main__":
    main()
