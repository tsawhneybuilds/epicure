#!/usr/bin/env python3
"""
Generate 500 additional diverse menu items for Epicure
Creates realistic menu items across different cuisines and categories
"""

import os
import json
import uuid
import random
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

@dataclass
class MenuItemData:
    name: str
    description: str
    price: float
    cuisine_type: str
    category: str
    dietary_tags: List[str]
    allergens: List[str]
    estimated_calories: int
    estimated_protein_g: float
    estimated_carbs_g: float
    estimated_fat_g: float

class MenuItemGenerator:
    def __init__(self):
        """Initialize menu item generator"""
        self.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        # Get existing restaurants for assignment
        self.restaurants = self._get_restaurants()
        print(f"🏪 Found {len(self.restaurants)} restaurants for menu item assignment")
        
        # Menu item templates by cuisine
        self.menu_templates = self._initialize_menu_templates()
        
    def _get_restaurants(self) -> List[Dict]:
        """Get existing restaurants from database"""
        try:
            restaurants = self.supabase.table('restaurants').select('id,name,cuisine').execute()
            return restaurants.data
        except Exception as e:
            print(f"❌ Error fetching restaurants: {e}")
            return []
    
    def _initialize_menu_templates(self) -> Dict[str, List[Dict]]:
        """Initialize menu item templates by cuisine"""
        return {
            'Italian': [
                {'name': 'Truffle Mushroom Risotto', 'description': 'Creamy arborio rice with wild mushrooms, truffle oil, and parmesan', 'price_range': (18, 28), 'calories': 520, 'protein': 18, 'carbs': 65, 'fat': 22, 'dietary': [], 'allergens': ['dairy', 'gluten']},
                {'name': 'Osso Buco Milanese', 'description': 'Braised veal shanks with saffron risotto and gremolata', 'price_range': (32, 42), 'calories': 680, 'protein': 45, 'carbs': 35, 'fat': 38, 'dietary': [], 'allergens': ['dairy', 'gluten']},
                {'name': 'Burrata Caprese', 'description': 'Fresh burrata with heirloom tomatoes, basil, and balsamic glaze', 'price_range': (14, 20), 'calories': 320, 'protein': 12, 'carbs': 15, 'fat': 24, 'dietary': ['vegetarian'], 'allergens': ['dairy']},
                {'name': 'Lobster Ravioli', 'description': 'House-made pasta filled with lobster, ricotta, and herbs in tomato cream sauce', 'price_range': (26, 34), 'calories': 580, 'protein': 28, 'carbs': 45, 'fat': 32, 'dietary': [], 'allergens': ['dairy', 'gluten', 'shellfish']},
                {'name': 'Arancini al Tartufo', 'description': 'Crispy risotto balls with truffle and mozzarella, served with marinara', 'price_range': (12, 18), 'calories': 420, 'protein': 15, 'carbs': 48, 'fat': 18, 'dietary': ['vegetarian'], 'allergens': ['dairy', 'gluten', 'eggs']},
            ],
            'Japanese': [
                {'name': 'Wagyu Beef Tataki', 'description': 'Seared wagyu beef with ponzu sauce, daikon, and microgreens', 'price_range': (28, 38), 'calories': 380, 'protein': 35, 'carbs': 8, 'fat': 22, 'dietary': ['gluten-free'], 'allergens': ['soy']},
                {'name': 'Uni Chawanmushi', 'description': 'Silky egg custard with sea urchin, dashi, and shiitake mushrooms', 'price_range': (16, 22), 'calories': 180, 'protein': 12, 'carbs': 6, 'fat': 12, 'dietary': ['gluten-free'], 'allergens': ['eggs', 'shellfish']},
                {'name': 'Toro Sashimi', 'description': 'Premium fatty tuna belly sashimi with wasabi and pickled ginger', 'price_range': (24, 32), 'calories': 220, 'protein': 25, 'carbs': 2, 'fat': 12, 'dietary': ['gluten-free', 'keto'], 'allergens': ['fish']},
                {'name': 'Miso Black Cod', 'description': 'Marinated black cod with miso glaze, served with steamed rice', 'price_range': (26, 34), 'calories': 450, 'protein': 38, 'carbs': 25, 'fat': 22, 'dietary': ['gluten-free'], 'allergens': ['fish', 'soy']},
                {'name': 'Vegetable Tempura', 'description': 'Seasonal vegetables in light tempura batter with tentsuyu dipping sauce', 'price_range': (14, 20), 'calories': 380, 'protein': 8, 'carbs': 45, 'fat': 18, 'dietary': ['vegetarian'], 'allergens': ['gluten', 'eggs']},
            ],
            'Mexican': [
                {'name': 'Cochinita Pibil', 'description': 'Slow-roasted pork marinated in achiote and citrus, served with pickled onions', 'price_range': (18, 26), 'calories': 520, 'protein': 42, 'carbs': 15, 'fat': 32, 'dietary': ['gluten-free'], 'allergens': []},
                {'name': 'Chiles en Nogada', 'description': 'Poblano peppers stuffed with picadillo, topped with walnut cream sauce and pomegranate', 'price_range': (22, 28), 'calories': 480, 'protein': 18, 'carbs': 35, 'fat': 28, 'dietary': ['vegetarian'], 'allergens': ['nuts', 'dairy']},
                {'name': 'Ceviche de Camarón', 'description': 'Fresh shrimp ceviche with lime, cilantro, red onion, and avocado', 'price_range': (16, 22), 'calories': 280, 'protein': 25, 'carbs': 12, 'fat': 15, 'dietary': ['gluten-free', 'keto'], 'allergens': ['shellfish']},
                {'name': 'Mole Poblano', 'description': 'Chicken in rich mole sauce with 20+ ingredients, served with rice and tortillas', 'price_range': (20, 28), 'calories': 580, 'protein': 35, 'carbs': 45, 'fat': 28, 'dietary': ['gluten-free'], 'allergens': ['nuts']},
                {'name': 'Queso Fundido', 'description': 'Melted cheese with chorizo, poblano peppers, and warm tortillas', 'price_range': (14, 20), 'calories': 420, 'protein': 22, 'carbs': 8, 'fat': 32, 'dietary': ['gluten-free'], 'allergens': ['dairy']},
            ],
            'American': [
                {'name': 'Dry-Aged Ribeye', 'description': '28-day dry-aged ribeye with roasted bone marrow and truffle butter', 'price_range': (45, 65), 'calories': 780, 'protein': 65, 'carbs': 8, 'fat': 52, 'dietary': ['gluten-free', 'keto'], 'allergens': ['dairy']},
                {'name': 'Lobster Roll', 'description': 'Fresh Maine lobster with mayo and herbs on brioche bun with fries', 'price_range': (24, 32), 'calories': 680, 'protein': 35, 'carbs': 45, 'fat': 38, 'dietary': [], 'allergens': ['shellfish', 'gluten', 'eggs']},
                {'name': 'BBQ Brisket Sandwich', 'description': 'Smoked brisket with house BBQ sauce, coleslaw, and pickles on brioche', 'price_range': (18, 26), 'calories': 720, 'protein': 42, 'carbs': 55, 'fat': 35, 'dietary': [], 'allergens': ['gluten']},
                {'name': 'Buffalo Cauliflower Wings', 'description': 'Crispy cauliflower in buffalo sauce with blue cheese dip and celery', 'price_range': (12, 18), 'calories': 320, 'protein': 8, 'carbs': 35, 'fat': 18, 'dietary': ['vegetarian', 'vegan'], 'allergens': []},
                {'name': 'Truffle Mac and Cheese', 'description': 'Three-cheese macaroni with truffle oil and crispy breadcrumbs', 'price_range': (16, 22), 'calories': 580, 'protein': 22, 'carbs': 45, 'fat': 35, 'dietary': ['vegetarian'], 'allergens': ['dairy', 'gluten']},
            ],
            'Thai': [
                {'name': 'Tom Kha Gai', 'description': 'Coconut milk soup with chicken, galangal, lemongrass, and kaffir lime', 'price_range': (14, 20), 'calories': 320, 'protein': 22, 'carbs': 15, 'fat': 20, 'dietary': ['gluten-free'], 'allergens': []},
                {'name': 'Pad Thai Goong', 'description': 'Stir-fried rice noodles with shrimp, bean sprouts, and tamarind sauce', 'price_range': (16, 24), 'calories': 480, 'protein': 28, 'carbs': 55, 'fat': 18, 'dietary': [], 'allergens': ['shellfish', 'eggs', 'nuts']},
                {'name': 'Green Curry', 'description': 'Spicy green curry with chicken, eggplant, and Thai basil over jasmine rice', 'price_range': (18, 26), 'calories': 520, 'protein': 32, 'carbs': 35, 'fat': 28, 'dietary': ['gluten-free'], 'allergens': []},
                {'name': 'Som Tam', 'description': 'Green papaya salad with tomatoes, green beans, peanuts, and spicy dressing', 'price_range': (12, 18), 'calories': 180, 'protein': 6, 'carbs': 25, 'fat': 8, 'dietary': ['vegetarian', 'vegan', 'gluten-free'], 'allergens': ['nuts']},
                {'name': 'Massaman Curry', 'description': 'Rich curry with beef, potatoes, and peanuts in coconut milk', 'price_range': (20, 28), 'calories': 580, 'protein': 35, 'carbs': 42, 'fat': 32, 'dietary': ['gluten-free'], 'allergens': ['nuts']},
            ],
            'Mediterranean': [
                {'name': 'Grilled Octopus', 'description': 'Tender grilled octopus with lemon, olive oil, and oregano', 'price_range': (22, 30), 'calories': 280, 'protein': 35, 'carbs': 8, 'fat': 12, 'dietary': ['gluten-free', 'keto'], 'allergens': ['shellfish']},
                {'name': 'Lamb Kofta', 'description': 'Spiced lamb meatballs with tzatziki, pita, and Greek salad', 'price_range': (18, 26), 'calories': 520, 'protein': 38, 'carbs': 25, 'fat': 28, 'dietary': ['gluten-free'], 'allergens': ['dairy']},
                {'name': 'Falafel Bowl', 'description': 'Crispy falafel with hummus, tabbouleh, and tahini dressing', 'price_range': (14, 20), 'calories': 420, 'protein': 18, 'carbs': 45, 'fat': 18, 'dietary': ['vegetarian', 'vegan'], 'allergens': ['gluten']},
                {'name': 'Spanakopita', 'description': 'Spinach and feta pie wrapped in phyllo pastry', 'price_range': (12, 18), 'calories': 380, 'protein': 15, 'carbs': 35, 'fat': 22, 'dietary': ['vegetarian'], 'allergens': ['dairy', 'gluten', 'eggs']},
                {'name': 'Branzino al Sale', 'description': 'Whole sea bass baked in salt crust with herbs and lemon', 'price_range': (28, 38), 'calories': 320, 'protein': 42, 'carbs': 2, 'fat': 15, 'dietary': ['gluten-free', 'keto'], 'allergens': ['fish']},
            ],
            'Indian': [
                {'name': 'Butter Chicken', 'description': 'Tandoori chicken in creamy tomato curry with basmati rice and naan', 'price_range': (18, 26), 'calories': 680, 'protein': 42, 'carbs': 55, 'fat': 32, 'dietary': ['gluten-free'], 'allergens': ['dairy']},
                {'name': 'Dal Makhani', 'description': 'Slow-cooked black lentils with cream, butter, and aromatic spices', 'price_range': (14, 20), 'calories': 420, 'protein': 18, 'carbs': 45, 'fat': 18, 'dietary': ['vegetarian', 'gluten-free'], 'allergens': ['dairy']},
                {'name': 'Biryani', 'description': 'Fragrant basmati rice with spiced meat, saffron, and fried onions', 'price_range': (20, 28), 'calories': 580, 'protein': 35, 'carbs': 65, 'fat': 22, 'dietary': ['gluten-free'], 'allergens': []},
                {'name': 'Chana Masala', 'description': 'Spiced chickpea curry with tomatoes, onions, and garam masala', 'price_range': (12, 18), 'calories': 320, 'protein': 15, 'carbs': 45, 'fat': 8, 'dietary': ['vegetarian', 'vegan', 'gluten-free'], 'allergens': []},
                {'name': 'Tandoori Salmon', 'description': 'Salmon marinated in yogurt and spices, cooked in tandoor oven', 'price_range': (22, 30), 'calories': 380, 'protein': 42, 'carbs': 8, 'fat': 18, 'dietary': ['gluten-free', 'keto'], 'allergens': ['fish', 'dairy']},
            ],
            'Chinese': [
                {'name': 'Peking Duck', 'description': 'Crispy duck with pancakes, hoisin sauce, and scallions', 'price_range': (35, 45), 'calories': 580, 'protein': 45, 'carbs': 25, 'fat': 32, 'dietary': ['gluten-free'], 'allergens': ['soy']},
                {'name': 'Mapo Tofu', 'description': 'Spicy tofu with ground pork in Sichuan sauce over rice', 'price_range': (16, 22), 'calories': 420, 'protein': 22, 'carbs': 25, 'fat': 22, 'dietary': ['gluten-free'], 'allergens': ['soy']},
                {'name': 'Xiao Long Bao', 'description': 'Soup dumplings filled with pork and hot broth', 'price_range': (12, 18), 'calories': 280, 'protein': 15, 'carbs': 35, 'fat': 8, 'dietary': [], 'allergens': ['gluten']},
                {'name': 'Kung Pao Chicken', 'description': 'Diced chicken with peanuts, vegetables, and spicy sauce', 'price_range': (16, 24), 'calories': 480, 'protein': 35, 'carbs': 18, 'fat': 28, 'dietary': ['gluten-free'], 'allergens': ['nuts', 'soy']},
                {'name': 'Vegetable Lo Mein', 'description': 'Stir-fried noodles with mixed vegetables and light sauce', 'price_range': (14, 20), 'calories': 420, 'protein': 12, 'carbs': 65, 'fat': 12, 'dietary': ['vegetarian'], 'allergens': ['gluten', 'soy']},
            ],
            'French': [
                {'name': 'Coq au Vin', 'description': 'Braised chicken in red wine with mushrooms, onions, and bacon', 'price_range': (24, 32), 'calories': 520, 'protein': 42, 'carbs': 15, 'fat': 28, 'dietary': ['gluten-free'], 'allergens': []},
                {'name': 'Bouillabaisse', 'description': 'Provençal fish stew with saffron, fennel, and rouille', 'price_range': (28, 38), 'calories': 420, 'protein': 35, 'carbs': 18, 'fat': 22, 'dietary': ['gluten-free'], 'allergens': ['fish', 'shellfish']},
                {'name': 'Ratatouille', 'description': 'Provençal vegetable stew with eggplant, zucchini, and tomatoes', 'price_range': (16, 22), 'calories': 180, 'protein': 6, 'carbs': 25, 'fat': 8, 'dietary': ['vegetarian', 'vegan', 'gluten-free'], 'allergens': []},
                {'name': 'Duck Confit', 'description': 'Slow-cooked duck leg with crispy skin and cherry gastrique', 'price_range': (26, 34), 'calories': 580, 'protein': 45, 'carbs': 8, 'fat': 42, 'dietary': ['gluten-free', 'keto'], 'allergens': []},
                {'name': 'Tarte Tatin', 'description': 'Upside-down apple tart with caramel and vanilla ice cream', 'price_range': (12, 18), 'calories': 480, 'protein': 6, 'carbs': 65, 'fat': 22, 'dietary': ['vegetarian'], 'allergens': ['dairy', 'gluten', 'eggs']},
            ]
        }
    
    def generate_menu_items(self, count: int = 500) -> List[MenuItemData]:
        """Generate diverse menu items"""
        print(f"🍽️ Generating {count} diverse menu items...")
        
        menu_items = []
        cuisines = list(self.menu_templates.keys())
        
        for i in range(count):
            # Select random cuisine
            cuisine = random.choice(cuisines)
            template = random.choice(self.menu_templates[cuisine])
            
            # Add variation to the template
            item = self._create_variation(template, cuisine)
            menu_items.append(item)
            
            if (i + 1) % 50 == 0:
                print(f"   Generated {i + 1}/{count} items...")
        
        print(f"✅ Generated {len(menu_items)} menu items")
        return menu_items
    
    def _create_variation(self, template: Dict, cuisine: str) -> MenuItemData:
        """Create a variation of a template menu item"""
        
        # Add slight variations to name and description
        name_variations = {
            'Italian': ['House', 'Chef\'s', 'Traditional', 'Authentic', 'Classic'],
            'Japanese': ['Fresh', 'Premium', 'Artisan', 'Traditional', 'Chef\'s'],
            'Mexican': ['Authentic', 'Traditional', 'House', 'Chef\'s', 'Grandma\'s'],
            'American': ['House', 'Chef\'s', 'Signature', 'Classic', 'Premium'],
            'Thai': ['Authentic', 'Traditional', 'Chef\'s', 'House', 'Spicy'],
            'Mediterranean': ['Fresh', 'Traditional', 'House', 'Chef\'s', 'Authentic'],
            'Indian': ['Traditional', 'Authentic', 'Chef\'s', 'House', 'Spicy'],
            'Chinese': ['Authentic', 'Traditional', 'Chef\'s', 'House', 'Premium'],
            'French': ['Classic', 'Traditional', 'Chef\'s', 'House', 'Authentic']
        }
        
        prefix = random.choice(name_variations.get(cuisine, ['House']))
        name = f"{prefix} {template['name']}"
        
        # Vary the price within the range
        price = random.uniform(template['price_range'][0], template['price_range'][1])
        price = round(price, 2)
        
        # Add slight variations to nutrition (within 10%)
        calories = int(template['calories'] * random.uniform(0.9, 1.1))
        protein = round(template['protein'] * random.uniform(0.9, 1.1), 1)
        carbs = round(template['carbs'] * random.uniform(0.9, 1.1), 1)
        fat = round(template['fat'] * random.uniform(0.9, 1.1), 1)
        
        return MenuItemData(
            name=name,
            description=template['description'],
            price=price,
            cuisine_type=cuisine,
            category=self._get_category(template['name']),
            dietary_tags=template['dietary'].copy(),
            allergens=template['allergens'].copy(),
            estimated_calories=calories,
            estimated_protein_g=protein,
            estimated_carbs_g=carbs,
            estimated_fat_g=fat
        )
    
    def _get_category(self, name: str) -> str:
        """Determine menu category from item name"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['salad', 'greens', 'caesar']):
            return 'appetizer'
        elif any(word in name_lower for word in ['soup', 'broth', 'bisque']):
            return 'appetizer'
        elif any(word in name_lower for word in ['dessert', 'cake', 'ice cream', 'tart', 'pie']):
            return 'dessert'
        elif any(word in name_lower for word in ['pizza', 'pasta', 'risotto', 'burger', 'sandwich']):
            return 'main'
        else:
            return 'main'
    
    def assign_to_restaurants(self, menu_items: List[MenuItemData]) -> List[Dict]:
        """Assign menu items to restaurants based on cuisine"""
        print("🏪 Assigning menu items to restaurants...")
        
        assigned_items = []
        
        # Group restaurants by cuisine
        restaurants_by_cuisine = {}
        for restaurant in self.restaurants:
            cuisine = restaurant.get('cuisine', 'International')
            if cuisine not in restaurants_by_cuisine:
                restaurants_by_cuisine[cuisine] = []
            restaurants_by_cuisine[cuisine].append(restaurant)
        
        # Assign items to matching cuisine restaurants
        for item in menu_items:
            # Find restaurants with matching cuisine
            matching_restaurants = restaurants_by_cuisine.get(item.cuisine_type, [])
            
            if not matching_restaurants:
                # Fallback to any restaurant if no cuisine match
                matching_restaurants = self.restaurants
            
            # Randomly select a restaurant
            restaurant = random.choice(matching_restaurants)
            
            # Create database record
            record = {
                'id': str(uuid.uuid4()),
                'restaurant_id': restaurant['id'],
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'dietary_tags': item.dietary_tags,
                'allergens': item.allergens,
                'estimated_calories': item.estimated_calories,
                'estimated_protein_g': item.estimated_protein_g,
                'estimated_carbs_g': item.estimated_carbs_g,
                'estimated_fat_g': item.estimated_fat_g,
                'inferred_cuisine_type': item.cuisine_type,
                'inferred_meal_category': item.category,
                'tag_confidence': 0.85,  # High confidence for generated items
                'nutrition_confidence': 0.80,  # High confidence for generated items
                'estimation_method': 'generated-template',
                'portion_size_assumption': 'standard-main'
            }
            
            assigned_items.append(record)
        
        print(f"✅ Assigned {len(assigned_items)} items to restaurants")
        return assigned_items
    
    def load_to_supabase(self, menu_items: List[Dict], batch_size: int = 50):
        """Load menu items to Supabase in batches"""
        print(f"📤 Loading {len(menu_items)} menu items to Supabase...")
        
        total_loaded = 0
        
        for i in range(0, len(menu_items), batch_size):
            batch = menu_items[i:i + batch_size]
            
            try:
                # Generate embeddings for the batch
                embeddings = self._generate_embeddings([f"{item['name']} - {item['description']}" for item in batch])
                
                # Add embeddings to batch
                for j, item in enumerate(batch):
                    item['embedding'] = embeddings[j]
                
                # Insert batch
                result = self.supabase.table('menu_items').insert(batch).execute()
                total_loaded += len(batch)
                
                print(f"   ✅ Loaded batch {i//batch_size + 1}: {len(batch)} items (Total: {total_loaded})")
                
            except Exception as e:
                print(f"   ❌ Error loading batch {i//batch_size + 1}: {e}")
        
        print(f"🎉 Successfully loaded {total_loaded} menu items to Supabase!")
        return total_loaded
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text using sentence transformers"""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            embeddings = model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except ImportError:
            print("⚠️ sentence-transformers not available, using random embeddings")
            return [np.random.rand(384).tolist() for _ in texts]
    
    def validate_loading(self):
        """Validate that items were loaded correctly"""
        print("🧪 Validating loaded data...")
        
        try:
            # Get total count
            total_count = self.supabase.table('menu_items').select('id', count='exact').execute()
            print(f"📊 Total menu items in database: {total_count.count}")
            
            # Get count of items with generated data
            generated_count = self.supabase.table('menu_items').select('id', count='exact').eq('estimation_method', 'generated-template').execute()
            print(f"📊 Generated items: {generated_count.count}")
            
            # Sample some items
            sample_items = self.supabase.table('menu_items').select(
                'name,price,inferred_cuisine_type,estimated_calories,estimated_protein_g'
            ).eq('estimation_method', 'generated-template').limit(5).execute()
            
            print(f"\n🔍 Sample generated items:")
            for item in sample_items.data:
                print(f"   • {item['name']} - ${item['price']} ({item['inferred_cuisine_type']})")
                print(f"     {item['estimated_calories']} cal, {item['estimated_protein_g']}g protein")
            
        except Exception as e:
            print(f"❌ Error validating data: {e}")

def main():
    """Main execution"""
    print("🍽️ Epicure Menu Item Generator")
    print("=" * 50)
    print("This will generate 500 diverse menu items with:")
    print("  🏷️ Realistic names and descriptions")
    print("  💰 Appropriate pricing")
    print("  🥗 Estimated nutrition data")
    print("  🏪 Assignment to existing restaurants")
    print("  🧠 Embeddings for semantic search")
    print()
    
    generator = MenuItemGenerator()
    
    # Generate menu items
    menu_items = generator.generate_menu_items(500)
    
    # Assign to restaurants
    assigned_items = generator.assign_to_restaurants(menu_items)
    
    # Load to Supabase
    loaded_count = generator.load_to_supabase(assigned_items)
    
    # Validate
    generator.validate_loading()
    
    print(f"\n🎉 Menu item generation complete!")
    print(f"📊 Generated and loaded {loaded_count} new menu items")
    print(f"💡 Next step: Run comprehensive_batch_generator.py to add AI-generated tags")

if __name__ == "__main__":
    main()
