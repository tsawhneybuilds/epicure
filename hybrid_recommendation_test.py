#!/usr/bin/env python3
"""
Hybrid Recommendation System Test
Tests the complete hybrid system using stored tags and nutrition data
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from supabase import create_client
from tag_inference_service import TagInferenceService

# Load environment variables
load_dotenv()

@dataclass
class UserPreferences:
    """User preference profile"""
    dietary_restrictions: List[str]
    cuisine_preferences: List[str]
    health_goals: List[str]
    spice_preference: str
    meal_type: List[str]
    cooking_method: List[str]
    max_calories: Optional[int] = None
    min_protein: Optional[float] = None
    max_price: Optional[float] = None
    location: Optional[tuple] = None  # (lat, lng)

@dataclass
class RecommendationResult:
    """Individual recommendation result"""
    menu_item_id: str
    name: str
    restaurant_name: str
    description: str
    price: float
    rating: float
    distance_km: float
    semantic_score: float
    tag_score: float
    nutrition_score: float
    price_score: float
    distance_score: float
    final_score: float
    reasoning: str

class HybridRecommendationEngine:
    """Hybrid recommendation engine using stored tags and nutrition data"""
    
    def __init__(self):
        """Initialize the recommendation engine"""
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        self.tag_service = TagInferenceService()
        
        # Weights for different scoring components
        self.weights = {
            'semantic': 0.30,    # Semantic similarity
            'tags': 0.30,        # Tag matching
            'nutrition': 0.20,   # Nutrition fit
            'price': 0.10,       # Price fit
            'distance': 0.10     # Distance fit
        }
    
    def extract_user_preferences(self, user_query: str) -> UserPreferences:
        """Extract user preferences from natural language query"""
        print(f"🔍 Extracting preferences from: '{user_query}'")
        
        # Use the tag service to extract preferences
        extracted = self.tag_service.extract_user_preferences(user_query)
        
        # Convert to UserPreferences format
        preferences = UserPreferences(
            dietary_restrictions=extracted.dietary_restrictions,
            cuisine_preferences=extracted.cuisine_preferences,
            health_goals=extracted.health_goals,
            spice_preference=extracted.spice_preference,
            meal_type=extracted.meal_type,
            cooking_method=extracted.cooking_method
        )
        
        # Extract additional preferences from query text
        query_lower = user_query.lower()
        
        # Extract calorie preferences
        if 'low calorie' in query_lower or 'light' in query_lower:
            preferences.max_calories = 400
        elif 'high calorie' in query_lower or 'hearty' in query_lower:
            preferences.max_calories = 800
        
        # Extract protein preferences
        if 'high protein' in query_lower or 'protein' in query_lower:
            preferences.min_protein = 25.0
        
        # Extract price preferences
        if 'cheap' in query_lower or 'budget' in query_lower:
            preferences.max_price = 15.0
        elif 'expensive' in query_lower or 'premium' in query_lower:
            preferences.max_price = 50.0
        
        print(f"  📋 Extracted preferences:")
        print(f"    Dietary: {preferences.dietary_restrictions}")
        print(f"    Cuisine: {preferences.cuisine_preferences}")
        print(f"    Health: {preferences.health_goals}")
        print(f"    Max calories: {preferences.max_calories}")
        print(f"    Min protein: {preferences.min_protein}g")
        
        return preferences
    
    def get_semantic_recommendations(self, user_query: str, limit: int = 50) -> List[Dict]:
        """Get semantic similarity recommendations"""
        print(f"🔍 Getting semantic recommendations...")
        
        try:
            result = self.supabase.rpc('semantic_search_with_restaurant', {
                'query_text': user_query,
                'match_threshold': 0.3,
                'match_count': limit
            }).execute()
            
            if result.data:
                print(f"  ✅ Found {len(result.data)} semantic matches")
                return result.data
            else:
                print(f"  ⚠️ No semantic matches found")
                return []
                
        except Exception as e:
            print(f"  ❌ Semantic search failed: {e}")
            return []
    
    def calculate_tag_score(self, menu_item: Dict, preferences: UserPreferences) -> float:
        """Calculate tag matching score"""
        score = 0.0
        max_score = 0.0
        
        # Dietary restrictions matching
        item_dietary = menu_item.get('inferred_dietary_tags', []) or []
        user_dietary = preferences.dietary_restrictions
        
        if user_dietary:
            max_score += 1.0
            if any(tag in item_dietary for tag in user_dietary):
                score += 1.0
        
        # Cuisine preferences matching
        item_cuisine = menu_item.get('inferred_cuisine_type', '')
        user_cuisines = preferences.cuisine_preferences
        
        if user_cuisines:
            max_score += 1.0
            if item_cuisine.lower() in [c.lower() for c in user_cuisines]:
                score += 1.0
        
        # Health goals matching (using enhanced health tags)
        item_health = menu_item.get('enhanced_health_tags', []) or []
        user_health = preferences.health_goals
        
        if user_health:
            max_score += 1.0
            health_matches = sum(1 for goal in user_health if any(goal.lower() in tag.lower() for tag in item_health))
            if health_matches > 0:
                score += min(1.0, health_matches / len(user_health))
        
        # Spice preference matching
        item_spice = menu_item.get('inferred_spice_level', 'mild')
        user_spice = preferences.spice_preference
        
        if user_spice and user_spice != 'any':
            max_score += 0.5
            if item_spice.lower() == user_spice.lower():
                score += 0.5
        
        return score / max_score if max_score > 0 else 0.0
    
    def calculate_nutrition_score(self, menu_item: Dict, preferences: UserPreferences) -> float:
        """Calculate nutrition fit score"""
        score = 0.0
        max_score = 0.0
        
        calories = menu_item.get('estimated_calories')
        protein = menu_item.get('estimated_protein_g')
        
        # Calorie fit
        if preferences.max_calories and calories:
            max_score += 1.0
            if calories <= preferences.max_calories:
                score += 1.0
            else:
                # Partial score for close matches
                ratio = preferences.max_calories / calories
                score += max(0, ratio)
        
        # Protein fit
        if preferences.min_protein and protein:
            max_score += 1.0
            if protein >= preferences.min_protein:
                score += 1.0
            else:
                # Partial score for close matches
                ratio = protein / preferences.min_protein
                score += max(0, ratio)
        
        # Health goal nutrition matching
        user_health = preferences.health_goals
        if user_health and calories and protein:
            max_score += 1.0
            health_score = 0.0
            
            for goal in user_health:
                if 'low-calorie' in goal.lower() and calories <= 400:
                    health_score += 0.33
                elif 'high-protein' in goal.lower() and protein >= 25:
                    health_score += 0.33
                elif 'keto' in goal.lower():
                    # Check if low carb (rough estimate)
                    carbs = menu_item.get('estimated_carbs_g', 0)
                    if carbs <= 20:
                        health_score += 0.33
            
            score += min(1.0, health_score)
        
        return score / max_score if max_score > 0 else 0.0
    
    def calculate_price_score(self, menu_item: Dict, preferences: UserPreferences) -> float:
        """Calculate price fit score"""
        price = menu_item.get('price')
        max_price = preferences.max_price
        
        if not price or not max_price:
            return 1.0  # No preference, neutral score
        
        if price <= max_price:
            return 1.0
        else:
            # Penalty for exceeding budget
            return max(0.0, 1.0 - (price - max_price) / max_price)
    
    def calculate_distance_score(self, menu_item: Dict, preferences: UserPreferences) -> float:
        """Calculate distance fit score"""
        distance = menu_item.get('distance_km', 0)
        
        if not preferences.location or distance == 0:
            return 1.0  # No location preference, neutral score
        
        # Prefer closer restaurants
        if distance <= 1.0:
            return 1.0
        elif distance <= 5.0:
            return 0.8
        elif distance <= 10.0:
            return 0.6
        else:
            return 0.4
    
    def get_recommendations(self, user_query: str, limit: int = 10) -> List[RecommendationResult]:
        """Get hybrid recommendations for a user query"""
        print(f"\n🎯 Getting hybrid recommendations for: '{user_query}'")
        print("=" * 60)
        
        # Step 1: Extract user preferences
        preferences = self.extract_user_preferences(user_query)
        
        # Step 2: Get semantic recommendations
        semantic_results = self.get_semantic_recommendations(user_query, limit * 3)
        
        if not semantic_results:
            print("❌ No semantic results found")
            return []
        
        # Step 3: Calculate hybrid scores
        recommendations = []
        
        for item in semantic_results:
            # Calculate individual scores
            semantic_score = item.get('similarity', 0.0)
            tag_score = self.calculate_tag_score(item, preferences)
            nutrition_score = self.calculate_nutrition_score(item, preferences)
            price_score = self.calculate_price_score(item, preferences)
            distance_score = self.calculate_distance_score(item, preferences)
            
            # Calculate weighted final score
            final_score = (
                semantic_score * self.weights['semantic'] +
                tag_score * self.weights['tags'] +
                nutrition_score * self.weights['nutrition'] +
                price_score * self.weights['price'] +
                distance_score * self.weights['distance']
            )
            
            # Generate reasoning
            reasoning_parts = []
            if tag_score > 0.5:
                reasoning_parts.append(f"matches your dietary preferences ({tag_score:.2f})")
            if nutrition_score > 0.5:
                reasoning_parts.append(f"fits your nutrition goals ({nutrition_score:.2f})")
            if semantic_score > 0.5:
                reasoning_parts.append(f"semantically similar to your request ({semantic_score:.2f})")
            
            reasoning = ", ".join(reasoning_parts) if reasoning_parts else "general match"
            
            recommendation = RecommendationResult(
                menu_item_id=item.get('id', ''),
                name=item.get('name', ''),
                restaurant_name=item.get('restaurant_name', ''),
                description=item.get('description', ''),
                price=item.get('price', 0.0),
                rating=item.get('rating', 0.0),
                distance_km=item.get('distance_km', 0.0),
                semantic_score=semantic_score,
                tag_score=tag_score,
                nutrition_score=nutrition_score,
                price_score=price_score,
                distance_score=distance_score,
                final_score=final_score,
                reasoning=reasoning
            )
            
            recommendations.append(recommendation)
        
        # Step 4: Sort by final score and return top results
        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        
        print(f"\n📊 Scoring breakdown for top results:")
        for i, rec in enumerate(recommendations[:5]):
            print(f"  {i+1}. {rec.name} ({rec.restaurant_name})")
            print(f"     Final: {rec.final_score:.3f} | Semantic: {rec.semantic_score:.3f} | Tags: {rec.tag_score:.3f} | Nutrition: {rec.nutrition_score:.3f}")
            print(f"     Reasoning: {rec.reasoning}")
            print()
        
        return recommendations[:limit]

def test_hybrid_recommendations():
    """Test the hybrid recommendation system with various queries"""
    
    print("🧪 Testing Hybrid Recommendation System")
    print("=" * 60)
    
    engine = HybridRecommendationEngine()
    
    # Test queries
    test_queries = [
        "I want a healthy vegetarian meal with high protein",
        "Looking for Italian food that's gluten-free",
        "Need something low calorie for lunch",
        "Want a hearty burger with good ratings",
        "Looking for vegan options under $20"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 50)
        
        recommendations = engine.get_recommendations(query, limit=5)
        
        if recommendations:
            print(f"\n🏆 Top {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec.name} at {rec.restaurant_name}")
                print(f"     💰 ${rec.price:.2f} | ⭐ {rec.rating:.1f} | 📍 {rec.distance_km:.1f}km")
                print(f"     🎯 Score: {rec.final_score:.3f} | {rec.reasoning}")
                print(f"     📝 {rec.description[:100]}...")
                print()
        else:
            print("❌ No recommendations found")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_hybrid_recommendations()
