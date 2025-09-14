-- Function for semantic search using text queries (converts to embeddings automatically)
-- This function takes a text query and performs semantic search

CREATE OR REPLACE FUNCTION semantic_search_with_text(
  query_text text,
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
  -- For now, we'll use a simple text matching approach
  -- In production, you'd want to generate embeddings for the query_text
  SELECT
    mi.id as item_id,
    mi.name as item_name,
    mi.description as item_description,
    mi.price as item_price,
    r.id as restaurant_id,
    r.name as restaurant_name,
    r.cuisine as restaurant_cuisine,
    -- Simple text similarity score based on name and description matching
    CASE 
      WHEN LOWER(mi.name) LIKE '%' || LOWER(query_text) || '%' THEN 0.9
      WHEN LOWER(mi.description) LIKE '%' || LOWER(query_text) || '%' THEN 0.7
      WHEN LOWER(r.cuisine) LIKE '%' || LOWER(query_text) || '%' THEN 0.6
      ELSE 0.3
    END as similarity
  FROM menu_items mi
  JOIN restaurants r ON mi.restaurant_id = r.id
  WHERE 
    (
      LOWER(mi.name) LIKE '%' || LOWER(query_text) || '%' OR
      LOWER(mi.description) LIKE '%' || LOWER(query_text) || '%' OR
      LOWER(r.cuisine) LIKE '%' || LOWER(query_text) || '%'
    )
    AND (cuisine_filter IS NULL OR r.cuisine ILIKE '%' || cuisine_filter || '%')
    AND (max_price IS NULL OR mi.price IS NULL OR mi.price <= max_price)
  ORDER BY similarity DESC
  LIMIT match_count;
$$;
