# Epicure Backend Architecture Plan

## Executive Summary

Based on detailed analysis of the frontend application, this document outlines the backend architecture needed to support Epicure's food recommendation system. The frontend is a sophisticated Tinder-style food discovery app with Apple Health integration, conversational AI personalization, and detailed nutritional tracking.

## Frontend Analysis Summary

### Core Features Discovered
1. **Swipe-based Food Discovery**: Tinder-style interface for restaurants/dishes
2. **Apple Health Integration**: Automatic import of health data during onboarding
3. **Conversational Personalization**: Chat and voice interfaces for preference learning
4. **User Profile Management**: Comprehensive health and preference tracking
5. **Liked Items Management**: Save and manage favorite restaurants
6. **Real-time Filtering**: Dynamic restaurant filtering based on preferences

### Key Data Structures from Frontend
```typescript
interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  image: string;
  distance: string;
  price: string; // $, $$, $$$, $$$$
  rating: number;
  waitTime?: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
  dietary?: string[]; // ['Vegetarian', 'Gluten-free']
  highlights: string[]; // ['High protein', 'Quick service']
  address?: string;
  phone?: string;
}

interface UserProfile {
  age: string;
  height: string;
  weight: string;
  gender: string;
  activityLevel: string;
  goals: string[];
  appleId?: string;
  healthData?: any;
}
```

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI (Python) for high-performance API
- **Database**: PostgreSQL with PostGIS for geo queries
- **Vector Database**: Supabase with pgvector extension
- **AI/ML**: Groq DeepSeek-V3 (primary) + fallback models + Hugging Face transformers
- **Cache**: Redis for session data and frequent queries
- **Message Queue**: Celery for background tasks
- **Real-time**: WebSocket support for live updates

### Core Services

#### 1. Authentication Service
```python
# Endpoints
POST /auth/apple-signin      # Apple ID authentication
POST /auth/email-signup      # Email registration
POST /auth/login             # Email/password login
POST /auth/refresh           # Token refresh
POST /auth/logout            # Session cleanup

# Apple Health Integration
POST /auth/apple-health/connect    # Request HealthKit permissions
GET  /auth/apple-health/sync       # Sync health data
POST /auth/apple-health/disconnect # Revoke permissions
```

#### 2. User Profile Service
```python
# Profile Management
GET    /profile                # Get user profile
PUT    /profile                # Update profile
PATCH  /profile/preferences    # Update specific preferences
DELETE /profile                # Delete account

# Health Data Integration
POST /profile/health/import    # Import Apple Health data
GET  /profile/health/status    # Health sync status
POST /profile/health/propose   # Propose profile extensions from health data

# Add-only Schema Support (per PRD)
POST /profile/extensions       # Add new profile fields
GET  /profile/extensions       # Get extension schema
PUT  /profile/extensions/{key} # Update extension value
```

#### 3. Restaurant Discovery Service
```python
# Core Discovery
POST /restaurants/search       # Main search endpoint
GET  /restaurants/{id}         # Restaurant details
GET  /restaurants/nearby       # Location-based discovery

# Filtering & Ranking
POST /restaurants/filter       # Apply user constraints
GET  /restaurants/categories   # Available cuisines/categories
GET  /restaurants/trending     # Popular restaurants

# Data Management
POST /restaurants/bulk-import  # Import restaurant data
PUT  /restaurants/{id}         # Update restaurant info
```

#### 4. User Interaction Service
```python
# Swipe Actions
POST /interactions/swipe       # Record swipe (like/dislike)
GET  /interactions/liked       # Get liked restaurants
DELETE /interactions/liked/{id} # Remove from liked

# Preference Learning
POST /interactions/feedback    # Explicit feedback
GET  /interactions/history     # Interaction history
POST /interactions/reset       # Reset learning data
```

#### 5. Conversational AI Service (DeepSeek-V3 powered)
```python
# Chat Interface
POST /chat/message             # Send chat message (DeepSeek-V3 primary)
GET  /chat/history             # Chat history
POST /chat/context             # Update conversation context

# Voice Interface
POST /voice/transcribe         # Speech-to-text
POST /voice/synthesize         # Text-to-speech
POST /voice/process            # Process voice command (DeepSeek-V3)

# Preference Extraction
POST /chat/extract-preferences # Extract structured preferences (DeepSeek-V3)
POST /chat/propose-extensions  # Propose new profile fields (DeepSeek-V3)
```

### Database Schema

#### Core Tables
```sql
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

### API Endpoints Detail

#### 1. Restaurant Search (Core Endpoint)
```python
POST /restaurants/search
Content-Type: application/json

{
  "query": "high protein lunch under $20",
  "location": {
    "lat": 40.7580,
    "lng": -73.9855
  },
  "filters": {
    "max_price": 3,
    "max_distance_miles": 2.0,
    "dietary_restrictions": ["vegetarian"],
    "max_calories": 600,
    "min_protein": 25
  },
  "user_context": {
    "current_goal": "muscle_gain",
    "meal_time": "lunch",
    "urgency": "normal"
  },
  "limit": 20
}

Response:
{
  "restaurants": [
    {
      "id": "uuid",
      "name": "Green Bowl Kitchen",
      "cuisine": "Healthy Bowls",
      "image": "https://...",
      "distance": "0.3 mi",
      "price": "$$",
      "rating": 4.8,
      "waitTime": "15 min",
      "calories": 420,
      "protein": 28,
      "carbs": 35,
      "fat": 18,
      "dietary": ["Vegetarian", "Gluten-free"],
      "highlights": ["High protein", "Fresh ingredients"],
      "score": 0.92,
      "explanation": {
        "factors": [
          {"factor": "protein_match", "score": 0.95, "reason": "28g protein meets your goal"},
          {"factor": "distance", "score": 0.90, "reason": "Very close to you"},
          {"factor": "rating", "score": 0.88, "reason": "Highly rated by users"}
        ]
      }
    }
  ],
  "meta": {
    "total_results": 45,
    "search_time_ms": 120,
    "filters_applied": ["dietary", "price", "distance"],
    "personalization_score": 0.87
  }
}
```

#### 2. Health Data Import
```python
POST /profile/health/import
Content-Type: application/json

{
  "source": "apple_health",
  "data": {
    "basic_info": {
      "age": 28,
      "height_cm": 175,
      "weight_kg": 70,
      "biological_sex": "male"
    },
    "activity": {
      "activity_level": "moderate",
      "avg_daily_calories_burned": 2400,
      "workout_frequency": 4
    },
    "nutrition": {
      "avg_daily_calories": 2200,
      "avg_protein_g": 120,
      "avg_carbs_g": 250,
      "avg_fat_g": 75,
      "avg_sodium_mg": 2100
    }
  },
  "sync_token": "apple_health_token_123"
}

Response:
{
  "profile_updates": {
    "canonical_fields": {
      "age": 28,
      "height_cm": 175,
      "weight_kg": 70,
      "activity_level": "moderate"
    },
    "proposed_extensions": [
      {
        "key": "protein_target_g",
        "value": 140,
        "confidence": 0.85,
        "reasoning": "Based on your weight (70kg) and moderate activity level, recommending 2g per kg",
        "status": "proposed"
      },
      {
        "key": "sodium_awareness",
        "value": true,
        "confidence": 0.70,
        "reasoning": "Your average sodium intake (2100mg) is near the recommended limit",
        "status": "proposed"
      }
    ]
  },
  "requires_confirmation": true
}
```

#### 3. Chat Interface (Groq-powered)
```python
POST /chat/message
Content-Type: application/json

{
  "message": "I want something healthy but filling for lunch, under $15",
  "context": {
    "location": {"lat": 40.7580, "lng": -73.9855},
    "meal_time": "lunch",
    "urgency": "normal"
  }
}

# DeepSeek-V3 + Fallback Implementation:
class DeepSeekConversationalService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.primary_model = "deepseek-v3"  # Superior reasoning
        self.fallback_model = "llama3-70b-8192"  # Complex tasks fallback
        self.speed_fallback = "mixtral-8x7b-32768"  # Speed fallback
    
    async def extract_preferences(self, message: str, context: dict):
        prompt = f"""
        Analyze this food preference message with deep reasoning:
        Message: "{message}"
        Context: {json.dumps(context)}
        
        Extract comprehensive preferences with deep analysis:
        - budget (number or null)
        - health_priority (low/medium/high with reasoning)
        - portion_preference (small/medium/large/filling)
        - dietary_restrictions (array with confidence scores and reasons)
        - cuisine_preferences (array with cultural context)
        - urgency (low/normal/high)
        - emotional_context (comfort/energy/social/celebration/stress)
        - meal_timing_preference (early/normal/late with context)
        - spice_tolerance (mild/medium/hot with cultural preferences)
        - cooking_method_preferences (grilled/fried/raw/steamed/etc)
        - ingredient_quality_preference (organic/grass-fed/local/etc)
        - nutrition_goals (weight-loss/muscle-gain/maintenance/performance)
        - allergen_concerns (with severity levels)
        - texture_preferences (crunchy/smooth/chewy/etc)
        
        Analyze implicit preferences, cultural context, and unstated dietary needs.
        Provide confidence scores and reasoning for all extractions.
        """
        
        try:
            # Try DeepSeek-V3 first (best reasoning)
            response = await self.client.chat.completions.create(
                model=self.primary_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1024
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            # Fallback to Llama3-70B for complex reasoning
            try:
                response = await self.client.chat.completions.create(
                    model=self.fallback_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=512
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e2:
                # Final fallback to Mixtral for speed
                response = await self.client.chat.completions.create(
                    model=self.speed_fallback,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=512
                )
                return json.loads(response.choices[0].message.content)

Response:
{
  "response": "I found some great healthy and filling options under $15 near you! Let me show you restaurants that match your preferences.",
  "extracted_preferences": {
    "meal_budget": 15,
    "health_priority": "high",
    "portion_preference": "filling",
    "meal_type": "lunch"
  },
  "proposed_extensions": [
    {
      "key": "lunch_budget_preference",
      "value": 15,
      "confidence": 0.90,
      "needs_confirmation": true
    }
  ],
  "search_triggered": true,
  "search_results": [
    // Restaurant objects as in search endpoint
  ]
}
```

#### 6. Menu Analysis Service (DeepSeek-V3 powered)
```python
# Menu Item Analysis
POST /menu/analyze               # Analyze menu item descriptions for tags
POST /menu/batch-analyze         # Batch analyze multiple items
GET  /menu/tags/{item_id}        # Get tags for specific menu item
PUT  /menu/tags/{item_id}        # Update/override tags

# Restaurant Menu Processing
POST /restaurants/{id}/analyze-menu  # Analyze entire restaurant menu
GET  /restaurants/{id}/dietary-options # Get dietary filtering options
```

### Integration with Existing Data

The backend will connect to the existing `soho_menu_harvest` data:

```python
# Data Import Service
class DataImportService:
    async def import_harvested_data(self):
        """Import from soho_menu_harvest/data/ files"""
        
        # Import restaurants from venues_enriched.jsonl
        venues = await self.load_venues()
        restaurants = await self.transform_venues_to_restaurants(venues)
        
        # Import menu items from menu_items.csv
        menu_items = await self.load_menu_items()
        items = await self.transform_to_menu_items(menu_items)
        
        # Generate embeddings for semantic search
        await self.generate_embeddings(restaurants, items)
        
        # Store in database
        await self.bulk_insert_restaurants(restaurants)
        await self.bulk_insert_menu_items(items)
```

### Security & Privacy

1. **Authentication**: JWT tokens with refresh mechanism
2. **Health Data**: HIPAA-compliant handling, encrypted at rest
3. **Location Data**: Fuzzy location for privacy
4. **Data Retention**: Configurable deletion policies
5. **Consent Management**: Granular permissions for health data

### Deployment Architecture

```yaml
# docker-compose.yml
services:
  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/epicure
      - REDIS_URL=redis://redis:6379
      - SUPABASE_URL=${SUPABASE_URL}
    
  db:
    image: postgis/postgis:15-3.3
    environment:
      - POSTGRES_DB=epicure
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    
  redis:
    image: redis:7-alpine
    
  vector-db:
    # Supabase handles this
    
  worker:
    build: ./backend
    command: celery worker
    depends_on: [redis, db]
```

## Development Phases

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] FastAPI setup with authentication
- [ ] PostgreSQL schema implementation
- [ ] Basic CRUD operations for users/profiles
- [ ] Apple Health data import pipeline

### Phase 2: Restaurant Discovery (Week 3-4)
- [ ] Restaurant search endpoint with filtering
- [ ] Location-based queries with PostGIS
- [ ] Integration with harvested data
- [ ] Basic recommendation scoring

### Phase 3: AI Integration (Week 5-6)
- [ ] Chat interface implementation
- [ ] Preference extraction from conversations
- [ ] Add-only schema with extensions
- [ ] Vector embeddings for semantic search

### Phase 4: Advanced Features (Week 7-8)
- [ ] Real-time updates via WebSocket
- [ ] Advanced recommendation algorithms
- [ ] Performance optimization
- [ ] Comprehensive testing

## Success Metrics

1. **API Performance**: <200ms response time for search
2. **Data Accuracy**: >95% correct restaurant information
3. **Personalization**: >80% user satisfaction with recommendations
4. **Health Integration**: Seamless Apple Health sync for >90% of users
5. **Conversation Quality**: Accurate preference extraction >85% of time

## Next Steps

1. Set up Supabase project with pgvector extension
2. Create development environment with Docker
3. Implement authentication and profile services
4. Begin integration with existing restaurant data
5. Develop recommendation engine (see recommendation_engine.md)

This backend architecture provides a solid foundation for the Epicure frontend while maintaining flexibility for future enhancements and ensuring excellent user experience through fast, personalized recommendations.
