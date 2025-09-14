#!/usr/bin/env python3
"""
Batch generate and store tags for all menu items in database
"""

import os
import json
import time
from typing import List, Dict
from dotenv import load_dotenv
from supabase import create_client
from tag_inference_service import TagInferenceService

load_dotenv()

class BatchTagGenerator:
    def __init__(self):
        """Initialize batch tag generator"""
        self.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        )
        self.tag_service = TagInferenceService()
        
        print("🏷️ Batch Tag Generator initialized")
    
    def add_tag_columns_to_schema(self):
        """Add tag storage columns to menu_items table"""
        print("📊 Adding tag columns to database schema...")
        
        # Add columns for storing inferred tags
        alter_statements = [
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_dietary_tags TEXT[];",
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_cuisine_type VARCHAR(50);",
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_health_tags TEXT[];",
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_spice_level VARCHAR(20);",
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_meal_category VARCHAR(30);",
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_cooking_methods TEXT[];",
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_allergens TEXT[];",
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS tag_confidence NUMERIC(3,2);",
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS tags_generated_at TIMESTAMPTZ;"
        ]
        
        for statement in alter_statements:
            try:
                # Note: Direct SQL execution not available via REST API
                # These need to be run manually in Supabase SQL Editor
                print(f"   📝 SQL: {statement}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("💡 Please run these ALTER statements in Supabase SQL Editor:")
        for statement in alter_statements:
            print(f"   {statement}")
    
    def get_menu_items_needing_tags(self, limit: int = 100) -> List[Dict]:
        """Get menu items that need tag generation"""
        
        # Get items without tags or with empty name/description
        items = self.supabase.table('menu_items').select(
            'id,restaurant_id,name,description,price'
        ).is_('inferred_dietary_tags', 'null').limit(limit).execute()
        
        # Filter out items with empty name and description
        valid_items = []
        removed_count = 0
        
        for item in items.data:
            name = item.get('name', '').strip()
            description = item.get('description', '').strip() if item.get('description') else ''
            
            if not name and not description:
                # Remove items with no usable content
                try:
                    self.supabase.table('menu_items').delete().eq('id', item['id']).execute()
                    removed_count += 1
                except Exception as e:
                    print(f"   ⚠️ Failed to remove empty item {item['id']}: {e}")
            else:
                valid_items.append(item)
        
        if removed_count > 0:
            print(f"🗑️ Removed {removed_count} items with empty name and description")
        
        return valid_items
    
    def get_restaurant_context(self, restaurant_id: str) -> Dict:
        """Get restaurant context for better tag inference"""
        
        restaurant = self.supabase.table('restaurants').select(
            'name,cuisine'
        ).eq('id', restaurant_id).single().execute()
        
        if restaurant.data:
            return {
                'restaurant_name': restaurant.data.get('name', ''),
                'restaurant_cuisine': restaurant.data.get('cuisine', '')
            }
        
        return {'restaurant_name': '', 'restaurant_cuisine': ''}
    
    def generate_tags_for_item(self, item: Dict, restaurant_context: Dict) -> Dict:
        """Generate tags for a single menu item"""
        
        name = item.get('name', '').strip()
        description = item.get('description', '').strip() if item.get('description') else ''
        
        # Skip if no usable content
        if not name and not description:
            return None
        
        try:
            # Infer tags using the service
            item_tags = self.tag_service.infer_menu_item_tags(
                name, 
                description, 
                restaurant_context.get('restaurant_cuisine', '')
            )
            
            # Convert to database format
            tag_data = {
                'inferred_dietary_tags': item_tags.dietary_tags,
                'inferred_cuisine_type': item_tags.cuisine_type,
                'inferred_health_tags': item_tags.health_tags,
                'inferred_spice_level': item_tags.spice_level,
                'inferred_meal_category': item_tags.meal_category,
                'inferred_cooking_methods': item_tags.cooking_methods,
                'inferred_allergens': item_tags.allergens,
                'tag_confidence': item_tags.confidence,
                'tags_generated_at': 'NOW()'
            }
            
            return tag_data
            
        except Exception as e:
            print(f"   ❌ Error generating tags for {name}: {e}")
            return None
    
    def batch_generate_tags(self, batch_size: int = 50, max_items: int = 1000):
        """Generate tags for all menu items in batches"""
        
        print(f"🚀 Starting batch tag generation (batch_size={batch_size}, max_items={max_items})")
        
        total_processed = 0
        total_successful = 0
        
        # Cache restaurant contexts to avoid repeated queries
        restaurant_cache = {}
        
        while total_processed < max_items:
            # Get next batch of items
            items = self.get_menu_items_needing_tags(batch_size)
            
            if not items:
                print("✅ No more items need tag generation")
                break
            
            print(f"\n📦 Processing batch of {len(items)} items...")
            
            batch_updates = []
            
            for i, item in enumerate(items):
                if total_processed >= max_items:
                    break
                
                # Get restaurant context (with caching)
                restaurant_id = item['restaurant_id']
                if restaurant_id not in restaurant_cache:
                    restaurant_cache[restaurant_id] = self.get_restaurant_context(restaurant_id)
                
                restaurant_context = restaurant_cache[restaurant_id]
                
                # Generate tags
                print(f"   🏷️ {i+1}/{len(items)}: {item.get('name', 'Unnamed item')}")
                tag_data = self.generate_tags_for_item(item, restaurant_context)
                
                if tag_data:
                    # Update item in database
                    try:
                        self.supabase.table('menu_items').update(tag_data).eq('id', item['id']).execute()
                        total_successful += 1
                        print(f"      ✅ Tags: {tag_data['inferred_dietary_tags']}, {tag_data['inferred_cuisine_type']}")
                    except Exception as e:
                        print(f"      ❌ Failed to update: {e}")
                
                total_processed += 1
                
                # Rate limiting to avoid hitting API limits
                if i % 10 == 0:
                    time.sleep(1)  # Brief pause every 10 items
            
            print(f"📊 Batch complete. Processed: {total_processed}, Successful: {total_successful}")
            
            # Longer pause between batches
            if total_processed < max_items and items:
                print("⏸️ Pausing between batches...")
                time.sleep(5)
        
        print(f"\n🎉 Tag generation complete!")
        print(f"📊 Final stats:")
        print(f"   Total processed: {total_processed}")
        print(f"   Successfully tagged: {total_successful}")
        print(f"   Success rate: {(total_successful/total_processed*100):.1f}%")
    
    def verify_tag_coverage(self):
        """Check how many items have tags"""
        
        total_items = self.supabase.table('menu_items').select('id', count='exact').execute()
        tagged_items = self.supabase.table('menu_items').select('id', count='exact').not_.is_('inferred_dietary_tags', 'null').execute()
        
        coverage = (tagged_items.count / total_items.count * 100) if total_items.count > 0 else 0
        
        print(f"📊 Tag Coverage Report:")
        print(f"   Total menu items: {total_items.count:,}")
        print(f"   Items with tags: {tagged_items.count:,}")
        print(f"   Coverage: {coverage:.1f}%")
        
        return coverage

def main():
    """Main execution"""
    
    print("🏷️ Batch Tag Generation for Epicure")
    print("=" * 50)
    
    generator = BatchTagGenerator()
    
    # Check current coverage
    generator.verify_tag_coverage()
    
    # Show schema update instructions
    generator.add_tag_columns_to_schema()
    
    # Ask user if they want to proceed
    print("\n" + "="*50)
    response = input("📝 Have you run the SQL schema updates? (y/n): ")
    
    if response.lower() == 'y':
        print("\n🚀 Starting tag generation...")
        generator.batch_generate_tags(batch_size=20, max_items=200)  # Start with smaller batch for testing
        
        print("\n📊 Final coverage check:")
        generator.verify_tag_coverage()
    else:
        print("💡 Please run the SQL schema updates first, then run this script again.")

if __name__ == "__main__":
    main()
