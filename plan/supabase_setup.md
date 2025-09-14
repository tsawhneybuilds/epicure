# Supabase Setup Guide for Epicure

## Step 1: Create Supabase Project

### 1.1 Sign up and Create Project
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" 
3. Sign in with GitHub (recommended)
4. Click "New Project"
5. Choose organization (or create new one)
6. Fill in project details:
   - **Name**: `epicure-production` (or your choice)
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your users (e.g., `us-east-1`)
7. Click "Create new project"
8. Wait 2-3 minutes for setup to complete

### 1.2 Get Connection Details
Once project is ready, go to Settings > Database:
- **Host**: `db.[your-project-ref].supabase.co`
- **Database name**: `postgres`
- **Port**: `6543`
- **User**: `postgres`
- **Password**: The one you set during creation

## Step 2: Enable Required Extensions

### 2.1 Enable pgvector (Vector Database)
1. Go to Database > Extensions in Supabase dashboard
2. Search for "vector" 
3. Enable the `vector` extension
4. Or run in SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2.2 Enable PostGIS (Geographic Queries)
1. In Extensions, search for "postgis"
2. Enable the `postgis` extension
3. Or run in SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

## Step 3: Set Up Database Schema

### 3.1 Run Initial Schema
Go to SQL Editor and run this script:

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis;

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
```

### 3.2 Create Vector Indexes
After your schema is created, add vector indexes for performance:

```sql
-- Create vector indexes for fast similarity search
CREATE INDEX ON menu_items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON restaurants USING ivfflat (description_embedding vector_cosine_ops) WITH (lists = 100);

-- Create geographic indexes
CREATE INDEX ON restaurants USING GIST (location);

-- Create regular indexes for common queries
CREATE INDEX ON user_interactions (user_id, created_at);
CREATE INDEX ON chat_messages (user_id, created_at);
CREATE INDEX ON restaurants (cuisine, price_level);
```

## Step 4: Configure Row Level Security (RLS)

### 4.1 Enable RLS on Tables
```sql
-- Enable RLS on all user-related tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_extension_meta ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_connections ENABLE ROW LEVEL SECURITY;

-- Create policies (users can only access their own data)
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own interactions" ON user_interactions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own chat messages" ON chat_messages
    FOR ALL USING (auth.uid() = user_id);

-- Restaurants and menu items are public (read-only for users)
CREATE POLICY "Anyone can view restaurants" ON restaurants
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view menu items" ON menu_items
    FOR SELECT USING (true);
```

## Step 5: Set Up Environment Variables

### 5.1 Get API Keys
In your Supabase project, go to Settings > API:
- **Project URL**: `https://[your-project-ref].supabase.co`
- **Anon/Public Key**: For client-side access
- **Service Role Key**: For server-side operations (keep secret!)

### 5.2 Environment Variables
Create a `.env` file in your backend:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Direct Database Connection (for migrations, etc.)
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:6543/postgres

# Groq API for LLM
GROQ_API_KEY=gsk_your_groq_api_key_here

# Hugging Face for embeddings
HUGGINGFACE_API_TOKEN=hf_your_token_here

# Optional: Google Places API
GOOGLE_PLACES_API_KEY=your_google_api_key
```

## Step 6: Test Connection

### 6.1 Test Basic Connection
```python
# test_connection.py
import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

# Test basic query
response = supabase.table('restaurants').select("*").limit(1).execute()
print("Connection successful!", response.data)
```

### 6.2 Test Vector Operations
```python
# test_vectors.py
import numpy as np

# Test vector insertion
test_embedding = np.random.rand(384).tolist()
response = supabase.table('menu_items').insert({
    'name': 'Test Item',
    'description': 'Test description',
    'embedding': test_embedding,
    'restaurant_id': None  # Will need a real restaurant_id
}).execute()

# Test vector similarity search
search_vector = np.random.rand(384).tolist()
response = supabase.rpc('match_menu_items', {
    'query_embedding': search_vector,
    'match_threshold': 0.8,
    'match_count': 10
}).execute()
```

## Step 7: Create Helper Functions

### 7.1 Vector Similarity Function
```sql
-- Create function for vector similarity search
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

-- Similar function for restaurants
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
```

## Step 8: Production Considerations

### 8.1 Backup Configuration
1. Go to Settings > Database
2. Enable automatic backups
3. Set backup retention period
4. Consider setting up point-in-time recovery

### 8.2 Connection Pooling
For production, consider using connection pooling:
```python
# Use pgbouncer connection string for production
DATABASE_URL=postgresql://postgres:password@db.your-project-ref.supabase.co:6543/postgres?pgbouncer=true
```

### 8.3 Monitoring
1. Enable database logs in Settings > Logs
2. Set up alerts for high resource usage
3. Monitor query performance

## Next Steps

1. **Create Supabase project** following steps 1-2
2. **Run database schema** from step 3
3. **Set up environment variables** from step 5  
4. **Test connection** using step 6
5. **Start building your backend** with the connection established

Your Supabase setup will be ready for the Epicure recommendation engine with vector search, geographic queries, and all the required tables for user profiles and restaurant data!
