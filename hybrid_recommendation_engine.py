#!/usr/bin/env python3
"""
Hybrid Recommendation Engine: Semantic Search + Tag Matching
Combines embedding similarity (40%) with tag matching (30%) plus other factors
"""

import os
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from tag_inference_service import TagInferenceService, ExtractedTags, MenuItemTags

load_dotenv()

@dataclass
class RecommendationResult:
    menu_item_id: str
    restaurant_id: str
    name: str
    description: str
    restaurant_name: str
    cuisine: str
    price: float
    
    # Scoring components
    semantic_similarity: float
    tag_similarity: float
    rating_score: float
    price_score: float
    distance_score: float
    
    # Final score
    total_score: float
    
    # Additional info
    matched_tags: Dict[str, List[str]]
    confidence: float

@dataclass
class SearchFilters:
    max_price: Optional[float] = None
    max_distance_km: Optional[float] = None
    required_dietary: List[str] = None
    excluded_allergens: List[str] = None
    cuisine_filter: Optional[str] = None
    min_rating: Optional[float] = None

class HybridRecommendationEngine:
    def __init__(self):
        """Initialize the hybrid recommendation engine"""
        
        # Initialize clients
        self.supabase = self._get_supabase_client()
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.tag_service = TagInferenceService()
        
        # Scoring weights (must sum to 1.0)
        self.weights = {
            'semantic_similarity': 0.40,
            'tag_matching': 0.30,
            'rating': 0.10,
            'price_fit': 0.10,
            'distance': 0.10
        }
        
        print("🎯 Hybrid Recommendation Engine initialized")
        print(f"📊 Scoring weights: {self.weights}")
    
    def _get_supabase_client(self) -> Client:
        """Initialize Supabase client"""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        
        return create_client(url, key)
    
    def get_recommendations(
        self, 
        user_query: str,
        user_location: Optional[Tuple[float, float]] = None,  # (lat, lng)
        filters: Optional[SearchFilters] = None,
        limit: int = 10
    ) -> List[RecommendationResult]:
        """Get hybrid recommendations combining semantic search and tag matching"""
        
        print(f"🔍 Getting recommendations for: '{user_query}'")
        
        # Step 1: Extract user preferences from query
        user_tags = self.tag_service.extract_user_preferences(user_query)
        print(f"🏷️ Extracted preferences: {user_tags}")
        
        # Step 2: Get semantic search candidates
        query_embedding = self.embedding_model.encode([user_query])[0].tolist()
        
        # Get broader set of candidates for hybrid ranking
        semantic_candidates = self.supabase.rpc('match_menu_items', {
            'query_embedding': query_embedding,
            'match_threshold': 0.15,  # Lower threshold for more candidates
            'match_count': limit * 3  # Get more candidates for reranking
        }).execute()
        
        if not semantic_candidates.data:
            print("❌ No semantic candidates found")
            return []
        
        print(f"🧠 Found {len(semantic_candidates.data)} semantic candidates")
        
        # Step 3: Apply hard filters
        filtered_candidates = self._apply_hard_filters(semantic_candidates.data, filters)
        print(f"🚫 After filtering: {len(filtered_candidates)} candidates")
        
        # Step 4: Get restaurant data for remaining candidates
        enriched_candidates = self._enrich_with_restaurant_data(filtered_candidates)
        
        # Step 5: Calculate hybrid scores
        recommendations = []
        for candidate in enriched_candidates:
            try:
                # Infer tags for this menu item
                item_tags = self.tag_service.infer_menu_item_tags(
                    candidate['name'], 
                    candidate['description'],
                    candidate.get('restaurant_cuisine', '')
                )
                
                # Calculate all scoring components
                semantic_score = candidate['similarity']
                tag_score = self.tag_service.calculate_tag_similarity(user_tags, item_tags)
                rating_score = self._calculate_rating_score(candidate.get('restaurant_rating'))
                price_score = self._calculate_price_score(candidate.get('price'), user_tags)
                distance_score = self._calculate_distance_score(
                    candidate.get('restaurant_location'), user_location
                )
                
                # Calculate weighted total score
                total_score = (
                    semantic_score * self.weights['semantic_similarity'] +
                    tag_score * self.weights['tag_matching'] +
                    rating_score * self.weights['rating'] +
                    price_score * self.weights['price_fit'] +
                    distance_score * self.weights['distance']
                )
                
                # Create recommendation result
                recommendation = RecommendationResult(
                    menu_item_id=candidate['id'],
                    restaurant_id=candidate['restaurant_id'],
                    name=candidate['name'],
                    description=candidate['description'] or '',
                    restaurant_name=candidate.get('restaurant_name', 'Unknown Restaurant'),
                    cuisine=candidate.get('restaurant_cuisine', 'Unknown'),
                    price=candidate.get('price', 0.0),
                    semantic_similarity=semantic_score,
                    tag_similarity=tag_score,
                    rating_score=rating_score,
                    price_score=price_score,
                    distance_score=distance_score,
                    total_score=total_score,
                    matched_tags=self._get_matched_tags(user_tags, item_tags),
                    confidence=(user_tags.confidence + item_tags.confidence) / 2
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                print(f"⚠️ Error processing candidate {candidate.get('name', 'unknown')}: {e}")
                continue
        
        # Step 6: Sort by total score and return top results
        recommendations.sort(key=lambda x: x.total_score, reverse=True)
        
        print(f"✅ Generated {len(recommendations)} recommendations")
        return recommendations[:limit]
    
    def _apply_hard_filters(self, candidates: List[Dict], filters: Optional[SearchFilters]) -> List[Dict]:
        """Apply hard constraint filters"""
        if not filters:
            return candidates
        
        filtered = []
        for candidate in candidates:
            # Price filter
            if filters.max_price and candidate.get('price') and candidate['price'] > filters.max_price:
                continue
            
            # Dietary restrictions (would need more sophisticated matching)
            # For now, basic implementation
            
            filtered.append(candidate)
        
        return filtered
    
    def _enrich_with_restaurant_data(self, candidates: List[Dict]) -> List[Dict]:
        """Enrich candidates with restaurant information"""
        
        # Get unique restaurant IDs
        restaurant_ids = list(set(c['restaurant_id'] for c in candidates))
        
        # Fetch restaurant data
        restaurants_data = {}
        if restaurant_ids:
            restaurants = self.supabase.table('restaurants').select(
                'id,name,cuisine,rating,location'
            ).in_('id', restaurant_ids).execute()
            
            for restaurant in restaurants.data:
                restaurants_data[restaurant['id']] = restaurant
        
        # Enrich candidates
        enriched = []
        for candidate in candidates:
            restaurant_id = candidate['restaurant_id']
            if restaurant_id in restaurants_data:
                restaurant = restaurants_data[restaurant_id]
                candidate['restaurant_name'] = restaurant['name']
                candidate['restaurant_cuisine'] = restaurant['cuisine']
                candidate['restaurant_rating'] = restaurant['rating']
                candidate['restaurant_location'] = restaurant['location']
            
            enriched.append(candidate)
        
        return enriched
    
    def _calculate_rating_score(self, rating: Optional[float]) -> float:
        """Calculate normalized rating score (0-1)"""
        if not rating:
            return 0.5  # Neutral score for missing ratings
        
        # Normalize rating from 1-5 scale to 0-1
        return min(max((rating - 1) / 4, 0), 1)
    
    def _calculate_price_score(self, price: Optional[float], user_tags: ExtractedTags) -> float:
        """Calculate price fit score based on user preferences"""
        if not price:
            return 0.5  # Neutral score for missing price
        
        # Simple price scoring - could be enhanced with user budget preferences
        # For now, favor moderately priced items (sweet spot around $15-25)
        if 15 <= price <= 25:
            return 1.0
        elif 10 <= price <= 35:
            return 0.8
        elif 5 <= price <= 50:
            return 0.6
        else:
            return 0.4
    
    def _calculate_distance_score(self, restaurant_location: Optional[str], user_location: Optional[Tuple[float, float]]) -> float:
        """Calculate distance score (closer = higher score)"""
        if not restaurant_location or not user_location:
            return 0.5  # Neutral score if location data missing
        
        # This would need actual distance calculation
        # For now, return neutral score
        return 0.5
    
    def _get_matched_tags(self, user_tags: ExtractedTags, item_tags: MenuItemTags) -> Dict[str, List[str]]:
        """Get matching tags between user preferences and menu item"""
        matches = {}
        
        # Dietary matches
        dietary_matches = list(set(user_tags.dietary_restrictions) & set(item_tags.dietary_tags))
        if dietary_matches:
            matches['dietary'] = dietary_matches
        
        # Cuisine matches
        if user_tags.cuisine_preferences and item_tags.cuisine_type in user_tags.cuisine_preferences:
            matches['cuisine'] = [item_tags.cuisine_type]
        
        # Health matches
        health_matches = list(set(user_tags.health_goals) & set(item_tags.health_tags))
        if health_matches:
            matches['health'] = health_matches
        
        # Spice matches
        if user_tags.spice_preference and user_tags.spice_preference == item_tags.spice_level:
            matches['spice'] = [item_tags.spice_level]
        
        return matches
    
    def explain_recommendation(self, recommendation: RecommendationResult) -> str:
        """Generate explanation for why this item was recommended"""
        explanation_parts = []
        
        # Semantic similarity
        if recommendation.semantic_similarity > 0.5:
            explanation_parts.append(f"Strong semantic match ({recommendation.semantic_similarity:.1%})")
        
        # Tag matches
        if recommendation.matched_tags:
            tag_explanations = []
            for category, tags in recommendation.matched_tags.items():
                tag_explanations.append(f"{category}: {', '.join(tags)}")
            explanation_parts.append(f"Preference matches: {'; '.join(tag_explanations)}")
        
        # Rating
        if recommendation.rating_score > 0.7:
            explanation_parts.append("Highly rated restaurant")
        
        # Price
        if recommendation.price_score > 0.8:
            explanation_parts.append("Good value for money")
        
        return " | ".join(explanation_parts) if explanation_parts else "General recommendation"

def test_hybrid_recommendations():
    """Test the hybrid recommendation system"""
    
    print("🎯 Testing Hybrid Recommendation Engine")
    print("=" * 60)
    
    try:
        engine = HybridRecommendationEngine()
    except Exception as e:
        print(f"❌ Failed to initialize engine: {e}")
        return
    
    # Test queries
    test_queries = [
        "I want something healthy and vegetarian for lunch",
        "Looking for spicy italian pasta with no dairy",
        "Need a low-carb high-protein dinner option",
        "Craving japanese sushi or ramen"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 50)
        
        try:
            recommendations = engine.get_recommendations(query, limit=5)
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    print(f"\n{i}. {rec.name} - {rec.restaurant_name}")
                    print(f"   Cuisine: {rec.cuisine} | Price: ${rec.price}")
                    print(f"   Total Score: {rec.total_score:.3f}")
                    print(f"   Breakdown: Semantic={rec.semantic_similarity:.2f}, Tags={rec.tag_similarity:.2f}, Rating={rec.rating_score:.2f}")
                    
                    if rec.matched_tags:
                        print(f"   Matches: {rec.matched_tags}")
                    
                    explanation = engine.explain_recommendation(rec)
                    print(f"   Why: {explanation}")
            else:
                print("   ❌ No recommendations found")
                
        except Exception as e:
            print(f"   ❌ Error getting recommendations: {e}")

if __name__ == "__main__":
    test_hybrid_recommendations()
