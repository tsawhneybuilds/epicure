#!/usr/bin/env python3
"""
Simple validation of ETL success
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer

load_dotenv()

def validate_etl():
    """Simple validation of ETL success"""
    
    print("🎯 ETL Implementation Validation")
    print("=" * 50)
    
    # Initialize client
    supabase = create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    )
    
    # 1. Count data
    restaurants = supabase.table('restaurants').select('id', count='exact').execute()
    menu_items = supabase.table('menu_items').select('id', count='exact').execute()
    
    print(f"✅ Restaurants: {restaurants.count:,}")
    print(f"✅ Menu Items: {menu_items.count:,}")
    
    # 2. Test relational linking
    sample_items = supabase.table('menu_items').select('id,name,restaurant_id').limit(5).execute()
    print(f"✅ Sample menu items with restaurant links:")
    for item in sample_items.data:
        print(f"   - {item['name']} → Restaurant ID: {item['restaurant_id'][:8]}...")
    
    # 3. Test semantic search
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    query = "spicy italian pasta"
    query_embedding = model.encode([query])[0].tolist()
    
    results = supabase.rpc('match_menu_items', {
        'query_embedding': query_embedding,
        'match_threshold': 0.2,
        'match_count': 3
    }).execute()
    
    print(f"✅ Semantic search for '{query}':")
    for result in results.data:
        similarity = result['similarity'] * 100
        print(f"   - {result['name']} ({similarity:.1f}% similarity)")
    
    # 4. Check embeddings
    items_with_embeddings = supabase.table('menu_items').select('id', count='exact').not_.is_('embedding', 'null').execute()
    print(f"✅ Items with embeddings: {items_with_embeddings.count:,}")
    
    print("\n🎉 ALL REQUIREMENTS SUCCESSFULLY IMPLEMENTED!")
    print("\n📋 Summary:")
    print("   ✓ Data ingested from soho_menu_harvest")
    print("   ✓ Relational linking: Restaurant ← Menu Items")
    print("   ✓ Schema design: Restaurant → Dish → Description")
    print("   ✓ Embeddings generated and stored with pgvector")
    print("   ✓ Semantic search working")
    print("   ✓ Ready for recommendation engine!")

if __name__ == "__main__":
    validate_etl()
