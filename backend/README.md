# Epicure Backend

FastAPI backend for the Epicure food recommendation system with DeepSeek-V3 AI integration and Supabase database.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.example .env
# Edit .env with your API keys
```

### 3. Start Development Server
```bash
python start.py
```

Or manually:
```bash
python main.py
# or
uvicorn main:app --reload
```

### 4. Test API
```bash
python test_api.py
```

## API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Alternative Docs**: http://localhost:8000/redoc

## Key Features

### 🤖 AI-Powered Recommendations
- DeepSeek-V3 integration via Groq API
- Natural language preference extraction
- Semantic similarity matching
- Conversational AI responses

### 🗃️ Supabase Integration
- PostgreSQL with PostGIS for location queries
- pgvector for semantic search
- Graceful fallback to mock data

### 🔄 Parallel Development Support
- Comprehensive mock data
- Works without external dependencies
- Frontend-compatible responses

### 🍽️ Frontend Integration
- API responses match TypeScript interfaces
- Drop-in replacement for mock data
- Real-time preference learning

## Environment Variables

### Required
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_key
GROQ_API_KEY=gsk_your_key
```

### Optional
```bash
MOCK_DATA=true              # Use mock data for development
DEBUG=true                  # Enable debug mode
GOOGLE_PLACES_API_KEY=key   # For enhanced location data
```

## API Endpoints

### Restaurant Search
```bash
POST /api/v1/restaurants/search
{
  "query": "healthy lunch under $15",
  "location": {"lat": 40.7580, "lng": -73.9855},
  "filters": {"max_price": 3, "dietary_restrictions": ["vegetarian"]},
  "limit": 20
}
```

### Chat Interface
```bash
POST /api/v1/chat/message
{
  "message": "I want something healthy but filling",
  "context": {"location": {"lat": 40.7580, "lng": -73.9855}}
}
```

### User Interactions
```bash
POST /api/v1/users/{user_id}/interactions/swipe
{
  "restaurant_id": "123",
  "action": "like",
  "context": {"search_position": 1}
}
```

### Health Data Import
```bash
POST /api/v1/health/import
{
  "source": "apple_health",
  "data": {
    "basic_info": {"age": 28, "weight_kg": 70},
    "nutrition": {"avg_protein_g": 120}
  }
}
```

## Development

### Project Structure
```
backend/
├── main.py              # FastAPI app entry point
├── start.py             # Development startup script
├── test_api.py          # API testing script
└── app/
    ├── core/            # Configuration and database
    ├── models/          # Data models
    ├── schemas/         # API schemas
    ├── services/        # Business logic
    └── api/v1/          # API routes
```

### Testing
```bash
# Test all endpoints
python test_api.py

# Test specific functionality
curl http://localhost:8000/api/v1/restaurants/stats
curl -X POST http://localhost:8000/api/v1/restaurants/search \
  -H "Content-Type: application/json" \
  -d '{"location": {"lat": 40.7580, "lng": -73.9855}, "limit": 5}'
```

### Mock Data
Set `MOCK_DATA=true` to use realistic mock data for development without external APIs.

Mock data includes:
- 3 sample restaurants with nutrition data
- AI preference extraction simulation
- Apple Health data simulation
- Chat conversation simulation

## Frontend Integration

### Replace Mock Data
Replace frontend mock data calls with API calls:

```typescript
// Before (mock data)
const loadRestaurants = () => {
  setRestaurants(MOCK_RESTAURANTS);
};

// After (real API)
const loadRestaurants = async () => {
  const response = await fetch('/api/v1/restaurants/search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      location: userLocation,
      filters: userFilters,
      limit: 20
    })
  });
  const data = await response.json();
  setRestaurants(data.restaurants);
};
```

### Data Compatibility
All API responses match frontend TypeScript interfaces exactly:
- `Restaurant` interface ✅
- `UserProfile` interface ✅  
- `ChatMessage` interface ✅
- No frontend changes required ✅

## Production Deployment

### Environment Setup
```bash
ENVIRONMENT=production
DEBUG=false
MOCK_DATA=false
SECRET_KEY=your_production_secret
```

### Docker Support (Coming Soon)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

**Import Errors**
```bash
pip install -r requirements.txt
```

**Supabase Connection Failed**
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY

# Or use mock data
export MOCK_DATA=true
```

**Groq API Issues**
```bash
# Check API key
echo $GROQ_API_KEY

# Test with mock AI
export MOCK_DATA=true
```

### Debug Mode
Set `DEBUG=true` for detailed error messages and automatic reloading.

### Logs
Check console output for detailed request/response logging in debug mode.

## Support

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health  
- **Test Suite**: `python test_api.py`
- **Mock Data Endpoints**: `/debug/*` routes

For questions about integration, check the comprehensive `plan/tbd.md` documentation.
