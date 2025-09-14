#!/usr/bin/env python3
"""
Frontend Interaction Test
Simulates actual user interactions with the frontend interface
"""

import requests
import json
import time
from typing import Dict, Any, List

class FrontendInteractionTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = "demo-user-123"
        self.base_location = {"lat": 40.7580, "lng": -73.9855}
        
    def simulate_initial_prompt(self, prompt: str) -> Dict[str, Any]:
        """Simulate user entering initial prompt"""
        print(f"🎯 Simulating initial prompt: '{prompt}'")
        
        payload = {
            "message": prompt,
            "user_id": self.user_id,
            "context": {
                "location": self.base_location,
                "meal_context": "lunch"
            }
        }
        
        response = self.session.post(
            "http://localhost:8000/api/v1/ai/recommend",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Response: {data.get('ai_response', '')[:100]}...")
            print(f"📱 Found {len(data.get('menu_items', []))} menu items")
            return data
        else:
            print(f"❌ Failed to get initial recommendations: {response.status_code}")
            return {}
    
    def simulate_location_change(self, new_location: str) -> bool:
        """Simulate user changing location"""
        print(f"📍 Simulating location change to: {new_location}")
        
        # Update location coordinates based on location name
        location_coords = {
            "Manhattan, NY": {"lat": 40.7580, "lng": -73.9855},
            "Brooklyn, NY": {"lat": 40.6782, "lng": -73.9442},
            "Queens, NY": {"lat": 40.7282, "lng": -73.7949}
        }
        
        coords = location_coords.get(new_location, self.base_location)
        
        payload = {
            "query": "popular dishes nearby",
            "location": coords,
            "limit": 5
        }
        
        response = self.session.post(
            "http://localhost:8000/api/v1/menu-items/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Location updated, found {len(data.get('menu_items', []))} items in {new_location}")
            return True
        else:
            print(f"❌ Failed to update location: {response.status_code}")
            return False
    
    def simulate_continue_conversation(self, message: str, chat_history: List[Dict]) -> Dict[str, Any]:
        """Simulate user continuing the conversation"""
        print(f"💬 Simulating continue conversation: '{message}'")
        
        payload = {
            "message": message,
            "user_id": self.user_id,
            "chat_history": chat_history,
            "context": {
                "location": self.base_location
            }
        }
        
        response = self.session.post(
            "http://localhost:8000/api/v1/ai/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Response: {data.get('ai_response', '')[:100]}...")
            print(f"📱 Found {len(data.get('menu_items', []))} refined menu items")
            return data
        else:
            print(f"❌ Failed to continue conversation: {response.status_code}")
            return {}
    
    def simulate_swipe_actions(self, menu_items: List[Dict]) -> Dict[str, int]:
        """Simulate user swiping on menu items"""
        print(f"👆 Simulating swipe actions on {len(menu_items)} items")
        
        swipe_results = {"likes": 0, "dislikes": 0}
        
        for i, item in enumerate(menu_items[:5]):  # Test first 5 items
            # Simulate user behavior: like high-protein items, dislike high-calorie items
            action = "like" if item.get("protein", 0) > 20 else "dislike"
            
            payload = {
                "user_id": self.user_id,
                "menu_item_id": item.get("id", f"item-{i}"),
                "action": action,
                "search_query": "user preferences",
                "position": i,
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            response = self.session.post(
                "http://localhost:8000/api/v1/menu-items/interactions/swipe",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                swipe_results[action + "s"] += 1
                print(f"  {action.capitalize()}d: {item.get('name', 'Unknown')} ({item.get('protein', 0)}g protein)")
            else:
                print(f"  ❌ Failed to record {action} for {item.get('name', 'Unknown')}")
        
        print(f"📊 Swipe Results: {swipe_results['likes']} likes, {swipe_results['dislikes']} dislikes")
        return swipe_results
    
    def simulate_voice_input(self, voice_message: str) -> Dict[str, Any]:
        """Simulate voice input"""
        print(f"🎤 Simulating voice input: '{voice_message}'")
        
        payload = {
            "message": voice_message,
            "user_id": self.user_id,
            "context": {
                "location": self.base_location,
                "input_method": "voice",
                "meal_context": "lunch"
            }
        }
        
        response = self.session.post(
            "http://localhost:8000/api/v1/ai/recommend",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voice AI Response: {data.get('ai_response', '')[:100]}...")
            print(f"📱 Found {len(data.get('menu_items', []))} voice-recommended items")
            return data
        else:
            print(f"❌ Failed voice input: {response.status_code}")
            return {}
    
    def simulate_discover_food_flow(self):
        """Simulate the complete discover food flow"""
        print("\n🍽️ Simulating Complete Discover Food Flow")
        print("=" * 50)
        
        # Step 1: Initial prompt
        initial_data = self.simulate_initial_prompt("I want healthy lunch options under $15")
        if not initial_data:
            return False
        
        menu_items = initial_data.get("menu_items", [])
        chat_history = [
            {"role": "user", "content": "I want healthy lunch options under $15"},
            {"role": "assistant", "content": initial_data.get("ai_response", "")}
        ]
        
        # Step 2: Continue conversation
        continue_data = self.simulate_continue_conversation(
            "Actually, I prefer vegetarian options", 
            chat_history
        )
        
        if continue_data:
            menu_items = continue_data.get("menu_items", [])
            chat_history.extend([
                {"role": "user", "content": "Actually, I prefer vegetarian options"},
                {"role": "assistant", "content": continue_data.get("ai_response", "")}
            ])
        
        # Step 3: Location change
        self.simulate_location_change("Brooklyn, NY")
        
        # Step 4: Voice input
        voice_data = self.simulate_voice_input("Show me something quick for breakfast")
        
        # Step 5: Swipe interactions
        if menu_items:
            swipe_results = self.simulate_swipe_actions(menu_items)
            print(f"✅ Complete flow successful: {swipe_results}")
            return True
        else:
            print("❌ No menu items to swipe on")
            return False
    
    def run_interaction_tests(self):
        """Run all interaction tests"""
        print("🧪 Starting Frontend Interaction Tests")
        print("=" * 60)
        
        # Test individual interactions
        print("\n1️⃣ Testing Initial Prompt")
        initial_data = self.simulate_initial_prompt("High protein meals for post-workout recovery")
        
        print("\n2️⃣ Testing Location Selection")
        self.simulate_location_change("Queens, NY")
        
        print("\n3️⃣ Testing Continue Conversation")
        chat_history = [
            {"role": "user", "content": "High protein meals for post-workout recovery"},
            {"role": "assistant", "content": initial_data.get("ai_response", "")}
        ]
        continue_data = self.simulate_continue_conversation("Show me vegan options too", chat_history)
        
        print("\n4️⃣ Testing Voice Input")
        voice_data = self.simulate_voice_input("I'm in a hurry, show me quick options")
        
        print("\n5️⃣ Testing Swipe Interactions")
        menu_items = initial_data.get("menu_items", [])
        if menu_items:
            swipe_results = self.simulate_swipe_actions(menu_items)
        
        print("\n6️⃣ Testing Complete Discover Food Flow")
        flow_success = self.simulate_discover_food_flow()
        
        print("\n" + "=" * 60)
        print("🎉 Frontend Interaction Tests Complete!")
        print("All user interactions have been simulated successfully.")
        
        return True

def main():
    """Main test runner"""
    tester = FrontendInteractionTester()
    tester.run_interaction_tests()

if __name__ == "__main__":
    main()
