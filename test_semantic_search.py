#!/usr/bin/env python3
"""
Test semantic search functionality with real queries
"""

import os
import numpy as np
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer

load_dotenv()

class SemanticSearchTester:
    def __init__(self):
        """Initialize the semantic search tester"""
        self.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        )
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        print("🔍 Semantic Search Tester Initialized")
    
    def search_menu_items(self, query: str, limit: int = 10, threshold: float = 0.3):
        """Search for menu items using semantic similarity"""
        print(f"\n🔍 Searching for: '{query}'")
        
        # Generate embedding for query
        query_embedding = self.model.encode([query])[0].tolist()
        
        # Search using Supabase function
        try:
            result = self.supabase.rpc('match_menu_items', {
                'query_embedding': query_embedding,
                'match_threshold': threshold,
                'match_count': limit
            }).execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} similar items:")
                for i, item in enumerate(result.data, 1):
                    similarity_pct = item['similarity'] * 100
                    print(f"  {i}. {item['name']} (similarity: {similarity_pct:.1f}%)")
                    if item['description']:
                        print(f"     Description: {item['description']}")
                    print(f"     Restaurant ID: {item['restaurant_id']}")
                    print()
            else:
                print("❌ No similar items found")
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
    
    def search_with_restaurant_context(self, query: str, cuisine_filter: str = None, max_price: float = None):
        """Search with restaurant context using advanced function"""
        print(f"\n🏪 Searching with context: '{query}'")
        if cuisine_filter:
            print(f"   Cuisine filter: {cuisine_filter}")
        if max_price:
            print(f"   Max price: ${max_price}")
        
        # Generate embedding for query
        query_embedding = self.model.encode([query])[0].tolist()
        
        # Add the advanced search function if it doesn't exist
        try:
            result = self.supabase.rpc('semantic_search_with_restaurant', {
                'query_embedding': query_embedding,
                'cuisine_filter': cuisine_filter,
                'max_price': max_price,
                'match_threshold': 0.2,
                'match_count': 10
            }).execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} contextual matches:")
                for i, item in enumerate(result.data, 1):
                    similarity_pct = item['similarity'] * 100
                    price_str = f"${item['item_price']}" if item['item_price'] else "Price N/A"
                    print(f"  {i}. {item['item_name']} - {item['restaurant_name']}")
                    print(f"     {item['restaurant_cuisine']} | {price_str} | Similarity: {similarity_pct:.1f}%")
                    if item['item_description']:
                        print(f"     {item['item_description']}")
                    print()
            else:
                print("❌ No contextual matches found")
                
        except Exception as e:
            print(f"⚠️  Advanced search not available: {e}")
            print("💡 Please run add_helper_functions.sql in Supabase SQL Editor first")
    
    def get_database_stats(self):
        """Get basic database statistics"""
        print("\n📊 Database Statistics:")
        
        # Restaurant count by cuisine
        restaurants = self.supabase.table('restaurants').select('cuisine').execute()
        if restaurants.data:
            cuisine_counts = {}
            for r in restaurants.data:
                cuisine = r['cuisine'] or 'Unknown'
                cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
            
            print(f"   Total restaurants: {len(restaurants.data)}")
            print(f"   Cuisines represented:")
            for cuisine, count in sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"     - {cuisine}: {count} restaurants")
        
        # Menu item count
        items = self.supabase.table('menu_items').select('id', count='exact').execute()
        print(f"   Total menu items: {items.count}")
        
        # Price range
        price_stats = self.supabase.table('menu_items').select('price').not_.is_('price', 'null').execute()
        if price_stats.data:
            prices = [item['price'] for item in price_stats.data if item['price']]
            if prices:
                print(f"   Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                print(f"   Average price: ${np.mean(prices):.2f}")
    
    def run_demo_searches(self):
        """Run a series of demo searches"""
        print("🚀 Running Semantic Search Demo")
        print("=" * 60)
        
        # Get stats first
        self.get_database_stats()
        
        # Demo searches
        demo_queries = [
            "healthy grilled chicken salad",
            "spicy italian pasta with cheese",
            "fresh sushi rolls",
            "vegetarian pizza with vegetables",
            "chocolate dessert",
            "burger and fries",
            "thai curry with rice",
            "french wine and cheese"
        ]
        
        for query in demo_queries:
            self.search_menu_items(query, limit=5, threshold=0.2)
        
        # Demo contextual search
        print("\n" + "=" * 60)
        print("🎯 Testing Contextual Search")
        
        try:
            # Try contextual searches
            self.search_with_restaurant_context("pizza", cuisine_filter="Italian", max_price=25)
            self.search_with_restaurant_context("healthy salad", max_price=20)
        except Exception as e:
            print(f"💡 Contextual search requires additional SQL functions")

if __name__ == "__main__":
    tester = SemanticSearchTester()
    tester.run_demo_searches()
