#!/usr/bin/env python3
"""
Comprehensive Batch Generator: Tags + Nutrition
Generate and store both tag and nutrition data for all menu items
"""

import os
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
from supabase import create_client
from tag_inference_service import TagInferenceService
from nutrition_inference_service import NutritionInferenceService

load_dotenv()

class ComprehensiveBatchGenerator:
    def __init__(self):
        """Initialize comprehensive batch generator"""
        self.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        )
        self.tag_service = TagInferenceService()
        self.nutrition_service = NutritionInferenceService()
        
        print("🏷️🥗 Comprehensive Batch Generator initialized")
        print("    - Tag inference: Llama-3.3-70B")
        print("    - Nutrition inference: Llama-3.3-70B with expert nutritionist prompting")
    
    def get_items_needing_processing(self, limit: int = 50) -> List[Dict]:
        """Get menu items that need tag and nutrition processing"""
        
        # Get items without tags OR nutrition data
        items = self.supabase.table('menu_items').select(
            'id,restaurant_id,name,description,price'
        ).or_(
            'inferred_dietary_tags.is.null,estimated_calories.is.null'
        ).limit(limit).execute()
        
        # Filter out items with no usable content
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
                    print(f"🗑️ Removed empty item: {item['id']}")
                except Exception as e:
                    print(f"   ⚠️ Failed to remove empty item {item['id']}: {e}")
            else:
                valid_items.append(item)
        
        if removed_count > 0:
            print(f"🗑️ Removed {removed_count} items with empty name and description")
        
        return valid_items
    
    def get_restaurant_context(self, restaurant_id: str) -> Dict:
        """Get restaurant context for better inference"""
        
        try:
            restaurant = self.supabase.table('restaurants').select(
                'name,cuisine'
            ).eq('id', restaurant_id).single().execute()
            
            if restaurant.data:
                return {
                    'restaurant_name': restaurant.data.get('name', ''),
                    'restaurant_cuisine': restaurant.data.get('cuisine', '')
                }
        except Exception as e:
            print(f"   ⚠️ Error getting restaurant context: {e}")
        
        return {'restaurant_name': '', 'restaurant_cuisine': ''}
    
    def process_single_item(self, item: Dict, restaurant_context: Dict) -> Optional[Dict]:
        """Process a single menu item for both tags and nutrition"""
        
        name = item.get('name', '').strip()
        description = item.get('description', '').strip() if item.get('description') else ''
        price = item.get('price')
        
        # Skip if no usable content
        if not name and not description:
            return None
        
        print(f"   🔄 Processing: {name}")
        
        try:
            # Generate tags
            print(f"      🏷️ Inferring tags...")
            item_tags = self.tag_service.infer_menu_item_tags(
                name, 
                description, 
                restaurant_context.get('restaurant_cuisine', '')
            )
            
            # Generate nutrition
            print(f"      🥗 Estimating nutrition...")
            nutrition = self.nutrition_service.estimate_nutrition(
                name,
                description,
                price,
                restaurant_context.get('restaurant_cuisine', '')
            )
            
            # Enhance health tags with nutrition-based tags
            enhanced_health_tags = self.nutrition_service.enhance_health_tags_with_macros(
                nutrition, item_tags.health_tags
            )
            
            # Prepare update data
            update_data = {
                # Tag data
                'inferred_dietary_tags': item_tags.dietary_tags,
                'inferred_cuisine_type': item_tags.cuisine_type,
                'inferred_health_tags': enhanced_health_tags,  # Enhanced with macro-based tags
                'inferred_spice_level': item_tags.spice_level,
                'inferred_meal_category': item_tags.meal_category,
                'inferred_cooking_methods': item_tags.cooking_methods,
                'inferred_allergens': item_tags.allergens,
                'tag_confidence': item_tags.confidence,
                'tags_generated_at': 'NOW()',
                
                # Nutrition data
                'estimated_calories': nutrition.calories,
                'estimated_protein_g': nutrition.protein_g,
                'estimated_carbs_g': nutrition.carbs_g,
                'estimated_fat_g': nutrition.fat_g,
                'estimated_fiber_g': nutrition.fiber_g,
                'estimated_sugar_g': nutrition.sugar_g,
                'estimated_sodium_mg': nutrition.sodium_mg,
                'calories_per_100g': nutrition.calories_per_100g,
                'protein_ratio': nutrition.protein_ratio,
                'carb_ratio': nutrition.carb_ratio,
                'fat_ratio': nutrition.fat_ratio,
                'nutrition_confidence': nutrition.confidence,
                'estimation_method': nutrition.estimation_method,
                'portion_size_assumption': nutrition.portion_size_assumption,
                'nutrition_generated_at': 'NOW()'
            }
            
            print(f"      ✅ Tags: {item_tags.dietary_tags}, Cuisine: {item_tags.cuisine_type}")
            print(f"      ✅ Nutrition: {nutrition.calories} cal, {nutrition.protein_g}g protein")
            print(f"      ✅ Enhanced health tags: {enhanced_health_tags}")
            
            return update_data
            
        except Exception as e:
            print(f"      ❌ Error processing {name}: {e}")
            return None
    
    def batch_process_all(self, batch_size: int = 20, max_items: int = 200):
        """Process all menu items in batches"""
        
        print(f"🚀 Starting comprehensive batch processing")
        print(f"   Batch size: {batch_size}")
        print(f"   Max items: {max_items}")
        print(f"   Processing: Tags + Nutrition + Enhanced Health Tags")
        print()
        
        total_processed = 0
        total_successful = 0
        
        # Cache restaurant contexts
        restaurant_cache = {}
        
        while total_processed < max_items:
            # Get next batch
            items = self.get_items_needing_processing(batch_size)
            
            if not items:
                print("✅ No more items need processing")
                break
            
            print(f"📦 Processing batch of {len(items)} items...")
            
            for i, item in enumerate(items):
                if total_processed >= max_items:
                    break
                
                # Get restaurant context (with caching)
                restaurant_id = item['restaurant_id']
                if restaurant_id not in restaurant_cache:
                    restaurant_cache[restaurant_id] = self.get_restaurant_context(restaurant_id)
                
                restaurant_context = restaurant_cache[restaurant_id]
                
                # Process item
                print(f"   🎯 {total_processed + 1}/{max_items}: {item.get('name', 'Unnamed')}")
                update_data = self.process_single_item(item, restaurant_context)
                
                if update_data:
                    # Update database
                    try:
                        self.supabase.table('menu_items').update(update_data).eq('id', item['id']).execute()
                        total_successful += 1
                    except Exception as e:
                        print(f"      ❌ Database update failed: {e}")
                
                total_processed += 1
                
                # Rate limiting to avoid API limits
                if i % 5 == 0:
                    time.sleep(2)  # Pause every 5 items
            
            print(f"📊 Batch complete. Processed: {total_processed}, Successful: {total_successful}")
            
            # Longer pause between batches
            if total_processed < max_items and items:
                print("⏸️ Pausing between batches...")
                time.sleep(10)
        
        print(f"\n🎉 Comprehensive processing complete!")
        print(f"📊 Final stats:")
        print(f"   Total processed: {total_processed}")
        print(f"   Successfully updated: {total_successful}")
        print(f"   Success rate: {(total_successful/total_processed*100):.1f}%")
        
        # Final coverage report
        self.generate_coverage_report()
    
    def generate_coverage_report(self):
        """Generate comprehensive coverage report"""
        
        print(f"\n📊 Coverage Report:")
        print("=" * 50)
        
        try:
            # Get basic counts
            total_items = self.supabase.table('menu_items').select('id', count='exact').execute()
            items_with_tags = self.supabase.table('menu_items').select('id', count='exact').not_.is_('inferred_dietary_tags', 'null').execute()
            items_with_nutrition = self.supabase.table('menu_items').select('id', count='exact').not_.is_('estimated_calories', 'null').execute()
            items_with_both = self.supabase.table('menu_items').select('id', count='exact').not_.is_('inferred_dietary_tags', 'null').not_.is_('estimated_calories', 'null').execute()
            
            tag_coverage = (items_with_tags.count / total_items.count * 100) if total_items.count > 0 else 0
            nutrition_coverage = (items_with_nutrition.count / total_items.count * 100) if total_items.count > 0 else 0
            complete_coverage = (items_with_both.count / total_items.count * 100) if total_items.count > 0 else 0
            
            print(f"Total menu items: {total_items.count:,}")
            print(f"Items with tags: {items_with_tags.count:,} ({tag_coverage:.1f}%)")
            print(f"Items with nutrition: {items_with_nutrition.count:,} ({nutrition_coverage:.1f}%)")
            print(f"Items with both: {items_with_both.count:,} ({complete_coverage:.1f}%)")
            
            # Sample some completed items
            print(f"\n🔍 Sample processed items:")
            sample_items = self.supabase.table('menu_items').select(
                'name,inferred_dietary_tags,estimated_calories,estimated_protein_g,inferred_health_tags'
            ).not_.is_('estimated_calories', 'null').limit(5).execute()
            
            for item in sample_items.data:
                print(f"   • {item['name']}")
                print(f"     Dietary: {item['inferred_dietary_tags']}")
                print(f"     Health: {item['inferred_health_tags']}")
                print(f"     Nutrition: {item['estimated_calories']} cal, {item['estimated_protein_g']}g protein")
                print()
            
        except Exception as e:
            print(f"❌ Error generating coverage report: {e}")

def main():
    """Main execution"""
    
    print("🏷️🥗 Comprehensive Batch Generation for Epicure")
    print("=" * 60)
    print("This will generate:")
    print("  🏷️ Dietary tags, cuisine types, health tags, spice levels")
    print("  🥗 Estimated calories, protein, carbs, fat, fiber, sodium")
    print("  🧬 Enhanced health tags based on macros")
    print("  📊 Nutritional ratios and confidence scores")
    print()
    
    generator = ComprehensiveBatchGenerator()
    
    # Check current coverage
    generator.generate_coverage_report()
    
    print("\n" + "="*60)
    print("⚠️  IMPORTANT: Make sure you've run comprehensive_schema_update.sql first!")
    response = input("📝 Have you run the SQL schema updates? (y/n): ")
    
    if response.lower() == 'y':
        print("\n🚀 Starting comprehensive processing...")
        generator.batch_process_all(batch_size=15, max_items=100)  # Start with smaller batch
    else:
        print("💡 Please run comprehensive_schema_update.sql first, then run this script again.")

if __name__ == "__main__":
    main()
