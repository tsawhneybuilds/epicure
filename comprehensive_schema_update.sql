-- Comprehensive Schema Update: Add Tags + Nutrition + Indexes
-- Run this in Supabase SQL Editor

-- ===================================
-- 1. ADD TAG COLUMNS
-- ===================================

ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_dietary_tags TEXT[];
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_cuisine_type VARCHAR(50);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_health_tags TEXT[];
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_spice_level VARCHAR(20);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_meal_category VARCHAR(30);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_cooking_methods TEXT[];
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS inferred_allergens TEXT[];
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS tag_confidence NUMERIC(3,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS tags_generated_at TIMESTAMPTZ;

-- ===================================
-- 2. ADD NUTRITION COLUMNS
-- ===================================

-- Macronutrients
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS estimated_calories INTEGER;
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS estimated_protein_g NUMERIC(5,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS estimated_carbs_g NUMERIC(5,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS estimated_fat_g NUMERIC(5,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS estimated_fiber_g NUMERIC(4,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS estimated_sugar_g NUMERIC(4,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS estimated_sodium_mg INTEGER;

-- Nutritional ratios
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS calories_per_100g INTEGER;
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS protein_ratio NUMERIC(3,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS carb_ratio NUMERIC(3,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS fat_ratio NUMERIC(3,2);

-- Nutrition metadata
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS nutrition_confidence NUMERIC(3,2);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS estimation_method VARCHAR(30);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS portion_size_assumption VARCHAR(50);
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS nutrition_generated_at TIMESTAMPTZ;

-- ===================================
-- 3. CREATE INDEXES FOR EFFICIENT QUERYING
-- ===================================

-- Tag-based indexes
CREATE INDEX IF NOT EXISTS idx_menu_items_dietary_tags ON menu_items USING GIN (inferred_dietary_tags);
CREATE INDEX IF NOT EXISTS idx_menu_items_cuisine_type ON menu_items (inferred_cuisine_type);
CREATE INDEX IF NOT EXISTS idx_menu_items_health_tags ON menu_items USING GIN (inferred_health_tags);
CREATE INDEX IF NOT EXISTS idx_menu_items_spice_level ON menu_items (inferred_spice_level);
CREATE INDEX IF NOT EXISTS idx_menu_items_allergens ON menu_items USING GIN (inferred_allergens);

-- Nutrition-based indexes
CREATE INDEX IF NOT EXISTS idx_menu_items_calories ON menu_items (estimated_calories);
CREATE INDEX IF NOT EXISTS idx_menu_items_protein ON menu_items (estimated_protein_g);
CREATE INDEX IF NOT EXISTS idx_menu_items_carbs ON menu_items (estimated_carbs_g);
CREATE INDEX IF NOT EXISTS idx_menu_items_fat ON menu_items (estimated_fat_g);
CREATE INDEX IF NOT EXISTS idx_menu_items_fiber ON menu_items (estimated_fiber_g);
CREATE INDEX IF NOT EXISTS idx_menu_items_sodium ON menu_items (estimated_sodium_mg);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_menu_items_diet_calories ON menu_items (inferred_dietary_tags, estimated_calories);
CREATE INDEX IF NOT EXISTS idx_menu_items_protein_ratio ON menu_items (protein_ratio) WHERE protein_ratio IS NOT NULL;

-- ===================================
-- 4. ADVANCED SEARCH FUNCTIONS
-- ===================================

-- Search by nutritional requirements
CREATE OR REPLACE FUNCTION search_by_nutrition(
  max_calories INTEGER DEFAULT NULL,
  min_protein_g NUMERIC DEFAULT NULL,
  max_carbs_g NUMERIC DEFAULT NULL,
  max_sodium_mg INTEGER DEFAULT NULL,
  dietary_requirements TEXT[] DEFAULT NULL,
  limit_count INT DEFAULT 20
)
RETURNS TABLE (
  id uuid,
  name text,
  description text,
  restaurant_id uuid,
  price numeric,
  estimated_calories integer,
  estimated_protein_g numeric,
  estimated_carbs_g numeric,
  estimated_fat_g numeric,
  inferred_dietary_tags text[],
  nutrition_score numeric
)
LANGUAGE sql stable
AS $$
  WITH nutrition_matches AS (
    SELECT 
      mi.*,
      (
        CASE WHEN max_calories IS NULL THEN 1.0 
             WHEN mi.estimated_calories <= max_calories THEN 1.0 
             ELSE 0.0 
        END +
        CASE WHEN min_protein_g IS NULL THEN 1.0 
             WHEN mi.estimated_protein_g >= min_protein_g THEN 1.0 
             ELSE 0.0 
        END +
        CASE WHEN max_carbs_g IS NULL THEN 1.0 
             WHEN mi.estimated_carbs_g <= max_carbs_g THEN 1.0 
             ELSE 0.0 
        END +
        CASE WHEN max_sodium_mg IS NULL THEN 1.0 
             WHEN mi.estimated_sodium_mg <= max_sodium_mg THEN 1.0 
             ELSE 0.0 
        END +
        CASE WHEN dietary_requirements IS NULL THEN 1.0 
             WHEN mi.inferred_dietary_tags && dietary_requirements THEN 1.0 
             ELSE 0.0 
        END
      ) / 5.0 AS nutrition_score
    FROM menu_items mi
    WHERE 
      (max_calories IS NULL OR mi.estimated_calories <= max_calories)
      AND (min_protein_g IS NULL OR mi.estimated_protein_g >= min_protein_g)
      AND (max_carbs_g IS NULL OR mi.estimated_carbs_g <= max_carbs_g)
      AND (max_sodium_mg IS NULL OR mi.estimated_sodium_mg <= max_sodium_mg)
      AND (dietary_requirements IS NULL OR mi.inferred_dietary_tags && dietary_requirements)
      AND mi.estimated_calories IS NOT NULL
  )
  SELECT 
    id, name, description, restaurant_id, price,
    estimated_calories, estimated_protein_g, estimated_carbs_g, estimated_fat_g,
    inferred_dietary_tags, nutrition_score
  FROM nutrition_matches
  WHERE nutrition_score > 0.6
  ORDER BY nutrition_score DESC, estimated_calories ASC
  LIMIT limit_count;
$$;

-- Combined semantic + tag + nutrition search
CREATE OR REPLACE FUNCTION hybrid_search_with_nutrition(
  query_embedding vector(384),
  max_calories INTEGER DEFAULT NULL,
  dietary_requirements TEXT[] DEFAULT NULL,
  cuisine_preference TEXT DEFAULT NULL,
  semantic_threshold FLOAT DEFAULT 0.3,
  limit_count INT DEFAULT 20
)
RETURNS TABLE (
  id uuid,
  name text,
  description text,
  restaurant_id uuid,
  estimated_calories integer,
  estimated_protein_g numeric,
  inferred_dietary_tags text[],
  inferred_cuisine_type text,
  semantic_similarity float,
  nutrition_match_score float,
  hybrid_score float
)
LANGUAGE sql stable
AS $$
  WITH semantic_matches AS (
    SELECT 
      mi.*,
      1 - (mi.embedding <=> query_embedding) as semantic_similarity
    FROM menu_items mi
    WHERE 1 - (mi.embedding <=> query_embedding) > semantic_threshold
  ),
  nutrition_filtered AS (
    SELECT 
      sm.*,
      (
        CASE WHEN max_calories IS NULL THEN 1.0 
             WHEN sm.estimated_calories <= max_calories THEN 1.0 
             ELSE 0.5 
        END +
        CASE WHEN dietary_requirements IS NULL THEN 1.0 
             WHEN sm.inferred_dietary_tags && dietary_requirements THEN 1.0 
             ELSE 0.0 
        END +
        CASE WHEN cuisine_preference IS NULL THEN 0.8 
             WHEN sm.inferred_cuisine_type = cuisine_preference THEN 1.0 
             ELSE 0.3 
        END
      ) / 3.0 AS nutrition_match_score,
      -- Hybrid score: 60% semantic, 40% nutrition/tags
      (sm.semantic_similarity * 0.6) + 
      ((
        CASE WHEN max_calories IS NULL THEN 1.0 
             WHEN sm.estimated_calories <= max_calories THEN 1.0 
             ELSE 0.5 
        END +
        CASE WHEN dietary_requirements IS NULL THEN 1.0 
             WHEN sm.inferred_dietary_tags && dietary_requirements THEN 1.0 
             ELSE 0.0 
        END +
        CASE WHEN cuisine_preference IS NULL THEN 0.8 
             WHEN sm.inferred_cuisine_type = cuisine_preference THEN 1.0 
             ELSE 0.3 
        END
      ) / 3.0 * 0.4) AS hybrid_score
    FROM semantic_matches sm
  )
  SELECT 
    id, name, description, restaurant_id,
    estimated_calories, estimated_protein_g, inferred_dietary_tags, inferred_cuisine_type,
    semantic_similarity, nutrition_match_score, hybrid_score
  FROM nutrition_filtered
  ORDER BY hybrid_score DESC
  LIMIT limit_count;
$$;

-- ===================================
-- 5. UTILITY FUNCTIONS
-- ===================================

-- Get nutrition stats for the database
CREATE OR REPLACE FUNCTION get_nutrition_coverage_stats()
RETURNS TABLE (
  total_items bigint,
  items_with_calories bigint,
  items_with_protein bigint,
  items_with_tags bigint,
  avg_calories numeric,
  avg_protein numeric,
  coverage_percentage numeric
)
LANGUAGE sql stable
AS $$
  SELECT 
    COUNT(*) as total_items,
    COUNT(estimated_calories) as items_with_calories,
    COUNT(estimated_protein_g) as items_with_protein,
    COUNT(inferred_dietary_tags) as items_with_tags,
    ROUND(AVG(estimated_calories), 0) as avg_calories,
    ROUND(AVG(estimated_protein_g), 1) as avg_protein,
    ROUND(COUNT(estimated_calories)::numeric / COUNT(*) * 100, 1) as coverage_percentage
  FROM menu_items;
$$;

-- Find high protein options
CREATE OR REPLACE FUNCTION find_high_protein_options(
  min_protein_g NUMERIC DEFAULT 25,
  max_calories INTEGER DEFAULT 600,
  limit_count INT DEFAULT 15
)
RETURNS TABLE (
  id uuid,
  name text,
  restaurant_id uuid,
  estimated_calories integer,
  estimated_protein_g numeric,
  protein_ratio numeric,
  inferred_dietary_tags text[]
)
LANGUAGE sql stable
AS $$
  SELECT 
    id, name, restaurant_id,
    estimated_calories, estimated_protein_g, protein_ratio,
    inferred_dietary_tags
  FROM menu_items
  WHERE 
    estimated_protein_g >= min_protein_g
    AND (max_calories IS NULL OR estimated_calories <= max_calories)
    AND estimated_calories IS NOT NULL
  ORDER BY protein_ratio DESC, estimated_protein_g DESC
  LIMIT limit_count;
$$;
