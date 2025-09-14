#!/usr/bin/env python3
"""
Quick verification that backend setup is correct
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required imports work"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError:
        print("❌ FastAPI import failed")
        return False
    
    try:
        from app.core.config import settings
        print("✅ Settings imported successfully")
    except ImportError as e:
        print(f"❌ Settings import failed: {e}")
        return False
    
    try:
        from app.services.restaurant_service import RestaurantService
        print("✅ RestaurantService imported successfully")
    except ImportError as e:
        print(f"❌ RestaurantService import failed: {e}")
        return False
    
    try:
        from app.services.ai_service import AIService
        print("✅ AIService imported successfully")
    except ImportError as e:
        print(f"❌ AIService import failed: {e}")
        return False
    
    return True

def test_mock_data():
    """Test mock data functionality"""
    print("\n🧪 Testing mock data...")
    
    try:
        import asyncio
        from app.services.restaurant_service import RestaurantService
        from app.schemas.restaurant import RestaurantSearchRequest
        
        async def test_search():
            service = RestaurantService()
            # Force mock mode
            service.use_mock = True
            
            request = RestaurantSearchRequest(
                query="test",
                location={"lat": 40.7580, "lng": -73.9855},
                limit=3
            )
            
            restaurants, meta = await service.search_restaurants(request)
            print(f"✅ Mock search returned {len(restaurants)} restaurants")
            
            if restaurants:
                r = restaurants[0]
                print(f"   Sample: {r.name} ({r.cuisine}) - {r.price}")
                print(f"   Rating: {r.rating}, Distance: {r.distance}")
            
            return len(restaurants) > 0
        
        result = asyncio.run(test_search())
        return result
        
    except Exception as e:
        print(f"❌ Mock data test failed: {e}")
        return False

def test_ai_service():
    """Test AI service functionality"""
    print("\n🤖 Testing AI service...")
    
    try:
        import asyncio
        from app.services.ai_service import AIService
        
        async def test_preferences():
            service = AIService()
            # Force mock mode
            service.use_mock = True
            
            prefs = await service.extract_preferences(
                "I want healthy vegan food under $20"
            )
            
            print(f"✅ AI service extracted preferences")
            print(f"   Health priority: {prefs.health_priority}")
            print(f"   Budget: ${prefs.budget}")
            print(f"   Dietary restrictions: {len(prefs.dietary_restrictions or [])}")
            
            return True
        
        result = asyncio.run(test_preferences())
        return result
        
    except Exception as e:
        print(f"❌ AI service test failed: {e}")
        return False

def main():
    """Main verification"""
    print("🍽️ Epicure Backend Verification")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Run from backend directory.")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        sys.exit(1)
    
    # Test mock data
    if not test_mock_data():
        print("\n❌ Mock data tests failed")
        sys.exit(1)
    
    # Test AI service
    if not test_ai_service():
        print("\n❌ AI service tests failed")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 All verification tests passed!")
    print("✅ Backend is ready for development")
    print("🚀 Run 'python start.py' to start the server")

if __name__ == "__main__":
    main()
