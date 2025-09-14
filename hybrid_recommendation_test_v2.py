#!/usr/bin/env python3
"""
Hybrid Recommendation System Test v2
Tests the complete hybrid system using stored tags, nutrition data, and semantic search
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
    # Additional data for display
    dietary_tags: List[str]
    cuisine_type: str
    health_tags: List[str]
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float

class HybridRecommendationEngine:
    """Hybrid recommendation engine using stored tags, nutrition data, and semantic search"""
    
    def __init__(self):
        """Initialize the recommendation engine"""
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        self.tag_service = TagInferenceService()
        
        # Weights for different scoring components
        self.weights = {
            'semantic': 0.40,    # Semantic similarity (increased)
            'tags': 0.25,        # Tag matching (decreased)
            'nutrition': 0.20,   # Nutrition fit
            'price': 0.10,       # Price fit
            'distance': 0.05     # Distance fit (decreased)
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
        """Get semantic similarity recommendations using the working match_menu_items function"""
        print(f"🔍 Getting semantic recommendations...")
        
        try:
            # Use the working match_menu_items function with embeddings
            from sentence_transformers import SentenceTransformer
            
            # Generate embedding for the query
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            query_embedding = model.encode([user_query])[0].tolist()
            
            result = self.supabase.rpc('match_menu_items', {
                'query_embedding': query_embedding,
                'match_threshold': 0.2,
                'match_count': limit
            }).execute()
            
            if result.data:
                print(f"  ✅ Found {len(result.data)} semantic matches")
                # Transform to expected format
                transformed = []
                for item in result.data:
                    transformed.append({
                        'item_id': item['id'],
                        'item_name': item['name'],
                        'item_description': item.get('description', ''),
                        'item_price': item.get('price', 0.0),
                        'restaurant_id': item['restaurant_id'],
                        'restaurant_name': '',  # Will be filled from restaurant lookup
                        'restaurant_cuisine': '',
                        'similarity': item['similarity']
                    })
                return transformed
            else:
                print(f"  ⚠️ No semantic matches found")
                return []
                
        except Exception as e:
            print(f"  ❌ Semantic search failed: {e}")
            # Fallback to simple text search
            return self._fallback_text_search(user_query, limit)
    
    def _fallback_text_search(self, user_query: str, limit: int) -> List[Dict]:
        """Fallback text search when semantic search is not available"""
        print(f"  🔄 Using fallback text search...")
        
        try:
            # Simple text search in menu items
            result = self.supabase.table('menu_items').select(
                'id, name, description, price, restaurant_id, restaurants(name, cuisine)'
            ).or_(
                f'name.ilike.%{user_query}%,description.ilike.%{user_query}%'
            ).limit(limit).execute()
            
            if result.data:
                # Transform to match expected format
                transformed = []
                for item in result.data:
                    restaurant = item.get('restaurants', {})
                    transformed.append({
                        'item_id': item['id'],
                        'item_name': item['name'],
                        'item_description': item.get('description', ''),
                        'item_price': item.get('price', 0.0),
                        'restaurant_id': item['restaurant_id'],
                        'restaurant_name': restaurant.get('name', ''),
                        'restaurant_cuisine': restaurant.get('cuisine', ''),
                        'similarity': 0.5  # Default similarity score
                    })
                
                print(f"  ✅ Found {len(transformed)} fallback matches")
                return transformed
            else:
                print(f"  ⚠️ No fallback matches found")
                return []
                
        except Exception as e:
            print(f"  ❌ Fallback search failed: {e}")
            return []
    
    def get_tagged_items(self, preferences: UserPreferences, limit: int = 100) -> List[Dict]:
        """Get items that match tag preferences"""
        print(f"🏷️ Getting items matching tag preferences...")
        
        try:
            # Build query based on preferences
            query = self.supabase.table('menu_items').select(
                'id, name, description, price, restaurant_id, '
                'inferred_dietary_tags, inferred_cuisine_type, inferred_health_tags, '
                'estimated_calories, estimated_protein_g, estimated_carbs_g, estimated_fat_g, '
                'restaurants(name, cuisine, rating)'
            )
            
            # Add dietary restrictions filter
            if preferences.dietary_restrictions:
                dietary_filter = ','.join(preferences.dietary_restrictions)
                query = query.contains('inferred_dietary_tags', preferences.dietary_restrictions)
            
            # Add cuisine filter
            if preferences.cuisine_preferences:
                cuisine_conditions = [f"inferred_cuisine_type.ilike.%{cuisine}%" for cuisine in preferences.cuisine_preferences]
                query = query.or_(','.join(cuisine_conditions))
            
            result = query.limit(limit).execute()
            
            if result.data:
                print(f"  ✅ Found {len(result.data)} tagged matches")
                return result.data
            else:
                print(f"  ⚠️ No tagged matches found")
                return []
                
        except Exception as e:
            print(f"  ❌ Tag search failed: {e}")
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
        item_health = menu_item.get('inferred_health_tags', []) or []
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
        semantic_results = self.get_semantic_recommendations(user_query, limit * 2)
        
        # Step 3: Get tagged recommendations
        tagged_results = self.get_tagged_items(preferences, limit * 2)
        
        # Step 4: Enrich semantic results with restaurant information
        enriched_semantic_results = []
        for item in semantic_results:
            try:
                # Get restaurant information
                restaurant_result = self.supabase.table('restaurants').select('name, cuisine').eq('id', item['restaurant_id']).execute()
                if restaurant_result.data:
                    restaurant = restaurant_result.data[0]
                    item['restaurant_name'] = restaurant['name']
                    item['restaurant_cuisine'] = restaurant['cuisine']
                enriched_semantic_results.append(item)
            except Exception as e:
                print(f"  ⚠️ Could not enrich restaurant info for {item['item_name']}: {e}")
                enriched_semantic_results.append(item)
        
        # Step 5: Combine and deduplicate results
        all_items = {}
        
        # Add semantic results
        print(f"  🔍 Processing {len(enriched_semantic_results)} semantic results...")
        for item in enriched_semantic_results:
            item_id = item.get('item_id', item.get('id'))
            similarity = item.get('similarity', 0.0)
            if item_id:
                all_items[item_id] = {
                    **item,
                    'semantic_score': similarity
                }
                print(f"    📊 {item.get('item_name', 'Unknown')}: item_id = {item_id}, semantic_score = {similarity:.3f}")
        
        print(f"  🏷️ Processing {len(tagged_results)} tagged results...")
        
        # Add tagged results
        for item in tagged_results:
            item_id = item.get('id')
            if item_id:
                print(f"    🏷️ {item.get('name', 'Unknown')}: item_id = {item_id}")
                if item_id in all_items:
                    print(f"      ✅ Merging with existing semantic item (semantic_score preserved)")
                else:
                    print(f"      ➕ Adding new tagged item (no semantic match)")
                if item_id in all_items:
                    # Merge with existing semantic item - preserve semantic score
                    all_items[item_id].update({
                        'inferred_dietary_tags': item.get('inferred_dietary_tags', []),
                        'inferred_cuisine_type': item.get('inferred_cuisine_type', ''),
                        'inferred_health_tags': item.get('inferred_health_tags', []),
                        'estimated_calories': item.get('estimated_calories'),
                        'estimated_protein_g': item.get('estimated_protein_g'),
                        'estimated_carbs_g': item.get('estimated_carbs_g'),
                        'estimated_fat_g': item.get('estimated_fat_g'),
                    })
                else:
                    # Add new item from tagged results (no semantic score)
                    all_items[item_id] = {
                        'item_id': item_id,
                        'item_name': item.get('name', ''),
                        'item_description': item.get('description', ''),
                        'item_price': item.get('price', 0.0),
                        'restaurant_id': item.get('restaurant_id'),
                        'restaurant_name': item.get('restaurants', {}).get('name', ''),
                        'restaurant_cuisine': item.get('restaurants', {}).get('cuisine', ''),
                        'semantic_score': 0.0,  # No semantic match for this item
                        'inferred_dietary_tags': item.get('inferred_dietary_tags', []),
                        'inferred_cuisine_type': item.get('inferred_cuisine_type', ''),
                        'inferred_health_tags': item.get('inferred_health_tags', []),
                        'estimated_calories': item.get('estimated_calories'),
                        'estimated_protein_g': item.get('estimated_protein_g'),
                        'estimated_carbs_g': item.get('estimated_carbs_g'),
                        'estimated_fat_g': item.get('estimated_fat_g'),
                    }
        
        if not all_items:
            print("❌ No items found for recommendation")
            return []
        
        # Step 5: Calculate hybrid scores
        recommendations = []
        
        for item in all_items.values():
            # Calculate individual scores
            semantic_score = item.get('semantic_score', 0.0)
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
                menu_item_id=item.get('item_id', ''),
                name=item.get('item_name', ''),
                restaurant_name=item.get('restaurant_name', ''),
                description=item.get('item_description', ''),
                price=item.get('item_price', 0.0),
                rating=0.0,  # Not available in current schema
                distance_km=0.0,  # Not calculated yet
                semantic_score=semantic_score,
                tag_score=tag_score,
                nutrition_score=nutrition_score,
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
        
        # Step 6: Sort by final score and return top results
        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        
        print(f"\n📊 All items processed: {len(recommendations)}")
        print(f"📊 Scoring breakdown for top results:")
        for i, rec in enumerate(recommendations[:5]):
            print(f"  {i+1}. {rec.name} ({rec.restaurant_name})")
            print(f"     Final: {rec.final_score:.3f} | Semantic: {rec.semantic_score:.3f} | Tags: {rec.tag_score:.3f} | Nutrition: {rec.nutrition_score:.3f}")
            print(f"     Reasoning: {rec.reasoning}")
            print()
        
        # Show some semantic-only results
        semantic_only = [r for r in recommendations if r.semantic_score > 0 and r.tag_score == 0]
        if semantic_only:
            print(f"📊 Semantic-only results (not in top 5):")
            for i, rec in enumerate(semantic_only[:3], 1):
                print(f"  {i}. {rec.name} ({rec.restaurant_name})")
                print(f"     Final: {rec.final_score:.3f} | Semantic: {rec.semantic_score:.3f} | Tags: {rec.tag_score:.3f} | Nutrition: {rec.nutrition_score:.3f}")
                print()
        
        return recommendations[:limit]

def test_hybrid_recommendations():
    """Test the hybrid recommendation system with various queries"""
    
    print("🧪 Testing Hybrid Recommendation System v2")
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
                print(f"     💰 ${rec.price or 0:.2f} | 🎯 Score: {rec.final_score:.3f}")
                print(f"     🏷️ Tags: {rec.dietary_tags} | {rec.cuisine_type}")
                print(f"     🥗 Nutrition: {rec.calories} cal, {rec.protein_g:.1f}g protein, {rec.carbs_g:.1f}g carbs, {rec.fat_g:.1f}g fat")
                print(f"     📝 {rec.description[:100] if rec.description else 'No description'}...")
                print(f"     💡 {rec.reasoning}")
                print()
        else:
            print("❌ No recommendations found")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_hybrid_recommendations()
