#!/usr/bin/env python3
"""
Tag Inference Service using DeepSeek-V3 via Groq
Extract dietary preferences, cuisine types, and health tags from natural language
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from groq import Groq
except ImportError:
    print("❌ Groq not installed. Run: pip install groq")
    exit(1)

@dataclass
class ExtractedTags:
    dietary_restrictions: List[str]  # ['vegetarian', 'gluten-free', 'dairy-free']
    cuisine_preferences: List[str]   # ['italian', 'japanese', 'mexican']
    health_goals: List[str]         # ['low-calorie', 'high-protein', 'keto']
    spice_preference: str           # 'mild', 'medium', 'hot'
    meal_type: List[str]           # ['breakfast', 'lunch', 'dinner', 'snack']
    cooking_method: List[str]      # ['grilled', 'fried', 'steamed', 'raw']
    confidence: float              # 0.0 - 1.0

@dataclass
class MenuItemTags:
    dietary_tags: List[str]        # What dietary restrictions it meets
    cuisine_type: str             # Primary cuisine category
    health_tags: List[str]        # Health characteristics
    spice_level: str              # Spice intensity
    meal_category: str            # When typically eaten
    cooking_methods: List[str]    # How it's prepared
    allergens: List[str]          # Potential allergens
    confidence: float             # Extraction confidence

class TagInferenceService:
    def __init__(self):
        """Initialize the tag inference service with Groq client"""
        self.groq_client = self._get_groq_client()
        self.dietary_restrictions = [
            'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'nut-free',
            'soy-free', 'egg-free', 'shellfish-free', 'pescatarian', 'kosher', 'halal'
        ]
        self.cuisine_types = [
            'italian', 'chinese', 'japanese', 'mexican', 'indian', 'thai', 
            'french', 'american', 'mediterranean', 'korean', 'vietnamese',
            'greek', 'spanish', 'middle-eastern', 'caribbean', 'african'
        ]
        self.health_goals = [
            'low-calorie', 'high-protein', 'low-carb', 'keto', 'paleo',
            'whole30', 'low-fat', 'high-fiber', 'diabetic-friendly', 'heart-healthy'
        ]
        
        print("🏷️ Tag Inference Service initialized with Llama-3.3-70B-Versatile")
    
    def _get_groq_client(self) -> Groq:
        """Initialize Groq client"""
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return Groq(api_key=api_key)
    
    def extract_user_preferences(self, user_query: str) -> ExtractedTags:
        """Extract user preferences from natural language query using DeepSeek-V3"""
        
        system_prompt = f"""You are an expert food preference analyst. Extract structured tags from user food queries.

Available dietary restrictions: {', '.join(self.dietary_restrictions)}
Available cuisines: {', '.join(self.cuisine_types)}
Available health goals: {', '.join(self.health_goals)}
Spice levels: mild, medium, hot
Meal types: breakfast, lunch, dinner, snack, dessert
Cooking methods: grilled, fried, baked, steamed, raw, roasted, sauteed

CRITICAL: Respond with ONLY valid JSON. No explanation, no thinking, no extra text.

Return this exact JSON structure:
{{
    "dietary_restrictions": ["list of dietary restrictions"],
    "cuisine_preferences": ["list of preferred cuisines"],
    "health_goals": ["list of health goals"],
    "spice_preference": "mild/medium/hot or null",
    "meal_type": ["list of meal types"],
    "cooking_method": ["list of cooking methods"],
    "confidence": 0.85
}}

If a category isn't mentioned, use an empty list. Use null (not "null") for empty spice_preference."""

        user_prompt = f"Extract food preferences from this query: '{user_query}'"
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Remove thinking tokens and extra text
            response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)
            response_text = response_text.strip()
            
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group()
            
            # Clean up common JSON issues - but be careful with null
            response_text = response_text.replace("'", '"')
            
            # Try parsing JSON with error handling
            try:
                extracted_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed for: {response_text[:100]}...")
                print(f"   Error: {e}")
                # Return default structure
                extracted_data = {
                    'dietary_restrictions': [],
                    'cuisine_preferences': [],
                    'health_goals': [],
                    'spice_preference': None,
                    'meal_type': [],
                    'cooking_method': [],
                    'confidence': 0.3
                }
            
            return ExtractedTags(
                dietary_restrictions=extracted_data.get('dietary_restrictions', []),
                cuisine_preferences=extracted_data.get('cuisine_preferences', []),
                health_goals=extracted_data.get('health_goals', []),
                spice_preference=extracted_data.get('spice_preference', ''),
                meal_type=extracted_data.get('meal_type', []),
                cooking_method=extracted_data.get('cooking_method', []),
                confidence=float(extracted_data.get('confidence', 0.5))
            )
            
        except Exception as e:
            print(f"❌ Error extracting user preferences: {e}")
            # Return empty tags with low confidence
            return ExtractedTags(
                dietary_restrictions=[], cuisine_preferences=[], health_goals=[],
                spice_preference='', meal_type=[], cooking_method=[], confidence=0.0
            )
    
    def infer_menu_item_tags(self, item_name: str, description: str = None, restaurant_cuisine: str = None) -> MenuItemTags:
        """Infer tags for a menu item using DeepSeek-V3"""
        
        # Create item context
        item_context = item_name
        if description:
            item_context += f": {description}"
        if restaurant_cuisine:
            item_context += f" (from {restaurant_cuisine} restaurant)"
        
        system_prompt = f"""You are an expert food analyzer. Analyze menu items and extract structured tags.

Available dietary tags: {', '.join(self.dietary_restrictions)}
Available cuisines: {', '.join(self.cuisine_types)}
Available health tags: {', '.join(self.health_goals)}
Spice levels: mild, medium, hot
Meal categories: breakfast, lunch, dinner, snack, dessert, appetizer, main, side
Cooking methods: grilled, fried, baked, steamed, raw, roasted, sauteed, braised
Common allergens: nuts, dairy, gluten, eggs, shellfish, soy, fish

CRITICAL: Respond with ONLY valid JSON. No explanation, no thinking, no extra text.

Return this exact JSON structure:
{{
    "dietary_tags": ["dietary restrictions this item meets"],
    "cuisine_type": "primary cuisine category",
    "health_tags": ["health characteristics"],
    "spice_level": "mild/medium/hot",
    "meal_category": "when typically eaten",
    "cooking_methods": ["how it's prepared"],
    "allergens": ["potential allergens present"],
    "confidence": 0.85
}}

Base analysis on ingredients and preparation methods. Use only values from the available lists above."""

        user_prompt = f"Analyze this menu item: '{item_context}'"
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Remove thinking tokens and extra text
            response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)
            response_text = response_text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group()
            
            # Clean up common JSON issues - but be careful with null
            response_text = response_text.replace("'", '"')
            
            # Try parsing JSON with error handling
            try:
                extracted_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed for menu item: {item_name}")
                print(f"   Response: {response_text[:100]}...")
                print(f"   Error: {e}")
                # Return default structure
                extracted_data = {
                    'dietary_tags': [],
                    'cuisine_type': 'unknown',
                    'health_tags': [],
                    'spice_level': 'mild',
                    'meal_category': 'main',
                    'cooking_methods': [],
                    'allergens': [],
                    'confidence': 0.3
                }
            
            return MenuItemTags(
                dietary_tags=extracted_data.get('dietary_tags', []),
                cuisine_type=extracted_data.get('cuisine_type', ''),
                health_tags=extracted_data.get('health_tags', []),
                spice_level=extracted_data.get('spice_level', ''),
                meal_category=extracted_data.get('meal_category', ''),
                cooking_methods=extracted_data.get('cooking_methods', []),
                allergens=extracted_data.get('allergens', []),
                confidence=float(extracted_data.get('confidence', 0.5))
            )
            
        except Exception as e:
            print(f"❌ Error inferring menu item tags: {e}")
            # Return empty tags with low confidence
            return MenuItemTags(
                dietary_tags=[], cuisine_type='', health_tags=[],
                spice_level='', meal_category='', cooking_methods=[],
                allergens=[], confidence=0.0
            )
    
    def calculate_tag_similarity(self, user_tags: ExtractedTags, item_tags: MenuItemTags) -> float:
        """Calculate similarity score between user preferences and menu item tags"""
        
        total_score = 0.0
        max_possible_score = 0.0
        
        # Dietary restrictions (highest weight - must match)
        if user_tags.dietary_restrictions:
            dietary_weight = 0.4
            max_possible_score += dietary_weight
            
            # Check if item meets all user dietary restrictions
            restrictions_met = 0
            for restriction in user_tags.dietary_restrictions:
                if restriction in item_tags.dietary_tags:
                    restrictions_met += 1
            
            if user_tags.dietary_restrictions:
                dietary_score = restrictions_met / len(user_tags.dietary_restrictions)
                total_score += dietary_score * dietary_weight
        
        # Cuisine preferences (medium weight)
        if user_tags.cuisine_preferences:
            cuisine_weight = 0.25
            max_possible_score += cuisine_weight
            
            if item_tags.cuisine_type in user_tags.cuisine_preferences:
                total_score += cuisine_weight
        
        # Health goals (medium weight)
        if user_tags.health_goals:
            health_weight = 0.2
            max_possible_score += health_weight
            
            health_matches = len(set(user_tags.health_goals) & set(item_tags.health_tags))
            if user_tags.health_goals:
                health_score = health_matches / len(user_tags.health_goals)
                total_score += health_score * health_weight
        
        # Spice preference (low weight)
        if user_tags.spice_preference:
            spice_weight = 0.1
            max_possible_score += spice_weight
            
            if user_tags.spice_preference == item_tags.spice_level:
                total_score += spice_weight
        
        # Cooking method (low weight)
        if user_tags.cooking_method:
            cooking_weight = 0.05
            max_possible_score += cooking_weight
            
            cooking_matches = len(set(user_tags.cooking_method) & set(item_tags.cooking_methods))
            if user_tags.cooking_method:
                cooking_score = cooking_matches / len(user_tags.cooking_method)
                total_score += cooking_score * cooking_weight
        
        # Normalize by maximum possible score
        if max_possible_score > 0:
            normalized_score = total_score / max_possible_score
        else:
            normalized_score = 0.0
        
        # Weight by confidence of both extractions
        confidence_weight = (user_tags.confidence + item_tags.confidence) / 2
        final_score = normalized_score * confidence_weight
        
        return min(final_score, 1.0)  # Cap at 1.0

def test_tag_inference():
    """Test the tag inference service with sample data"""
    
    print("🧪 Testing Tag Inference Service")
    print("=" * 50)
    
    # Initialize service
    try:
        service = TagInferenceService()
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return
    
    # Test user preference extraction
    test_queries = [
        "I want something healthy and vegetarian for lunch",
        "Looking for spicy italian pasta with no dairy",
        "Need a low-carb high-protein dinner option",
        "Want some grilled chicken or fish, nothing too spicy",
        "Craving japanese ramen or sushi for dinner"
    ]
    
    print("\n🔍 Testing User Preference Extraction:")
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        user_tags = service.extract_user_preferences(query)
        
        print(f"  Dietary: {user_tags.dietary_restrictions}")
        print(f"  Cuisine: {user_tags.cuisine_preferences}")
        print(f"  Health: {user_tags.health_goals}")
        print(f"  Spice: {user_tags.spice_preference}")
        print(f"  Meal: {user_tags.meal_type}")
        print(f"  Cooking: {user_tags.cooking_method}")
        print(f"  Confidence: {user_tags.confidence:.2f}")
    
    # Test menu item tag inference
    test_items = [
        ("Margherita Pizza", "Fresh mozzarella, tomato sauce, basil", "Italian"),
        ("Grilled Chicken Salad", "Mixed greens, grilled chicken breast, vegetables", "American"),
        ("Spicy Tuna Roll", "Fresh tuna, avocado, spicy mayo, seaweed", "Japanese"),
        ("Quinoa Buddha Bowl", "Quinoa, roasted vegetables, tahini dressing", "Mediterranean")
    ]
    
    print("\n\n🍽️ Testing Menu Item Tag Inference:")
    for name, description, cuisine in test_items:
        print(f"\nItem: {name}")
        print(f"Description: {description}")
        
        item_tags = service.infer_menu_item_tags(name, description, cuisine)
        
        print(f"  Dietary: {item_tags.dietary_tags}")
        print(f"  Cuisine: {item_tags.cuisine_type}")
        print(f"  Health: {item_tags.health_tags}")
        print(f"  Spice: {item_tags.spice_level}")
        print(f"  Category: {item_tags.meal_category}")
        print(f"  Cooking: {item_tags.cooking_methods}")
        print(f"  Allergens: {item_tags.allergens}")
        print(f"  Confidence: {item_tags.confidence:.2f}")
    
    # Test tag matching
    print("\n\n🎯 Testing Tag Similarity Matching:")
    user_query = "I want something healthy and vegetarian for lunch"
    user_tags = service.extract_user_preferences(user_query)
    
    print(f"User query: '{user_query}'")
    print(f"User preferences: {user_tags}")
    
    for name, description, cuisine in test_items:
        item_tags = service.infer_menu_item_tags(name, description, cuisine)
        similarity = service.calculate_tag_similarity(user_tags, item_tags)
        
        print(f"\n{name}: {similarity:.3f} similarity")
        print(f"  Matches: Dietary={set(user_tags.dietary_restrictions) & set(item_tags.dietary_tags)}")
        print(f"           Health={set(user_tags.health_goals) & set(item_tags.health_tags)}")

if __name__ == "__main__":
    test_tag_inference()
