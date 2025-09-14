-- Supabase Setup Script for Epicure
-- Run this in your Supabase SQL Editor or via psql

-- ===================================
-- 1. ENABLE EXTENSIONS
-- ===================================

-- Enable vector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable PostGIS for geographic queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- ===================================
-- 2. CORE SCHEMA
-- ===================================

-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    apple_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Profiles (Canonical Fields)
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    age INTEGER,
    height_cm INTEGER,
    weight_kg NUMERIC(5,2),
    gender VARCHAR(20),
    activity_level VARCHAR(20),
    goals TEXT[],
    budget_usd_per_meal NUMERIC(6,2),
    max_walk_time_minutes INTEGER,
    dietary_restrictions TEXT[],
    allergies TEXT[],
    profile_extensions JSONB DEFAULT '{}',
    schema_version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add-only Schema Registry
CREATE TABLE profile_schema_fields (
    key VARCHAR(100) PRIMARY KEY,
    type VARCHAR(20) NOT NULL, -- 'string', 'number', 'boolean', 'array'
    source VARCHAR(20) DEFAULT 'ai', -- 'ai', 'user', 'health'
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW()
);

-- Extension Value Provenance
CREATE TABLE profile_extension_meta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    key VARCHAR(100) REFERENCES profile_schema_fields(key),
    value_json JSONB,
    confidence NUMERIC(3,2), -- 0.00 to 1.00
    source_type VARCHAR(20), -- 'chat', 'voice', 'health', 'manual'
    source_id VARCHAR(100), -- message_id, health_sync_id, etc.
    status VARCHAR(20) DEFAULT 'proposed', -- 'proposed', 'active', 'rejected'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Restaurants
CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    cuisine VARCHAR(100),
    description TEXT,
    address TEXT,
    location GEOGRAPHY(POINT, 4326),
    phone VARCHAR(20),
    website VARCHAR(255),
    price_level INTEGER, -- 1-4 ($, $$, $$$, $$$$)
    rating NUMERIC(2,1),
    review_count INTEGER,
    image_url TEXT,
    open_hours JSONB,
    delivery_providers JSONB, -- DoorDash, Uber Eats links
    description_embedding VECTOR(384), -- For restaurant-level search
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Menu Items (for detailed nutritional data)
CREATE TABLE menu_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID REFERENCES restaurants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(6,2),
    calories INTEGER,
    protein_g NUMERIC(5,2),
    carbs_g NUMERIC(5,2),
    fat_g NUMERIC(5,2),
    fiber_g NUMERIC(5,2),
    sodium_mg INTEGER,
    sugar_g NUMERIC(5,2),
    dietary_tags TEXT[], -- ['vegan', 'gluten-free', 'high-protein']
    allergens TEXT[],
    image_url TEXT,
    embedding VECTOR(384), -- For semantic search
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Interactions
CREATE TABLE user_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    restaurant_id UUID REFERENCES restaurants(id),
    menu_item_id UUID REFERENCES menu_items(id),
    interaction_type VARCHAR(20), -- 'like', 'dislike', 'view', 'order'
    context JSONB, -- Search parameters, position in results, etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat History
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    role VARCHAR(20), -- 'user', 'assistant'
    content TEXT,
    metadata JSONB, -- Extracted preferences, confidence scores
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Health Data Connections
CREATE TABLE health_connections (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    source VARCHAR(20), -- 'apple_health', 'google_fit'
    scopes TEXT[],
    sync_token VARCHAR(255),
    last_sync_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'revoked'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===================================
-- 3. INDEXES
-- ===================================

-- Vector indexes for fast similarity search
CREATE INDEX ON menu_items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON restaurants USING ivfflat (description_embedding vector_cosine_ops) WITH (lists = 100);

-- Geographic indexes
CREATE INDEX ON restaurants USING GIST (location);

-- Regular indexes for common queries
CREATE INDEX ON user_interactions (user_id, created_at);
CREATE INDEX ON chat_messages (user_id, created_at);
CREATE INDEX ON restaurants (cuisine, price_level);
CREATE INDEX ON menu_items (restaurant_id);
CREATE INDEX ON profile_extension_meta (user_id, key);

-- ===================================
-- 4. ROW LEVEL SECURITY (RLS)
-- ===================================

-- Enable RLS on user-related tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_extension_meta ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_connections ENABLE ROW LEVEL SECURITY;

-- Create policies (users can only access their own data)
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own extension meta" ON profile_extension_meta
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own interactions" ON user_interactions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own chat messages" ON chat_messages
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own health connections" ON health_connections
    FOR ALL USING (auth.uid() = user_id);

-- Restaurants and menu items are public (read-only for users)
CREATE POLICY "Anyone can view restaurants" ON restaurants
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view menu items" ON menu_items
    FOR SELECT USING (true);

-- ===================================
-- 5. VECTOR SIMILARITY FUNCTIONS
-- ===================================

-- Function for menu item similarity search
CREATE OR REPLACE FUNCTION match_menu_items(
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  name text,
  description text,
  restaurant_id uuid,
  similarity float
)
LANGUAGE sql stable
AS $$
  SELECT
    id,
    name,
    description,
    restaurant_id,
    1 - (embedding <=> query_embedding) as similarity
  FROM menu_items
  WHERE 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$;

-- Function for restaurant similarity search
CREATE OR REPLACE FUNCTION match_restaurants(
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  name text,
  cuisine text,
  similarity float
)
LANGUAGE sql stable
AS $$
  SELECT
    id,
    name,
    cuisine,
    1 - (description_embedding <=> query_embedding) as similarity
  FROM restaurants
  WHERE 1 - (description_embedding <=> query_embedding) > match_threshold
  ORDER BY description_embedding <=> query_embedding
  LIMIT match_count;
$$;

-- Function for geographic restaurant search
CREATE OR REPLACE FUNCTION nearby_restaurants(
  user_lat float,
  user_lng float,
  radius_meters int DEFAULT 1000,
  limit_count int DEFAULT 20
)
RETURNS TABLE (
  id uuid,
  name text,
  cuisine text,
  distance_meters float
)
LANGUAGE sql stable
AS $$
  SELECT
    r.id,
    r.name,
    r.cuisine,
    ST_Distance(
      r.location,
      ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326)
    ) as distance_meters
  FROM restaurants r
  WHERE ST_DWithin(
    r.location,
    ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326),
    radius_meters
  )
  ORDER BY distance_meters
  LIMIT limit_count;
$$;

-- ===================================
-- 6. TRIGGERS FOR AUTO-UPDATING
-- ===================================

-- Function to update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables that need auto-updating timestamps
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_restaurants_updated_at BEFORE UPDATE ON restaurants 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_menu_items_updated_at BEFORE UPDATE ON menu_items 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_health_connections_updated_at BEFORE UPDATE ON health_connections 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===================================
-- 7. INITIAL DATA
-- ===================================

-- Insert some initial schema fields
INSERT INTO profile_schema_fields (key, type, source, description) VALUES
('preferred_cuisines', 'array', 'ai', 'User preferred cuisine types extracted from conversations'),
('spice_tolerance', 'string', 'ai', 'User spice preference level (mild, medium, hot)'),
('meal_timing_preferences', 'array', 'ai', 'Preferred meal times and frequency'),
('social_dining_preference', 'string', 'ai', 'Preference for dining alone vs with others'),
('environmental_consciousness', 'string', 'ai', 'Preference for sustainable/local food options');

-- Setup complete!
