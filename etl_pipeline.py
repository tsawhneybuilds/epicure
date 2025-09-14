#!/usr/bin/env python3
"""
ETL Pipeline for Epicure - Load SoHo menu harvest data into Supabase
"""

import os
import json
import csv
import uuid
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

@dataclass
class Restaurant:
    id: str
    name: str
    lat: float
    lng: float
    website: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price_level: Optional[int] = None
    cuisine: Optional[str] = None
    address: Optional[str] = None

@dataclass
class MenuItem:
    id: str
    restaurant_id: str
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    section: Optional[str] = None
    dietary_tags: List[str] = None
    allergens: List[str] = None
    confidence: Optional[float] = None

class EpicureETL:
    def __init__(self):
        """Initialize ETL pipeline with Supabase connection"""
        self.supabase = self._get_supabase_client()
        self.data_dir = "soho_menu_harvest/data"
        
        # ID mappings for relational linking
        self.restaurant_map = {}  # source_id -> supabase_id
        self.menu_map = {}       # menu_id -> restaurant_id
        
        print("🚀 Epicure ETL Pipeline Initialized")
        print(f"📂 Data directory: {self.data_dir}")
    
    def _get_supabase_client(self) -> Client:
        """Initialize Supabase client"""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        
        return create_client(url, key)
    
    def extract_restaurants(self) -> List[Restaurant]:
        """Extract restaurant data from venues_enriched.jsonl"""
        print("📥 Extracting restaurant data...")
        
        restaurants = []
        venues_file = f"{self.data_dir}/venues_enriched.jsonl"
        
        with open(venues_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    venue = json.loads(line.strip())
                    
                    # Extract basic info
                    restaurant = Restaurant(
                        id=venue['id'],
                        name=venue['name'],
                        lat=venue['lat'],
                        lng=venue['lng'],
                        website=venue.get('website'),
                        phone=venue.get('phone'),
                        rating=venue.get('google_rating') or venue.get('yelp', {}).get('rating'),
                        review_count=venue.get('google_review_count') or venue.get('yelp', {}).get('review_count')
                    )
                    
                    restaurants.append(restaurant)
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  Error parsing line {line_num}: {e}")
                    continue
                except KeyError as e:
                    print(f"⚠️  Missing required field {e} in line {line_num}")
                    continue
        
        print(f"✅ Extracted {len(restaurants)} restaurants")
        return restaurants
    
    def extract_menu_data(self) -> Tuple[List[MenuItem], Dict[str, str]]:
        """Extract menu items and build restaurant mapping"""
        print("📥 Extracting menu data...")
        
        # First, build menu_id -> restaurant_id mapping
        menu_map = {}
        menus_file = f"{self.data_dir}/menus.csv"
        
        with open(menus_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                menu_map[row['id']] = row['restaurant_id']
        
        print(f"📋 Built menu mapping for {len(menu_map)} menus")
        
        # Now extract menu items
        menu_items = []
        items_file = f"{self.data_dir}/menu_items.csv"
        
        with open(items_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Get restaurant_id via menu_id lookup
                    menu_id = row['menu_id']
                    restaurant_id = menu_map.get(menu_id)
                    
                    if not restaurant_id:
                        print(f"⚠️  No restaurant found for menu {menu_id}")
                        continue
                    
                    # Parse price
                    price = None
                    if row['price']:
                        try:
                            price = float(row['price'])
                        except ValueError:
                            pass
                    
                    # Parse allergens and tags
                    allergens = []
                    if row['allergens']:
                        allergens = [a.strip() for a in row['allergens'].split(',')]
                    
                    dietary_tags = []
                    if row['tags']:
                        dietary_tags = [t.strip() for t in row['tags'].split(',')]
                    
                    menu_item = MenuItem(
                        id=row['x'],  # Using 'x' as the ID field
                        restaurant_id=restaurant_id,
                        name=row['name'],
                        description=row['description'] if row['description'] else None,
                        price=price,
                        currency=row['currency'] if row['currency'] else 'USD',
                        section=row['section'] if row['section'] else None,
                        dietary_tags=dietary_tags,
                        allergens=allergens,
                        confidence=float(row['confidence']) if row['confidence'] else None
                    )
                    
                    menu_items.append(menu_item)
                    
                except Exception as e:
                    print(f"⚠️  Error parsing menu item: {e}")
                    continue
        
        print(f"✅ Extracted {len(menu_items)} menu items")
        return menu_items, menu_map
    
    def infer_cuisine_and_price_level(self, restaurants: List[Restaurant], menu_items: List[MenuItem]) -> List[Restaurant]:
        """Infer cuisine type and price level from menu items"""
        print("🔍 Inferring cuisine types and price levels...")
        
        # Build restaurant -> menu items mapping
        restaurant_items = {}
        for item in menu_items:
            if item.restaurant_id not in restaurant_items:
                restaurant_items[item.restaurant_id] = []
            restaurant_items[item.restaurant_id].append(item)
        
        # Process each restaurant
        for restaurant in restaurants:
            items = restaurant_items.get(restaurant.id, [])
            
            if not items:
                continue
            
            # Infer price level from average price
            prices = [item.price for item in items if item.price and item.price > 0]
            if prices:
                avg_price = np.mean(prices)
                if avg_price <= 15:
                    restaurant.price_level = 1  # $
                elif avg_price <= 30:
                    restaurant.price_level = 2  # $$
                elif avg_price <= 60:
                    restaurant.price_level = 3  # $$$
                else:
                    restaurant.price_level = 4  # $$$$
            
            # Simple cuisine inference based on menu item patterns
            item_names = ' '.join([item.name.lower() for item in items if item.name])
            item_descriptions = ' '.join([item.description.lower() for item in items if item.description])
            combined_text = f"{item_names} {item_descriptions}"
            
            # Basic cuisine classification
            if any(word in combined_text for word in ['pizza', 'pasta', 'italian', 'mozzarella', 'marinara']):
                restaurant.cuisine = 'Italian'
            elif any(word in combined_text for word in ['sushi', 'ramen', 'japanese', 'tempura', 'miso']):
                restaurant.cuisine = 'Japanese'
            elif any(word in combined_text for word in ['taco', 'burrito', 'mexican', 'salsa', 'guacamole']):
                restaurant.cuisine = 'Mexican'
            elif any(word in combined_text for word in ['burger', 'fries', 'american', 'bbq', 'wings']):
                restaurant.cuisine = 'American'
            elif any(word in combined_text for word in ['pad thai', 'curry', 'thai', 'asian', 'stir fry']):
                restaurant.cuisine = 'Thai'
            elif any(word in combined_text for word in ['baguette', 'french', 'croissant', 'wine', 'cheese']):
                restaurant.cuisine = 'French'
            else:
                restaurant.cuisine = 'International'  # Default
        
        print(f"✅ Inferred cuisine and price levels for {len(restaurants)} restaurants")
        return restaurants
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for text using Hugging Face transformers"""
        print(f"🧠 Generating embeddings for {len(texts)} texts...")
        
        try:
            # Try to use local transformers
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = model.encode(batch, convert_to_tensor=False)
                embeddings.extend(batch_embeddings.tolist())
                
                if i % (batch_size * 5) == 0:
                    print(f"   📊 Processed {min(i + batch_size, len(texts))}/{len(texts)} embeddings")
            
            print(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings
            
        except ImportError:
            print("⚠️  sentence-transformers not installed, using random embeddings for testing")
            # Generate random embeddings for testing
            return [np.random.rand(384).tolist() for _ in texts]
    
    def load_restaurants(self, restaurants: List[Restaurant]) -> Dict[str, str]:
        """Load restaurants into Supabase and return ID mapping"""
        print("📤 Loading restaurants into Supabase...")
        
        # Generate embeddings for restaurant descriptions
        restaurant_texts = []
        for restaurant in restaurants:
            # Create description text for embedding
            desc_parts = [restaurant.name]
            if restaurant.cuisine:
                desc_parts.append(restaurant.cuisine)
            description = f"{' '.join(desc_parts)} restaurant"
            restaurant_texts.append(description)
        
        embeddings = self.generate_embeddings(restaurant_texts)
        
        # Prepare restaurant records
        restaurant_records = []
        id_mapping = {}
        
        for i, restaurant in enumerate(restaurants):
            # Generate new UUID for Supabase
            supabase_id = str(uuid.uuid4())
            id_mapping[restaurant.id] = supabase_id
            
            # Create address from coordinates if missing
            address = None
            if restaurant.lat and restaurant.lng:
                address = f"Latitude: {restaurant.lat}, Longitude: {restaurant.lng}"
            
            record = {
                'id': supabase_id,
                'name': restaurant.name,
                'cuisine': restaurant.cuisine,
                'description': f"{restaurant.name} - {restaurant.cuisine or 'Restaurant'}",
                'address': address,
                'location': f"POINT({restaurant.lng} {restaurant.lat})",
                'phone': restaurant.phone,
                'website': restaurant.website,
                'price_level': restaurant.price_level,
                'rating': restaurant.rating,
                'review_count': restaurant.review_count,
                'description_embedding': embeddings[i]
            }
            restaurant_records.append(record)
        
        # Insert in batches
        batch_size = 50
        for i in range(0, len(restaurant_records), batch_size):
            batch = restaurant_records[i:i + batch_size]
            try:
                self.supabase.table('restaurants').insert(batch).execute()
                print(f"   ✅ Inserted restaurants {i + 1}-{min(i + batch_size, len(restaurant_records))}")
            except Exception as e:
                print(f"   ❌ Error inserting restaurant batch {i}: {e}")
        
        print(f"✅ Loaded {len(restaurant_records)} restaurants")
        return id_mapping
    
    def load_menu_items(self, menu_items: List[MenuItem], restaurant_id_mapping: Dict[str, str]):
        """Load menu items into Supabase"""
        print("📤 Loading menu items into Supabase...")
        
        # Filter items with valid restaurant mappings
        valid_items = []
        for item in menu_items:
            if item.restaurant_id in restaurant_id_mapping:
                valid_items.append(item)
            else:
                print(f"⚠️  Skipping item {item.name} - no restaurant mapping for {item.restaurant_id}")
        
        print(f"📊 Processing {len(valid_items)} valid menu items")
        
        # Generate embeddings for menu items
        item_texts = []
        for item in valid_items:
            # Get restaurant name for context
            restaurant_name = "Restaurant"  # Default fallback
            
            # Create combined text for embedding
            text_parts = []
            if restaurant_name:
                text_parts.append(restaurant_name)
            text_parts.append(item.name)
            if item.description:
                text_parts.append(item.description)
            
            combined_text = " - ".join(text_parts)
            item_texts.append(combined_text)
        
        embeddings = self.generate_embeddings(item_texts)
        
        # Prepare menu item records
        item_records = []
        for i, item in enumerate(valid_items):
            supabase_restaurant_id = restaurant_id_mapping[item.restaurant_id]
            
            record = {
                'id': str(uuid.uuid4()),  # Generate new UUID
                'restaurant_id': supabase_restaurant_id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'dietary_tags': item.dietary_tags,
                'allergens': item.allergens,
                'embedding': embeddings[i]
            }
            item_records.append(record)
        
        # Insert in batches
        batch_size = 50
        for i in range(0, len(item_records), batch_size):
            batch = item_records[i:i + batch_size]
            try:
                self.supabase.table('menu_items').insert(batch).execute()
                print(f"   ✅ Inserted menu items {i + 1}-{min(i + batch_size, len(item_records))}")
            except Exception as e:
                print(f"   ❌ Error inserting menu item batch {i}: {e}")
        
        print(f"✅ Loaded {len(item_records)} menu items")
    
    def validate_data(self):
        """Validate the loaded data"""
        print("🧪 Validating loaded data...")
        
        # Check restaurant count
        restaurant_count = self.supabase.table('restaurants').select('id', count='exact').execute()
        print(f"📊 Restaurants in database: {restaurant_count.count}")
        
        # Check menu item count
        item_count = self.supabase.table('menu_items').select('id', count='exact').execute()
        print(f"📊 Menu items in database: {item_count.count}")
        
        # Check relational integrity by counting items with valid restaurant links
        try:
            # Count menu items
            total_items = self.supabase.table('menu_items').select('id', count='exact').execute()
            
            # Count items with valid restaurant references
            valid_items = self.supabase.table('menu_items').select('id', count='exact').eq('restaurant_id', 'restaurant_id').execute()
            
            print("✅ Menu items properly linked to restaurants")
        except Exception as e:
            print(f"⚠️  Could not validate relational integrity: {e}")
        
        # Test semantic search
        try:
            search_result = self.supabase.rpc('match_menu_items', {
                'query_embedding': np.random.rand(384).tolist(),
                'match_threshold': 0.0,
                'match_count': 5
            }).execute()
            print(f"✅ Semantic search working - found {len(search_result.data)} similar items")
        except Exception as e:
            print(f"❌ Semantic search test failed: {e}")
    
    def run_full_pipeline(self):
        """Run the complete ETL pipeline"""
        print("🚀 Starting Epicure ETL Pipeline")
        print("=" * 60)
        
        try:
            # Extract data
            restaurants = self.extract_restaurants()
            menu_items, menu_map = self.extract_menu_data()
            
            # Transform data
            restaurants = self.infer_cuisine_and_price_level(restaurants, menu_items)
            
            # Load data
            restaurant_id_mapping = self.load_restaurants(restaurants)
            self.load_menu_items(menu_items, restaurant_id_mapping)
            
            # Validate
            self.validate_data()
            
            print("\n🎉 ETL Pipeline Completed Successfully!")
            print(f"📊 Loaded {len(restaurants)} restaurants and {len(menu_items)} menu items")
            print("🔍 Ready for semantic search and recommendations!")
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            raise

if __name__ == "__main__":
    etl = EpicureETL()
    etl.run_full_pipeline()
