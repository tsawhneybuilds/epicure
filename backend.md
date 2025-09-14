# Epicure Backend Architecture

## Overview
Backend API for the Epicure food recommendation app, designed to serve personalized restaurant recommendations using ML-powered ranking, real-time filtering, and comprehensive restaurant data from the SoHo Menu Harvest dataset.

## Tech Stack

### Core Backend
- **Runtime**: Node.js with TypeScript
- **Framework**: Express.js or Fastify
- **Database**: Supabase (PostgreSQL with pgvector extension)
- **Authentication**: Supabase Auth
- **ML/AI**: Hugging Face Transformers, Sentence Transformers
- **Vector Search**: pgvector for embedding similarity
- **Real-time**: Supabase Realtime for live updates

### Data Sources
- **Restaurant Data**: 2,000+ restaurants from SoHo Menu Harvest
- **Menu Items**: 6,267+ menu items with descriptions, prices, allergens
- **Location Data**: Lat/lng coordinates for all restaurants
- **Enriched Data**: Phone numbers, hours, ratings, delivery links

## Database Schema

### Core Tables

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Restaurants table
CREATE TABLE restaurants (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    cuisine text,
    address text,
    phone text,
    website text,
    location GEOGRAPHY(POINT, 4326),
    rating numeric,
    price_level text, -- $, $$, $$$
    opening_hours jsonb,
    delivery_links jsonb, -- {doordash: url, ubereats: url, etc}
    google_place_id text,
    yelp_id text,
    created_at timestamptz DEFAULT NOW(),
    updated_at timestamptz DEFAULT NOW()
);

-- Menu items table
CREATE TABLE menu_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id uuid REFERENCES restaurants(id),
    menu_id text,
    section text,
    name text NOT NULL,
    description text,
    price numeric,
    currency text DEFAULT 'USD',
    tags text[],
    allergens text[],
    nutrition jsonb, -- {calories, protein, carbs, fat}
    dietary_flags text[], -- [vegan, gluten-free, etc]
    confidence numeric,
    embedding vector(384), -- Sentence transformer embedding
    created_at timestamptz DEFAULT NOW(),
    last_seen timestamptz
);

-- Users table
CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text UNIQUE,
    apple_id text,
    profile jsonb, -- {age, height, weight, gender, activity_level}
    goals text[], -- [muscle_gain, weight_loss, etc]
    goals_text text, -- Free-form goals description
    dietary_restrictions text[], -- [vegan, gluten_free, etc]
    allergens text[],
    budget_max numeric,
    preferred_distance_m integer DEFAULT 1600, -- ~1 mile
    location_home GEOGRAPHY(POINT, 4326),
    preferences jsonb, -- UI preferences, notification settings
    created_at timestamptz DEFAULT NOW(),
    updated_at timestamptz DEFAULT NOW()
);

-- User sessions/searches
CREATE TABLE search_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id),
    query_text text,
    location GEOGRAPHY(POINT, 4326),
    filters jsonb, -- Applied filters
    created_at timestamptz DEFAULT NOW()
);

-- Impressions (shown to user)
CREATE TABLE impressions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id uuid REFERENCES search_sessions(id),
    user_id uuid REFERENCES users(id),
    menu_item_id uuid REFERENCES menu_items(id),
    restaurant_id uuid REFERENCES restaurants(id),
    position integer, -- Position in swipe deck
    score numeric, -- ML ranking score
    score_breakdown jsonb, -- Feature scores for explainability
    shown_at timestamptz DEFAULT NOW()
);

-- User feedback
CREATE TABLE feedback (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    impression_id uuid REFERENCES impressions(id),
    user_id uuid REFERENCES users(id),
    menu_item_id uuid REFERENCES menu_items(id),
    feedback_type text, -- 'like', 'dislike', 'order', 'view_details'
    feedback_at timestamptz DEFAULT NOW()
);

-- User liked items
CREATE TABLE liked_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id),
    menu_item_id uuid REFERENCES menu_items(id),
    restaurant_id uuid REFERENCES restaurants(id),
    liked_at timestamptz DEFAULT NOW(),
    UNIQUE(user_id, menu_item_id)
);
```

### Indexes

```sql
-- Vector similarity search
CREATE INDEX ON menu_items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Geospatial queries
CREATE INDEX ON restaurants USING GIST (location);

-- Filter queries
CREATE INDEX ON menu_items (restaurant_id);
CREATE INDEX ON menu_items USING GIN (tags);
CREATE INDEX ON menu_items USING GIN (allergens);
CREATE INDEX ON menu_items USING GIN (dietary_flags);
CREATE INDEX ON restaurants (price_level);
CREATE INDEX ON feedback (user_id, feedback_type);
CREATE INDEX ON impressions (user_id, shown_at);
```

## API Endpoints

### Authentication
```
POST /auth/signup
POST /auth/login
POST /auth/apple-signin
GET  /auth/profile
PUT  /auth/profile
```

### Search & Recommendations (Frontend-Compatible)
```
POST /api/recommendations/search
Body: {
  query: string,
  location: {lat: number, lng: number},
  preferences: FrontendPreferences, // Direct frontend preferences object
  userProfile: UserProfile,
  limit?: number
}

Response: {
  restaurants: FrontendRestaurant[], // Transformed to frontend format
  total: number,
  sessionId: string,
  explanations: {
    [restaurantId: string]: {
      tags: string[],
      similarity: number,
      reasons: string[]
    }
  }
}

GET /api/recommendations/:userId
Query: ?location=lat,lng&limit=50
```

### Restaurants & Menu Items
```
GET  /api/restaurants
GET  /api/restaurants/:id
GET  /api/restaurants/:id/menu
GET  /api/menu-items/:id
```

### User Actions
```
POST /api/feedback
Body: {
  impressionId: string,
  feedbackType: 'like' | 'dislike' | 'order' | 'view_details'
}

GET  /api/liked-items/:userId
POST /api/liked-items
DELETE /api/liked-items/:id
```

### Analytics
```
GET /api/analytics/user-stats/:userId
GET /api/analytics/popular-items
GET /api/analytics/recommendation-performance
```

## Core Services

### 1. Data Ingestion Service
```typescript
class DataIngestionService {
  async importRestaurants(jsonlPath: string): Promise<void> // Updated for JSONL format
  async importMenuItems(csvPath: string): Promise<void>
  async enrichRestaurantData(): Promise<void>
  async generateEmbeddings(): Promise<void>
}
```

### 2. Recommendation Engine
```typescript
class RecommendationEngine {
  async getRecommendations(
    userId: string,
    query: string,
    location: {lat: number, lng: number},
    preferences: FrontendPreferences // Accept frontend preferences directly
  ): Promise<FrontendRestaurant[]> // Return frontend-compatible format
  
  async applyHardFilters(
    restaurants: Restaurant[],
    filters: SearchFilters,
    userLocation: {lat: number, lng: number}
  ): Promise<Restaurant[]>
  
  async scoreRestaurants(
    restaurants: Restaurant[],
    userGoals: string,
    query: string
  ): Promise<ScoredRestaurant[]>
}
```

### 3. Embedding Service
```typescript
class EmbeddingService {
  async generateItemEmbedding(name: string, description: string): Promise<number[]>
  async generateQueryEmbedding(goals: string, query: string): Promise<number[]>
  async findSimilarItems(embedding: number[], limit: number): Promise<MenuItem[]>
}
```

### 4. Tag Inference Service
```typescript
class TagInferenceService {
  async inferTags(text: string): Promise<{[tag: string]: number}>
  async matchUserGoalsToTags(goals: string): Promise<string[]>
}
```

### 5. Data Transformation Service (NEW - Critical for Frontend Integration)
```typescript
interface FrontendRestaurant {
  id: string;
  name: string;
  cuisine: string;
  image: string;
  distance: string;      // "0.3 mi" format
  price: string;         // "$", "$$", "$$$" format
  rating: number;
  waitTime?: string;     // "15 min" format
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
  dietary?: string[];
  highlights: string[];
  address?: string;
  phone?: string;
}

class DataTransformService {
  transformToFrontendFormat(
    restaurant: BackendRestaurant,
    menuItems: MenuItem[],
    userLocation: {lat: number, lng: number}
  ): FrontendRestaurant
  
  private inferCuisine(name: string, menuItems: MenuItem[]): string
  private calculateDistance(restaurant: BackendRestaurant, userLocation: {lat: number, lng: number}): string
  private normalizePriceLevel(yelpPrice?: string, menuItems?: MenuItem[]): string
  private generateHighlights(restaurant: BackendRestaurant, menuItems: MenuItem[]): string[]
  private estimateWaitTime(restaurant: BackendRestaurant): string
  private extractNutritionAverages(menuItems: MenuItem[]): {calories?: number, protein?: number, carbs?: number, fat?: number}
}
```

### 6. Preference Translation Service (NEW - Maps Frontend to ML Engine)
```typescript
interface FrontendPreferences {
  cuisinePreference?: string;
  mealTime?: 'breakfast' | 'lunch' | 'dinner';
  budgetFriendly?: boolean;
  quickService?: boolean;
  dietary?: 'vegetarian' | 'vegan';
  trackMacros?: boolean;
  showCalories?: boolean;
  showMacros?: boolean;
  showWaitTime?: boolean;
  showDietary?: boolean;
  priorityInfo?: string[];
}

class PreferenceTranslationService {
  translateFrontendPreferences(
    frontendPrefs: FrontendPreferences,
    userProfile: UserProfile,
    query: string
  ): RecommendationRequest
  
  private buildQueryString(prefs: FrontendPreferences, originalQuery: string): string
  private extractGoals(prefs: FrontendPreferences, userProfile: UserProfile): string[]
  private buildFilters(prefs: FrontendPreferences, userProfile: UserProfile): SearchFilters
}
```

## Data Migration Plan

### Phase 1: Core Data Import
1. Import restaurant data from `venues_enriched.jsonl`
2. Import menu items from `menu_items.csv`
3. Clean and normalize data
4. Generate initial embeddings

### Phase 2: Data Enrichment
1. Scrape missing restaurant images
2. Standardize opening hours format
3. Geocode any missing coordinates
4. Validate and clean dietary/allergen tags

### Phase 3: ML Model Setup
1. Initialize sentence transformer model
2. Generate embeddings for all menu items
3. Set up zero-shot classifier for tag inference
4. Create initial scoring weights

## Deployment Architecture

### Development
- **Local**: Docker Compose with PostgreSQL + pgvector
- **Supabase**: Cloud development instance
- **Models**: Local Hugging Face models

### Production
- **API**: Deployed on Vercel/Railway/Render
- **Database**: Supabase Pro with pgvector
- **Models**: Hugging Face Inference API
- **CDN**: Cloudinary for images
- **Monitoring**: Sentry + LogRocket

## Environment Variables
```env
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
HUGGINGFACE_API_KEY=your-hf-key
OPENAI_API_KEY=your-openai-key (optional)
JWT_SECRET=your-jwt-secret
GOOGLE_PLACES_API_KEY=your-google-key
NODE_ENV=development|production
PORT=3001
```

## Development Setup

1. **Clone & Install**
```bash
cd epicure
mkdir backend && cd backend
npm init -y
npm install express typescript @types/node @supabase/supabase-js
npm install @huggingface/inference sentence-transformers
npm install cors helmet morgan dotenv
npm install -D nodemon ts-node @types/express
```

2. **Database Setup**
```bash
# Connect to Supabase and run schema
psql "postgresql://[connection-string]" -f schema.sql
```

3. **Data Import**
```bash
npm run import-data
npm run generate-embeddings
```

4. **Start Development**
```bash
npm run dev
```

## Performance Considerations

### Caching Strategy
- **Redis**: Cache frequent queries and user preferences
- **CDN**: Static assets (images, embeddings)
- **Application**: In-memory caching for ML models

### Scaling
- **Database**: Read replicas for search queries
- **API**: Horizontal scaling with load balancer
- **ML**: Dedicated service for embedding generation

### Monitoring
- **Metrics**: Response times, recommendation quality, user engagement
- **Logs**: Search queries, errors, performance bottlenecks
- **Alerts**: Database performance, API errors, ML model failures

## Security

### Data Protection
- **PII**: Encrypt sensitive user data
- **API**: Rate limiting and authentication
- **Database**: Row-level security in Supabase

### Privacy
- **GDPR**: Data deletion endpoints
- **Location**: Opt-in location sharing
- **Analytics**: Anonymized usage data

## Next Steps for Integration

1. **Frontend Connection**: Update frontend to use real API endpoints
2. **Data Migration**: Import your restaurant dataset
3. **ML Pipeline**: Set up embedding generation and ranking
4. **Testing**: Create test users and validate recommendations
5. **Deployment**: Deploy to production environment

This backend architecture provides a solid foundation for your Epicure app, leveraging your comprehensive restaurant dataset while being ready for ML-powered personalization.
