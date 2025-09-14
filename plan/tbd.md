# Epicure Backend Documentation (TBD - To Be Developed)

## Overview

This document describes the Epicure backend architecture, key routes, and integration points with both Supabase and the frontend. The backend is designed to support parallel development with comprehensive mock data while the Supabase data population is in progress.

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI (Python) - High-performance, modern API framework
- **Database**: Supabase (PostgreSQL with PostGIS and pgvector)
- **AI/ML**: Groq API with DeepSeek-V3 for conversational AI and preference extraction
- **Authentication**: JWT tokens (future implementation)
- **Environment Management**: Python-dotenv for configuration

### Project Structure
```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
└── app/
    ├── core/
    │   ├── config.py      # Application settings
    │   └── supabase.py    # Supabase client configuration
    ├── models/
    │   ├── restaurant.py  # Restaurant & menu item models
    │   └── user.py        # User & profile models
    ├── schemas/
    │   ├── restaurant.py  # API request/response schemas
    │   └── user.py        # User API schemas
    ├── services/
    │   ├── restaurant_service.py  # Restaurant business logic
    │   └── ai_service.py          # AI/ML service integration
    └── api/v1/
        ├── api.py         # Main API router
        └── endpoints/
            ├── restaurants.py  # Restaurant endpoints
            ├── users.py       # User management endpoints
            ├── chat.py        # Conversational AI endpoints
            └── health.py      # Health data integration endpoints
```

### Key Design Principles

1. **Parallel Development Support**: All services have mock implementations that work without Supabase
2. **Frontend Compatibility**: API responses exactly match frontend TypeScript interfaces
3. **Graceful Degradation**: If Supabase is unavailable, the system falls back to mock data
4. **Modular Architecture**: Clear separation between data access, business logic, and API layers
5. **AI-Ready**: Built-in support for DeepSeek-V3 conversational AI and preference extraction

## Key API Routes

### Restaurant Endpoints (`/api/v1/restaurants`)

#### `POST /search`
**Purpose**: Main search endpoint used by frontend SwipeInterface
**Request**:
```json
{
  "query": "healthy lunch under $15",
  "location": {"lat": 40.7580, "lng": -73.9855},
  "filters": {
    "max_price": 3,
    "max_distance_miles": 2.0,
    "dietary_restrictions": ["vegetarian"],
    "max_calories": 600
  },
  "limit": 20
}
```
**Response**: Array of restaurants matching frontend `FrontendRestaurant` interface
**Mock Data**: Returns 3 sample restaurants with realistic data

#### `GET /stats`
**Purpose**: Restaurant database statistics for dashboard
**Response**: `{"restaurants": 2000, "menu_items": 6039, "cuisines": 25, "neighborhoods": 5}`

#### `GET /{restaurant_id}`
**Purpose**: Detailed restaurant information
**Response**: Full restaurant object with menu items

#### `GET /nearby`
**Purpose**: Location-based restaurant discovery
**Parameters**: `lat`, `lng`, `radius` (miles), `limit`

### User Endpoints (`/api/v1/users`)

#### `POST /create`
**Purpose**: Create new user account
**Request**: `{"email": "user@example.com", "apple_id": "optional"}`

#### `GET /{user_id}/profile`
**Purpose**: Get user profile (matches frontend `UserProfile` interface)
**Response**: Profile data compatible with frontend onboarding

#### `PUT /{user_id}/profile`
**Purpose**: Update user profile from frontend forms

#### `PATCH /{user_id}/preferences`
**Purpose**: Update user preferences from SwipeInterface

#### `POST /{user_id}/interactions/swipe`
**Purpose**: Record swipe actions (like/dislike/skip)
**Request**: `{"restaurant_id": "123", "action": "like", "context": {...}}`

#### `GET /{user_id}/interactions/liked`
**Purpose**: Get liked restaurants for LikedScreen component

### Chat Endpoints (`/api/v1/chat`)

#### `POST /message`
**Purpose**: Main conversational AI endpoint
**Features**:
- Extracts structured preferences using DeepSeek-V3
- Generates natural language responses
- Triggers restaurant search when location provided
- Proposes profile extensions

**Request**:
```json
{
  "message": "I want something healthy but filling for lunch",
  "context": {
    "location": {"lat": 40.7580, "lng": -73.9855},
    "meal_time": "lunch"
  }
}
```

**Response**:
```json
{
  "response": "I found some great healthy options...",
  "extracted_preferences": {
    "health_priority": "high",
    "portion_preference": "filling",
    "meal_timing_preference": "lunch"
  },
  "search_triggered": true,
  "search_results": [...]
}
```

#### `GET /{user_id}/history`
**Purpose**: Chat history for conversation continuity

#### `POST /extract-preferences`
**Purpose**: Standalone preference extraction for testing

### Health Endpoints (`/api/v1/health`)

#### `POST /import`
**Purpose**: Apple Health data import during onboarding
**Features**:
- Processes HealthKit data
- Auto-fills profile fields
- Proposes smart extensions (protein targets, dietary awareness)

#### `GET /{user_id}/connections`
**Purpose**: Health data connection status

#### `POST /{user_id}/sync`
**Purpose**: Manual health data sync

## Supabase Integration

### Database Models

The backend defines Pydantic models that map to Supabase tables:

```python
# Restaurant model matches database schema
class Restaurant(BaseModel):
    id: UUID4
    name: str
    cuisine: Optional[str]
    latitude: Optional[float] 
    longitude: Optional[float]
    rating: Optional[float]
    price_level: Optional[int]  # 1-4
    # ... other fields

# Frontend transformation
class FrontendRestaurant(BaseModel):
    id: str
    name: str
    cuisine: str
    image: str
    distance: str  # "0.3 mi"
    price: str     # "$$"
    rating: float
    # ... matches frontend TypeScript interface exactly
```

### Connection Strategy

1. **Primary**: Uses Supabase service role key for full database access
2. **Fallback**: Graceful degradation to mock data if connection fails
3. **Geographic Queries**: Leverages PostGIS for location-based searches
4. **Vector Queries**: Ready for pgvector similarity searches (when data populated)

### Query Examples

```python
# Location-based restaurant search
supabase.table('restaurants').select('*').filter(
    'location', 'dwithin', f'POINT({lng} {lat})', radius_meters
).limit(20).execute()

# Vector similarity search (future)
supabase.rpc('match_menu_items', {
    'query_embedding': embedding_vector,
    'match_threshold': 0.8,
    'match_count': 10
})
```

## Frontend Integration

### Data Compatibility

The backend is designed to seamlessly integrate with the existing frontend:

1. **Restaurant Interface**: API responses match the frontend `Restaurant` interface exactly
2. **User Profile**: Compatible with frontend `UserProfile` and onboarding flow
3. **Search Results**: Plug-and-play replacement for current mock data
4. **Chat Interface**: Ready for frontend chat/voice components

### Integration Points

#### SwipeInterface Component
- **Current**: Uses `MOCK_RESTAURANTS` array
- **Integration**: Replace with `POST /api/v1/restaurants/search` call
- **Benefits**: Real restaurant data, personalized results, AI-powered matching

#### OnboardingScreen Component
- **Current**: Simulates Apple Health data
- **Integration**: Use `POST /api/v1/health/import` for real HealthKit data
- **Benefits**: Auto-fill profile, smart preference proposals

#### ChatModal Component
- **Current**: Mock conversation
- **Integration**: `POST /api/v1/chat/message` for real AI conversations
- **Benefits**: DeepSeek-V3 powered preference extraction, intelligent responses

### Example Frontend Integration

```typescript
// Replace mock restaurant loading
const loadRestaurants = async () => {
  const response = await fetch('/api/v1/restaurants/search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      query: userQuery,
      location: userLocation,
      filters: userFilters,
      limit: 20
    })
  });
  
  const data = await response.json();
  setRestaurants(data.restaurants); // Direct compatibility!
};
```

## Mock Data Strategy

### Development Benefits

1. **Immediate Frontend Testing**: Frontend can develop against realistic data
2. **API Contract Validation**: Ensures responses match expected schemas
3. **Performance Testing**: Mock responses have configurable delays
4. **Error Handling**: Mock failures help test error states

### Mock Data Examples

```python
# Mock restaurant matches frontend exactly
FrontendRestaurant(
    id='1',
    name='Green Bowl Kitchen',
    cuisine='Healthy Bowls',
    image='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
    distance='0.3 mi',
    price='$$',
    rating=4.8,
    waitTime='15 min',
    calories=420,
    protein=28,
    dietary=['Vegetarian', 'Gluten-free'],
    highlights=['High protein', 'Fresh ingredients']
)
```

### Switching to Real Data

Environment variable `MOCK_DATA=false` switches all services to Supabase. No code changes required.

## AI Service Integration

### DeepSeek-V3 Capabilities

1. **Preference Extraction**: Converts natural language to structured preferences
2. **Menu Analysis**: Deep understanding of food descriptions and properties  
3. **Semantic Similarity**: Context-aware matching between queries and items
4. **Conversational Responses**: Natural, helpful responses to user messages

### Fallback Strategy

```python
# Robust fallback chain
try:
    # Primary: DeepSeek-V3 (when available on Groq)
    response = await client.chat.completions.create(model="deepseek-v3", ...)
except:
    try:
        # Fallback 1: Llama3-70B for complex tasks  
        response = await client.chat.completions.create(model="llama3-70b-8192", ...)
    except:
        # Fallback 2: Mock data for development
        response = mock_preference_extraction(message)
```

### Example AI Output

```json
{
  "extracted_preferences": {
    "budget": 15,
    "health_priority": "high", 
    "dietary_restrictions": [
      {"restriction": "vegetarian", "confidence": 0.9}
    ],
    "emotional_context": "energy",
    "cooking_method_preferences": ["grilled", "fresh"],
    "nutrition_goals": ["high-protein"]
  }
}
```

## Environment Configuration

### Required Environment Variables

```bash
# Supabase (provided by data population agent)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Groq API
GROQ_API_KEY=gsk_your_groq_key

# Development
MOCK_DATA=false  # Set to true for development without Supabase
DEBUG=true
LOG_LEVEL=info
```

### Optional Variables

```bash
# Future integrations
GOOGLE_PLACES_API_KEY=your_google_key
HUGGINGFACE_API_TOKEN=hf_your_token

# Security (production)
SECRET_KEY=your_jwt_secret
```

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.example .env
# Edit .env with your keys
```

### 3. Run Development Server
```bash
python main.py
# or
uvicorn main:app --reload
```

### 4. Test API
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/restaurants/stats
```

### 5. Frontend Integration
Update frontend API base URL to `http://localhost:8000/api/v1`

## TODOs and Open Questions

### High Priority TODOs

1. **Authentication System**
   - [ ] Implement JWT authentication
   - [ ] Apple Sign-In integration
   - [ ] User session management

2. **Real Data Integration** 
   - [ ] Test with populated Supabase data
   - [ ] Optimize database queries
   - [ ] Implement vector similarity search

3. **Production Readiness**
   - [ ] Error handling and logging
   - [ ] Rate limiting
   - [ ] Health checks and monitoring
   - [ ] Docker containerization

### Medium Priority TODOs

4. **AI Enhancement**
   - [ ] DeepSeek-V3 integration when available on Groq
   - [ ] Embedding generation for menu items
   - [ ] Real-time preference learning

5. **Feature Completions**
   - [ ] Real Apple Health integration
   - [ ] Push notifications
   - [ ] Restaurant owner dashboard
   - [ ] Advanced filtering

### Open Questions

1. **Data Population Timeline**: When will Supabase be fully populated?
2. **DeepSeek-V3 Availability**: Is DeepSeek-V3 available on Groq yet?
3. **Apple Health Permissions**: What specific HealthKit permissions do we need?
4. **Production Deployment**: What's the deployment strategy (AWS, Vercel, etc.)?
5. **Performance Requirements**: What are the target response times?

### Integration Questions

1. **Frontend Deployment**: How will frontend connect to backend in production?
2. **Real-time Updates**: Do we need WebSocket support for live data?
3. **Offline Support**: Should the app work offline with cached data?
4. **Analytics**: What user interactions should be tracked?

## Current Status

### ✅ Completed
- [x] FastAPI backend structure
- [x] All API endpoints matching frontend needs
- [x] Supabase integration with fallback
- [x] Mock data for parallel development
- [x] AI service with Groq integration
- [x] Data models matching frontend interfaces

### 🔄 In Progress (Other Agents)
- [ ] Supabase data population
- [ ] Database schema creation

### ⏳ Ready for Integration
- Backend API ready for frontend consumption
- Mock data provides realistic development experience
- Seamless switch to real data when Supabase is ready

## Contact/Support

For questions about backend integration:
1. Check API documentation at `http://localhost:8000/docs`
2. Review mock data at `/debug/*` endpoints
3. Test specific endpoints with provided curl examples

The backend is designed to support rapid frontend development while the data population completes in parallel.
