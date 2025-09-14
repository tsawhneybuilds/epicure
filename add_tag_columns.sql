-- Add tag storage columns to menu_items table
-- Run this in Supabase SQL Editor first

ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_dietary_tags TEXT[];
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_cuisine_type VARCHAR(50);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_health_tags TEXT[];
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_spice_level VARCHAR(20);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_meal_category VARCHAR(30);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_cooking_methods TEXT[];
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_allergens TEXT[];
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS tag_confidence NUMERIC(3,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS tags_generated_at TIMESTAMPTZ;

-- Create index for tag-based queries
CREATE INDEX IF NOT EXISTS idx_menu_items_dietary_tags ON menu_items USING GIN (inferred_dietary_tags);
CREATE INDEX IF NOT EXISTS idx_menu_items_cuisine_type ON menu_items (inferred_cuisine_type);
CREATE INDEX IF NOT EXISTS idx_menu_items_health_tags ON menu_items USING GIN (inferred_health_tags);
CREATE INDEX IF NOT EXISTS idx_menu_items_spice_level ON menu_items (inferred_spice_level);

-- Create function to search by tags
CREATE OR REPLACE FUNCTION search_by_tags(
  dietary_requirements TEXT[] DEFAULT NULL,
  cuisine_preference TEXT DEFAULT NULL,
  health_goals TEXT[] DEFAULT NULL,
  max_spice_level TEXT DEFAULT NULL,
  limit_count INT DEFAULT 20
)
RETURNS TABLE (
  id uuid,
  name text,
  description text,
  restaurant_id uuid,
  price numeric,
  inferred_dietary_tags text[],
  inferred_cuisine_type text,
  inferred_health_tags text[],
  tag_match_score numeric
)
LANGUAGE sql stable
AS $$
  WITH tag_matches AS (
    SELECT 
      mi.*,
      (
        CASE 
          WHEN dietary_requirements IS NULL THEN 1.0
          ELSE (
            SELECT COUNT(*)::float / GREATEST(array_length(dietary_requirements, 1), 1)
            FROM unnest(dietary_requirements) AS req
            WHERE req = ANY(mi.inferred_dietary_tags)
          )
        END +
        CASE 
          WHEN cuisine_preference IS NULL THEN 0.5
          WHEN mi.inferred_cuisine_type = cuisine_preference THEN 1.0
          ELSE 0.0
        END +
        CASE 
          WHEN health_goals IS NULL THEN 0.5
          ELSE (
            SELECT COUNT(*)::float / GREATEST(array_length(health_goals, 1), 1) * 0.5
            FROM unnest(health_goals) AS goal
            WHERE goal = ANY(mi.inferred_health_tags)
          )
        END
      ) AS tag_match_score
    FROM menu_items mi
    WHERE 
      (dietary_requirements IS NULL OR mi.inferred_dietary_tags && dietary_requirements)
      AND (cuisine_preference IS NULL OR mi.inferred_cuisine_type = cuisine_preference)
      AND (max_spice_level IS NULL OR 
           (max_spice_level = 'hot') OR
           (max_spice_level = 'medium' AND mi.inferred_spice_level IN ('mild', 'medium')) OR
           (max_spice_level = 'mild' AND mi.inferred_spice_level = 'mild'))
  )
  SELECT 
    id, name, description, restaurant_id, price,
    inferred_dietary_tags, inferred_cuisine_type, inferred_health_tags,
    tag_match_score
  FROM tag_matches
  ORDER BY tag_match_score DESC
  LIMIT limit_count;
$$;
