#!/usr/bin/env python3
"""
Integration Demo Script for Frontend_New ↔ Backend
Runs both backend and frontend, then executes integration tests
"""

import subprocess
import time
import requests
import json
import os
import signal
import sys
from typing import Optional

class IntegrationDemo:
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting Backend Server...")
        os.chdir("backend")
        
        # Set environment variable for mock data
        env = os.environ.copy()
        env["MOCK_DATA"] = "true"
        
        self.backend_process = subprocess.Popen([
            "python3", "-c", """
import asyncio
import uvicorn
from main import app
import os

# Set mock data mode
os.environ['MOCK_DATA'] = 'true'

print('🍽️ Starting Epicure Backend Integration Demo')
print('📱 Mock data mode enabled')
print('🚀 Server will be available at: http://localhost:8000')
print('📖 API docs: http://localhost:8000/docs')

uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
"""
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        os.chdir("..")
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"{self.backend_url}/api/v1/menu-items/stats", timeout=1)
                if response.status_code == 200:
                    print("✅ Backend is running!")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Backend failed to start")
        return False
    
    def start_frontend(self):
        """Start the React frontend development server"""
        print("\n🚀 Starting Frontend Server...")
        os.chdir("frontend_new")
        
        # Create .env.local if it doesn't exist
        with open(".env.local", "w") as f:
            f.write("VITE_API_BASE_URL=http://localhost:8000/api/v1\n")
        
        self.frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        os.chdir("..")
        
        # Wait for frontend to start
        print("⏳ Waiting for frontend to start...")
        for i in range(60):  # Wait up to 60 seconds for npm
            try:
                response = requests.get(self.frontend_url, timeout=1)
                if response.status_code == 200:
                    print("✅ Frontend is running!")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Frontend failed to start")
        return False
    
    def run_integration_tests(self):
        """Run integration tests via API calls"""
        print("\n🧪 Running Integration Tests...")
        print("=" * 60)
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Backend Health
        print("\n🔍 Testing: Backend Health Check")
        tests_total += 1
        try:
            response = requests.get(f"{self.backend_url}/api/v1/menu-items/stats")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ PASS: Backend responding with {data.get('total_menu_items', 0)} menu items")
                tests_passed += 1
            else:
                print(f"❌ FAIL: Backend returned status {response.status_code}")
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
        
        # Test 2: Menu Item Search
        print("\n🔍 Testing: Menu Item Search API")
        tests_total += 1
        try:
            search_request = {
                "query": "healthy protein bowl",
                "location": {"lat": 40.7580, "lng": -73.9855},
                "filters": {"min_protein": 20},
                "limit": 3
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/menu-items/search",
                json=search_request
            )
            
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get('menu_items', [])
                print(f"✅ PASS: Found {len(menu_items)} menu items")
                if menu_items:
                    item = menu_items[0]
                    print(f"   Sample: {item['name']} ({item['protein']}g protein, {item['calories']} cal)")
                    print(f"   Reason: {data['meta']['recommendations_reason']}")
                tests_passed += 1
            else:
                print(f"❌ FAIL: Search returned status {response.status_code}")
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
        
        # Test 3: Conversational AI
        print("\n🔍 Testing: Conversational AI Search")
        tests_total += 1
        try:
            ai_request = {
                "message": "I want something healthy for lunch",
                "context": {"meal_context": "lunch"},
                "user_id": "demo-user-123"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/ai/search",
                json=ai_request
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ PASS: AI responded with {len(data.get('menu_items', []))} suggestions")
                print(f"   AI Response: {data.get('ai_response', '')[:100]}...")
                tests_passed += 1
            else:
                print(f"❌ FAIL: AI search returned status {response.status_code}")
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
        
        # Test 4: Interaction Recording
        print("\n🔍 Testing: Menu Item Interaction Recording")
        tests_total += 1
        try:
            interaction = {
                "user_id": "demo-user-123",
                "menu_item_id": "item-1",
                "action": "like",
                "search_query": "healthy lunch"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/menu-items/interactions/swipe",
                json=interaction
            )
            
            if response.status_code == 200:
                print("✅ PASS: Interaction recorded successfully")
                tests_passed += 1
            else:
                print(f"❌ FAIL: Interaction recording returned status {response.status_code}")
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
        
        # Print Results
        print("\n" + "=" * 60)
        print("🎯 Integration Test Results")
        print("=" * 60)
        print(f"✅ Passed: {tests_passed}")
        print(f"❌ Failed: {tests_total - tests_passed}")
        print(f"📈 Success Rate: {(tests_passed/tests_total)*100:.1f}%")
        
        if tests_passed == tests_total:
            print("\n🎉 All integration tests passed!")
            print("🔗 Frontend ↔ Backend integration is working perfectly!")
        else:
            print("\n⚠️ Some tests failed. Check the logs above.")
        
        return tests_passed == tests_total
    
    def show_demo_info(self):
        """Show information about the running demo"""
        print("\n" + "=" * 60)
        print("🎉 INTEGRATION DEMO RUNNING")
        print("=" * 60)
        print(f"🔧 Backend API: {self.backend_url}")
        print(f"   📖 API Documentation: {self.backend_url}/docs")
        print(f"   📊 Health Check: {self.backend_url}/api/v1/menu-items/stats")
        print()
        print(f"💻 Frontend App: {self.frontend_url}")
        print(f"   🍽️ Menu Item Discovery Interface")
        print(f"   💬 Conversational AI Integration")
        print(f"   📱 Swipe-based Menu Item Selection")
        print()
        print("🧪 Integration Test Results: See above")
        print()
        print("🔍 What to Test:")
        print("   1. Open the frontend in your browser")
        print("   2. Go through the onboarding flow")
        print("   3. Try the conversational search")
        print("   4. Swipe on menu items (right=like, left=dislike)")
        print("   5. Check the liked items screen")
        print("   6. Try the chat interface for refinements")
        print()
        print("📊 Data Flow:")
        print("   Frontend → API Client → Backend → Menu Item Service → Mock Data")
        print("   User Interactions → Backend → Recorded in Mock System")
        print("   Chat Messages → AI Service → Menu Item Recommendations")
        print()
        print("⏹️ Press Ctrl+C to stop the demo")
    
    def cleanup(self):
        """Clean up running processes"""
        print("\n🛑 Stopping demo servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            print("✅ Backend stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            print("✅ Frontend stopped")
        
        print("👋 Demo stopped. Thanks for testing!")
    
    def run(self):
        """Run the complete integration demo"""
        try:
            print("🚀 Starting Epicure Frontend_New ↔ Backend Integration Demo")
            print("=" * 60)
            
            # Start backend
            if not self.start_backend():
                print("❌ Failed to start backend. Exiting.")
                return False
            
            # Start frontend
            if not self.start_frontend():
                print("❌ Failed to start frontend. Exiting.")
                return False
            
            # Run integration tests
            tests_passed = self.run_integration_tests()
            
            # Show demo information
            self.show_demo_info()
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
        
        return True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Received interrupt signal...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    demo = IntegrationDemo()
    demo.run()
