-- Run this in Supabase SQL Editor to enable semantic search
-- This adds the missing helper functions for semantic search

-- Function for advanced semantic search with restaurant context
CREATE OR REPLACE FUNCTION semantic_search_with_restaurant(
  query_embedding vector(384),
  cuisine_filter text DEFAULT NULL,
  max_price numeric DEFAULT NULL,
  match_threshold float DEFAULT 0.3,
  match_count int DEFAULT 20
)
RETURNS TABLE (
  item_id uuid,
  item_name text,
  item_description text,
  item_price numeric,
  restaurant_id uuid,
  restaurant_name text,
  restaurant_cuisine text,
  similarity float
)
LANGUAGE sql stable
AS $$
  SELECT
    mi.id as item_id,
    mi.name as item_name,
    mi.description as item_description,
    mi.price as item_price,
    r.id as restaurant_id,
    r.name as restaurant_name,
    r.cuisine as restaurant_cuisine,
    1 - (mi.embedding <=> query_embedding) as similarity
  FROM menu_items mi
  JOIN restaurants r ON mi.restaurant_id = r.id
  WHERE 
    1 - (mi.embedding <=> query_embedding) > match_threshold
    AND (cuisine_filter IS NULL OR r.cuisine ILIKE '%' || cuisine_filter || '%')
    AND (max_price IS NULL OR mi.price IS NULL OR mi.price <= max_price)
  ORDER BY mi.embedding <=> query_embedding
  LIMIT match_count;
$$;

-- Function to get restaurant statistics
CREATE OR REPLACE FUNCTION get_restaurant_stats()
RETURNS TABLE (
  total_restaurants bigint,
  total_menu_items bigint,
  avg_items_per_restaurant numeric,
  restaurants_with_items bigint
)
LANGUAGE sql stable
AS $$
  SELECT 
    (SELECT COUNT(*) FROM restaurants) as total_restaurants,
    (SELECT COUNT(*) FROM menu_items) as total_menu_items,
    (SELECT ROUND(COUNT(*)::numeric / NULLIF((SELECT COUNT(*) FROM restaurants), 0), 2) FROM menu_items) as avg_items_per_restaurant,
    (SELECT COUNT(DISTINCT restaurant_id) FROM menu_items) as restaurants_with_items;
$$;

-- Function to search restaurants by cuisine and location
CREATE OR REPLACE FUNCTION search_restaurants_by_cuisine_location(
  cuisine_filter text DEFAULT NULL,
  user_lat float DEFAULT NULL,
  user_lng float DEFAULT NULL,
  max_distance_km float DEFAULT 5.0,
  limit_count int DEFAULT 20
)
RETURNS TABLE (
  id uuid,
  name text,
  cuisine text,
  distance_km float,
  item_count bigint
)
LANGUAGE sql stable
AS $$
  SELECT 
    r.id,
    r.name,
    r.cuisine,
    CASE 
      WHEN user_lat IS NOT NULL AND user_lng IS NOT NULL THEN
        ST_Distance(
          r.location,
          ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326)
        ) / 1000.0
      ELSE NULL
    END as distance_km,
    COUNT(mi.id) as item_count
  FROM restaurants r
  LEFT JOIN menu_items mi ON r.id = mi.restaurant_id
  WHERE 
    (cuisine_filter IS NULL OR r.cuisine ILIKE '%' || cuisine_filter || '%')
    AND (
      user_lat IS NULL OR user_lng IS NULL OR
      ST_DWithin(
        r.location,
        ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326),
        max_distance_km * 1000
      )
    )
  GROUP BY r.id, r.name, r.cuisine, r.location
  ORDER BY 
    CASE 
      WHEN user_lat IS NOT NULL AND user_lng IS NOT NULL THEN
        ST_Distance(r.location, ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326))
      ELSE 0
    END
  LIMIT limit_count;
$$;

-- Function to check for orphaned menu items
CREATE OR REPLACE FUNCTION check_orphaned_menu_items()
RETURNS TABLE (
  item_id uuid,
  item_name text,
  restaurant_id uuid
)
LANGUAGE sql stable
AS $$
  SELECT 
    mi.id as item_id,
    mi.name as item_name,
    mi.restaurant_id
  FROM menu_items mi
  LEFT JOIN restaurants r ON mi.restaurant_id = r.id
  WHERE r.id IS NULL;
$$;
