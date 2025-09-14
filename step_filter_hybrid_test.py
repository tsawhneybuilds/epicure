#!/usr/bin/env python3
"""
Step-Filter Hybrid Recommendation System
Uses a step-by-step filtering approach:
1. Hard filters (tags, dietary restrictions)
2. Location/distance filters
3. Semantic search within filtered results
4. Soft scoring (rating, price, nutrition)
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from supabase import create_client
from tag_inference_service import TagInferenceService
from sentence_transformers import SentenceTransformer

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
    rating_score: float
    price_score: float
    distance_score: float
    final_score: float
    reasoning: str
    # Additional data for display
    dietary_tags: List[str]
    cuisine_type: str
    health_tags: List[str]
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float

class StepFilterHybridEngine:
    """Step-by-step filtering hybrid recommendation engine"""
    
    def __init__(self):
        """Initialize the recommendation engine"""
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        self.tag_service = TagInferenceService()
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Weights for final soft scoring
        self.weights = {
            'semantic': 0.35,    # Semantic similarity
            'nutrition': 0.25,   # Nutrition fit
            'rating': 0.20,      # Restaurant rating
            'price': 0.15,       # Price fit
            'distance': 0.05     # Distance fit
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
        print(f"    Max price: ${preferences.max_price}")
        
        return preferences
    
    def step1_hard_filters(self, preferences: UserPreferences, limit: int = 100) -> List[Dict]:
        """Step 1: Apply hard filters (dietary restrictions, tags)"""
        print(f"\n🚫 Step 1: Applying hard filters...")
        
        try:
            # Build query based on hard requirements
            query = self.supabase.table('menu_items').select(
                'id, name, description, price, restaurant_id, '
                'inferred_dietary_tags, inferred_cuisine_type, inferred_health_tags, '
                'estimated_calories, estimated_protein_g, estimated_carbs_g, estimated_fat_g, '
                'restaurants(name, cuisine, rating)'
            )
            
            # Apply dietary restrictions filter (HARD REQUIREMENT)
            if preferences.dietary_restrictions:
                print(f"  🏷️ Filtering by dietary restrictions: {preferences.dietary_restrictions}")
                query = query.contains('inferred_dietary_tags', preferences.dietary_restrictions)
            
            # Apply cuisine filter (HARD REQUIREMENT)
            if preferences.cuisine_preferences:
                print(f"  🍝 Filtering by cuisine: {preferences.cuisine_preferences}")
                cuisine_conditions = [f"inferred_cuisine_type.ilike.%{cuisine}%" for cuisine in preferences.cuisine_preferences]
                query = query.or_(','.join(cuisine_conditions))
            
            # Apply price filter (HARD REQUIREMENT)
            if preferences.max_price:
                print(f"  💰 Filtering by max price: ${preferences.max_price}")
                query = query.lte('price', preferences.max_price)
            
            result = query.limit(limit).execute()
            
            if result.data:
                print(f"  ✅ Step 1: {len(result.data)} items passed hard filters")
                return result.data
            else:
                print(f"  ❌ Step 1: No items passed hard filters")
                return []
                
        except Exception as e:
            print(f"  ❌ Step 1 failed: {e}")
            return []
    
    def step2_location_filters(self, items: List[Dict], preferences: UserPreferences) -> List[Dict]:
        """Step 2: Apply location/distance filters"""
        print(f"\n📍 Step 2: Applying location filters...")
        
        if not preferences.location:
            print(f"  ⏭️ No location provided, skipping location filters")
            return items
        
        user_lat, user_lng = preferences.location
        max_distance_km = 10.0  # Default max distance
        
        print(f"  📍 User location: ({user_lat}, {user_lng})")
        print(f"  📏 Max distance: {max_distance_km}km")
        
        try:
            # Get restaurant locations and calculate distances
            filtered_items = []
            for item in items:
                restaurant_id = item.get('restaurant_id')
                if restaurant_id:
                    # Get restaurant location from database
                    restaurant_result = self.supabase.table('restaurants').select('location').eq('id', restaurant_id).execute()
                    
                    if restaurant_result.data and restaurant_result.data[0].get('location'):
                        # Calculate distance using PostGIS (if available) or simple approximation
                        restaurant_location = restaurant_result.data[0]['location']
                        
                        # For now, use a simple distance approximation
                        # In production, this would use PostGIS ST_Distance
                        distance_km = self._calculate_distance_approximation(
                            user_lat, user_lng, 
                            restaurant_location.get('lat', 0), 
                            restaurant_location.get('lng', 0)
                        )
                        
                        if distance_km <= max_distance_km:
                            item['distance_km'] = distance_km
                            filtered_items.append(item)
                    else:
                        # If no location data, include the item
                        item['distance_km'] = 0.0
                        filtered_items.append(item)
            
            print(f"  ✅ Step 2: {len(filtered_items)} items passed location filters")
            return filtered_items
            
        except Exception as e:
            print(f"  ❌ Step 2 failed: {e}")
            return items
    
    def _calculate_distance_approximation(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate approximate distance between two points in kilometers"""
        import math
        
        # Haversine formula for distance calculation
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def step3_semantic_search(self, items: List[Dict], user_query: str, limit: int = 20) -> List[Dict]:
        """Step 3: Apply semantic search within filtered results"""
        print(f"\n🧠 Step 3: Applying semantic search...")
        
        if not items:
            print(f"  ❌ No items to search semantically")
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.embedding_model.encode([user_query])[0].tolist()
            
            # Get item IDs from filtered results
            item_ids = [item['id'] for item in items]
            
            # Search for semantic matches within our filtered items
            result = self.supabase.rpc('match_menu_items', {
                'query_embedding': query_embedding,
                'match_threshold': 0.2,
                'match_count': limit
            }).execute()
            
            if result.data:
                # Filter semantic results to only include items that passed hard filters
                filtered_semantic = []
                for semantic_item in result.data:
                    if semantic_item['id'] in item_ids:
                        # Find the original item data
                        original_item = next((item for item in items if item['id'] == semantic_item['id']), None)
                        if original_item:
                            # Merge semantic score with original data
                            enriched_item = {
                                **original_item,
                                'semantic_score': semantic_item['similarity']
                            }
                            filtered_semantic.append(enriched_item)
                
                print(f"  ✅ Step 3: {len(filtered_semantic)} items passed semantic search")
                return filtered_semantic
            else:
                print(f"  ❌ Step 3: No semantic matches found")
                return []
                
        except Exception as e:
            print(f"  ❌ Step 3 failed: {e}")
            return []
    
    def step4_soft_scoring(self, items: List[Dict], preferences: UserPreferences) -> List[RecommendationResult]:
        """Step 4: Apply soft scoring (nutrition, price, distance)"""
        print(f"\n⭐ Step 4: Applying soft scoring...")
        
        recommendations = []
        
        for item in items:
            # Calculate individual scores
            semantic_score = item.get('semantic_score', 0.0)
            nutrition_score = self.calculate_nutrition_score(item, preferences)
            rating_score = self.calculate_rating_score(item)
            price_score = self.calculate_price_score(item, preferences)
            distance_score = self.calculate_distance_score(item, preferences)
            
            # Calculate weighted final score
            final_score = (
                semantic_score * self.weights['semantic'] +
                nutrition_score * self.weights['nutrition'] +
                rating_score * self.weights['rating'] +
                price_score * self.weights['price'] +
                distance_score * self.weights['distance']
            )
            
            # Generate reasoning
            reasoning_parts = []
            if semantic_score > 0.3:
                reasoning_parts.append(f"semantically similar to your request ({semantic_score:.2f})")
            if nutrition_score > 0.5:
                reasoning_parts.append(f"fits your nutrition goals ({nutrition_score:.2f})")
            if rating_score > 0.7:
                reasoning_parts.append(f"highly rated restaurant ({rating_score:.2f})")
            if price_score > 0.8:
                reasoning_parts.append(f"good price fit ({price_score:.2f})")
            
            reasoning = ", ".join(reasoning_parts) if reasoning_parts else "general match"
            
            restaurant_data = item.get('restaurants', {})
            
            recommendation = RecommendationResult(
                menu_item_id=item.get('id', ''),
                name=item.get('name', ''),
                restaurant_name=restaurant_data.get('name', ''),
                description=item.get('description', ''),
                price=item.get('price', 0.0),
                rating=restaurant_data.get('rating', 0.0),
                distance_km=item.get('distance_km', 0.0),
                semantic_score=semantic_score,
                tag_score=1.0,  # All items passed tag filters
                nutrition_score=nutrition_score,
                rating_score=rating_score,
                price_score=price_score,
                distance_score=distance_score,
                final_score=final_score,
                reasoning=reasoning,
                dietary_tags=item.get('inferred_dietary_tags', []),
                cuisine_type=item.get('inferred_cuisine_type', ''),
                health_tags=item.get('inferred_health_tags', []),
                calories=item.get('estimated_calories', 0),
                protein_g=item.get('estimated_protein_g', 0.0),
                carbs_g=item.get('estimated_carbs_g', 0.0),
                fat_g=item.get('estimated_fat_g', 0.0)
            )
            
            recommendations.append(recommendation)
        
        # Sort by final score
        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        
        print(f"  ✅ Step 4: Scored {len(recommendations)} items")
        return recommendations
    
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
    
    def calculate_rating_score(self, menu_item: Dict) -> float:
        """Calculate restaurant rating score"""
        restaurant_data = menu_item.get('restaurants', {})
        rating = restaurant_data.get('rating')
        
        if not rating:
            return 0.5  # Neutral score for unrated restaurants
        
        # Normalize rating to 0-1 scale (assuming 1-5 star rating)
        if rating <= 5.0:
            return rating / 5.0
        else:
            # Handle other rating scales (e.g., 1-10)
            return min(1.0, rating / 10.0)
    
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
        """Get step-filtered hybrid recommendations"""
        print(f"\n🎯 Step-Filter Hybrid Recommendations for: '{user_query}'")
        print("=" * 70)
        
        # Step 1: Extract user preferences
        preferences = self.extract_user_preferences(user_query)
        
        # Step 2: Apply hard filters
        filtered_items = self.step1_hard_filters(preferences, limit * 5)
        
        if not filtered_items:
            print("❌ No items passed hard filters")
            return []
        
        # Step 3: Apply location filters
        location_filtered = self.step2_location_filters(filtered_items, preferences)
        
        # Step 4: Apply semantic search within filtered results
        semantic_filtered = self.step3_semantic_search(location_filtered, user_query, limit * 3)
        
        # If semantic search found no results, use the hard-filtered results instead
        if not semantic_filtered:
            print(f"  🔄 No semantic matches found, using hard-filtered results")
            semantic_filtered = location_filtered
        
        # Step 5: Apply soft scoring
        recommendations = self.step4_soft_scoring(semantic_filtered, preferences)
        
        print(f"\n📊 Final Results:")
        print(f"  Hard filters: {len(filtered_items)} items")
        print(f"  After semantic: {len(semantic_filtered)} items")
        print(f"  Final recommendations: {len(recommendations)} items")
        
        return recommendations[:limit]

def test_step_filter_hybrid():
    """Test the step-filter hybrid recommendation system"""
    
    print("🧪 Testing Step-Filter Hybrid Recommendation System")
    print("=" * 70)
    
    engine = StepFilterHybridEngine()
    
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
                print(f"     💰 ${rec.price or 0:.2f} | ⭐ {rec.rating or 0:.1f} | 📍 {rec.distance_km or 0:.1f}km | 🎯 Score: {rec.final_score:.3f}")
                print(f"     🧠 Semantic: {rec.semantic_score:.3f} | 🥗 Nutrition: {rec.nutrition_score:.3f} | ⭐ Rating: {rec.rating_score:.3f} | 💰 Price: {rec.price_score:.3f}")
                print(f"     🏷️ Tags: {rec.dietary_tags} | {rec.cuisine_type}")
                print(f"     🥗 Nutrition: {rec.calories} cal, {rec.protein_g:.1f}g protein, {rec.carbs_g:.1f}g carbs, {rec.fat_g:.1f}g fat")
                print(f"     📝 {rec.description[:100] if rec.description else 'No description'}...")
                print(f"     💡 {rec.reasoning}")
                print()
        else:
            print("❌ No recommendations found")
        
        print("\n" + "="*70)

if __name__ == "__main__":
    test_step_filter_hybrid()
