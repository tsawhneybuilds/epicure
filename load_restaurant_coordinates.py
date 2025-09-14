#!/usr/bin/env python3
"""
Load restaurant coordinates from venues_enriched.jsonl into Supabase
"""

import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Get Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Supabase credentials not found in environment variables")
        return None
    
    return create_client(url, key)

def load_restaurant_data():
    """Load restaurant data with coordinates from venues_enriched.jsonl"""
    supabase = get_supabase_client()
    if not supabase:
        return
    
    # Read the venues_enriched.jsonl file
    venues_file = "soho_menu_harvest/data/venues_enriched.jsonl"
    
    if not os.path.exists(venues_file):
        print(f"❌ File not found: {venues_file}")
        return
    
    print(f"📖 Reading restaurant data from {venues_file}")
    
    restaurants_to_insert = []
    
    with open(venues_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                venue = json.loads(line.strip())
                
                # Extract restaurant data
                restaurant_data = {
                    "id": venue["id"],
                    "name": venue["name"],
                    "latitude": venue.get("lat"),
                    "longitude": venue.get("lng"),
                    "website": venue.get("website"),
                    "phone": venue.get("phone"),
                    "address": venue.get("address", ""),
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
                
                # Only add if we have coordinates
                if restaurant_data["latitude"] and restaurant_data["longitude"]:
                    restaurants_to_insert.append(restaurant_data)
                
                # Process in batches of 100
                if len(restaurants_to_insert) >= 100:
                    print(f"📤 Inserting batch of {len(restaurants_to_insert)} restaurants...")
                    try:
                        result = supabase.table("restaurants").upsert(restaurants_to_insert).execute()
                        print(f"✅ Inserted {len(result.data)} restaurants")
                    except Exception as e:
                        print(f"❌ Error inserting batch: {e}")
                    
                    restaurants_to_insert = []
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON decode error on line {line_num}: {e}")
                continue
            except Exception as e:
                print(f"⚠️  Error processing line {line_num}: {e}")
                continue
    
    # Insert remaining restaurants
    if restaurants_to_insert:
        print(f"📤 Inserting final batch of {len(restaurants_to_insert)} restaurants...")
        try:
            result = supabase.table("restaurants").upsert(restaurants_to_insert).execute()
            print(f"✅ Inserted {len(result.data)} restaurants")
        except Exception as e:
            print(f"❌ Error inserting final batch: {e}")
    
    print("�� Restaurant data loading complete!")

if __name__ == "__main__":
    load_restaurant_data()
