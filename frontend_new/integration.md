# Frontend_New ↔ Backend Integration Plan

## 🎯 Overview

This document outlines the integration plan for the new **menu-item focused** frontend with our existing **restaurant-focused** backend. The key paradigm shift requires significant backend updates to support a more granular, dish-level recommendation system.

## 🔄 Key Architectural Changes

### Frontend_New Architecture (Menu-Item Focused)
- **Primary Entity**: `MenuItem` (individual dishes)
- **Secondary Entity**: `Restaurant` (nested within MenuItem)
- **User Experience**: Swipe on individual dishes, not restaurants
- **Conversational AI**: Deep integration with chat for preference refinement
- **Detailed Nutrition**: Comprehensive nutrition data per dish

### Current Backend Architecture (Restaurant Focused)
- **Primary Entity**: `Restaurant` 
- **Limited Menu Data**: Basic menu structure
- **Simple Search**: Restaurant-level filtering
- **Basic AI**: Limited conversational capabilities

## 📊 Data Model Comparison

### Frontend_New MenuItem Interface
```typescript
interface MenuItem {
  id: string;
  name: string;
  description: string;
  image: string;
  restaurant: {
    name: string;
    cuisine: string;
    distance: string;
    rating: number;
    price: string;
  };
  price: number;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber?: number;
  sugar?: number;
  sodium?: number;
  dietary: string[];
  ingredients: string[];
  highlights: string[];
  category: string;
  preparationTime?: string;
  isPopular?: boolean;
}
```

### Current Backend Restaurant Model
```python
class Restaurant(BaseModel):
  id: str
  name: str
  cuisine: str
  image: str
  distance: str
  price: str
  rating: float
  # Limited menu support
```

## 🚧 Required Backend Changes

### 1. New Data Models

#### Enhanced MenuItem Model
```python
class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    image: str
    restaurant_id: str
    restaurant: RestaurantInfo  # Nested restaurant data
    price: float
    
    # Comprehensive Nutrition
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    
    # Dietary & Preferences
    dietary: List[str] = []
    ingredients: List[str] = []
    allergens: List[str] = []
    
    # Metadata
    category: str
    highlights: List[str] = []
    preparation_time: Optional[str] = None
    is_popular: Optional[bool] = False
    
    # ML Features
    embedding: Optional[List[float]] = None
    tags: List[str] = []
    cuisine_tags: List[str] = []

class RestaurantInfo(BaseModel):
    id: str
    name: str
    cuisine: str
    distance: str
    rating: float
    price_range: str  # $, $$, $$$
    address: Optional[str] = None
    phone: Optional[str] = None
```

### 2. New API Endpoints

#### Menu-Item Search & Discovery
```python
# Primary endpoint for frontend_new
POST /api/v1/menu-items/search
{
  "query": "high protein breakfast",
  "location": {"lat": 40.7580, "lng": -73.9855},
  "filters": {
    "max_calories": 600,
    "min_protein": 20,
    "dietary_restrictions": ["vegetarian"],
    "max_price": 15.0,
    "categories": ["breakfast", "bowls"]
  },
  "personalization": {
    "user_id": "user-123",
    "preferences": {...},
    "context": "post_workout"
  },
  "limit": 20
}

Response:
{
  "menu_items": [MenuItem...],
  "meta": {
    "total_results": 47,
    "personalization_score": 0.89,
    "search_time_ms": 145,
    "filters_applied": [...],
    "recommendations_reason": "Based on your protein goals and workout schedule"
  }
}
```

#### Conversational AI Integration
```python
POST /api/v1/ai/chat/food-search
{
  "message": "I need something quick and healthy after my workout",
  "context": {
    "user_id": "user-123",
    "recent_meals": [...],
    "current_time": "14:30",
    "location": {...}
  },
  "chat_history": [...]
}

Response:
{
  "ai_response": "Perfect! I found high-protein options nearby...",
  "suggested_search": {
    "query": "high protein quick meals",
    "filters": {...}
  },
  "menu_items": [MenuItem...],
  "conversation_id": "conv-123"
}
```

#### Enhanced Interaction Tracking
```python
POST /api/v1/users/{user_id}/interactions/menu-item-swipe
{
  "menu_item_id": "item-123",
  "action": "like|dislike|order",
  "context": {
    "search_query": "...",
    "position": 3,
    "conversation_context": "...",
    "time_spent_viewing": 4.2
  }
}
```

### 3. Database Schema Updates

#### New Tables
```sql
-- Menu Items (primary entity)
CREATE TABLE menu_items (
    id UUID PRIMARY KEY,
    restaurant_id UUID REFERENCES restaurants(id),
    name TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    price DECIMAL(10,2),
    
    -- Nutrition Facts
    calories INTEGER,
    protein DECIMAL(5,2),
    carbs DECIMAL(5,2),
    fat DECIMAL(5,2),
    fiber DECIMAL(5,2),
    sugar DECIMAL(5,2),
    sodium DECIMAL(8,2),
    
    -- Categories & Tags
    category TEXT,
    dietary_tags TEXT[], -- ['vegan', 'gluten-free']
    ingredients TEXT[],
    allergens TEXT[],
    highlights TEXT[],
    
    -- Metadata
    preparation_time INTERVAL,
    is_popular BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    
    -- ML Features
    embedding vector(384), -- For semantic search
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enhanced Menu Item Interactions
CREATE TABLE menu_item_interactions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    menu_item_id UUID REFERENCES menu_items(id),
    action TEXT NOT NULL, -- 'like', 'dislike', 'order', 'save'
    
    -- Context
    search_query TEXT,
    position INTEGER, -- Position in search results
    conversation_context JSONB,
    time_spent_viewing DECIMAL(5,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversational Sessions
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    session_start TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    context JSONB, -- User goals, current state
    preferences_extracted JSONB,
    total_messages INTEGER DEFAULT 0
);

-- Conversation Messages
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES conversation_sessions(id),
    role TEXT NOT NULL, -- 'user', 'assistant'
    content TEXT NOT NULL,
    intent_extracted JSONB, -- Parsed preferences/goals
    menu_items_suggested UUID[], -- Array of menu item IDs
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔧 Implementation Plan

### Phase 1: Backend Data Model Updates (Day 1)
- [ ] Create new MenuItem and RestaurantInfo models
- [ ] Update database schema with new tables
- [ ] Create data migration scripts
- [ ] Update Supabase setup

### Phase 2: Menu-Item API Development (Day 1-2)
- [ ] Implement `/menu-items/search` endpoint
- [ ] Create menu item service layer
- [ ] Add nutrition filtering and sorting
- [ ] Implement semantic search for menu items

### Phase 3: Conversational AI Integration (Day 2)
- [ ] Create conversation session management
- [ ] Implement DeepSeek-V3 integration for menu item analysis
- [ ] Create preference extraction from natural language
- [ ] Build chat-to-search pipeline

### Phase 4: Frontend Integration (Day 2-3)
- [ ] Create new API client for frontend_new
- [ ] Update SwipeInterface to use menu-item endpoints
- [ ] Integrate chat system with backend AI
- [ ] Implement interaction tracking

### Phase 5: Testing & Optimization (Day 3)
- [ ] Create comprehensive integration tests
- [ ] Performance testing with large menu datasets
- [ ] User experience testing
- [ ] Bug fixes and optimization

## 🧪 Testing Strategy

### Unit Tests
```python
# Menu Item Search Tests
def test_menu_item_search_with_nutrition_filters()
def test_menu_item_search_with_dietary_restrictions()
def test_menu_item_personalization_scoring()

# Conversational AI Tests
def test_preference_extraction_from_chat()
def test_chat_to_search_conversion()
def test_conversation_context_persistence()

# Integration Tests
def test_frontend_menu_item_display()
def test_swipe_interaction_recording()
def test_chat_recommendation_flow()
```

### API Integration Tests
```bash
# Menu Item Search
curl -X POST http://localhost:8000/api/v1/menu-items/search \
  -H "Content-Type: application/json" \
  -d '{"query": "high protein", "filters": {"min_protein": 25}}'

# Conversational Search
curl -X POST http://localhost:8000/api/v1/ai/chat/food-search \
  -H "Content-Type: application/json" \
  -d '{"message": "I want something healthy for lunch"}'
```

### Frontend Integration Tests
```typescript
// Test menu item API integration
test('should fetch menu items from backend', async () => {
  const menuItems = await EpicureAPI.searchMenuItems({
    query: 'protein bowl',
    filters: { min_protein: 20 }
  });
  expect(menuItems.length).toBeGreaterThan(0);
  expect(menuItems[0]).toHaveProperty('protein');
});

// Test chat integration
test('should get AI responses and menu suggestions', async () => {
  const response = await EpicureAPI.sendChatMessage('I need energy for my workout');
  expect(response).toHaveProperty('ai_response');
  expect(response).toHaveProperty('menu_items');
});
```

## 🚀 Migration Strategy

### Data Migration from Current System
```python
# Migrate existing restaurant data to menu-item format
async def migrate_restaurant_to_menu_items():
    """
    Convert existing restaurant data to individual menu items
    using the scraped menu data from soho_menu_harvest
    """
    # Load existing menu data
    menu_items_df = pd.read_csv('soho_menu_harvest/data/menu_items.csv')
    restaurants_df = pd.read_csv('soho_menu_harvest/data/restaurants.csv')
    
    # Transform to new MenuItem format
    for _, menu_item in menu_items_df.iterrows():
        restaurant_info = restaurants_df[restaurants_df['id'] == menu_item['restaurant_id']].iloc[0]
        
        menu_item_obj = MenuItem(
            id=menu_item['id'],
            name=menu_item['name'],
            description=menu_item['description'],
            restaurant=RestaurantInfo(
                id=restaurant_info['id'],
                name=restaurant_info['name'],
                cuisine=restaurant_info['cuisine'],
                # ... map other fields
            ),
            # Parse nutrition data
            calories=parse_calories(menu_item['description']),
            protein=extract_protein(menu_item['description']),
            # ... use AI to extract nutrition if not present
        )
        
        await create_menu_item(menu_item_obj)
```

## 🔍 Key Integration Points

### 1. SwipeInterface Integration
```typescript
// frontend_new/src/components/SwipeInterface.tsx
const loadMenuItems = async () => {
  const request = {
    query: conversationContext || "recommended for you",
    location: userLocation,
    filters: buildFiltersFromPreferences(userPreferences),
    personalization: {
      user_id: userId,
      preferences: userPreferences,
      context: getCurrentContext()
    }
  };
  
  const response = await EpicureAPI.searchMenuItems(request);
  setMenuItems(response.menu_items);
  setPersonalizationReason(response.meta.recommendations_reason);
};
```

### 2. Chat Integration
```typescript
// frontend_new/src/components/ChatModal.tsx
const handleSendMessage = async (message: string) => {
  const response = await EpicureAPI.sendChatMessage(message, {
    user_id: userId,
    conversation_id: currentConversationId,
    current_preferences: userPreferences
  });
  
  // Update chat history
  setChatHistory(prev => [...prev, 
    { sender: 'user', content: message },
    { sender: 'ai', content: response.ai_response }
  ]);
  
  // Update menu items if AI suggests new search
  if (response.menu_items) {
    setMenuItems(response.menu_items);
  }
};
```

## 🎯 Success Metrics

### Technical Performance
- [ ] API response time < 200ms for menu item search
- [ ] AI response time < 3s for conversational queries
- [ ] Successfully handle 100+ concurrent users
- [ ] 99.9% uptime for critical endpoints

### User Experience
- [ ] Seamless transition from chat to menu item discovery
- [ ] Accurate nutrition data display
- [ ] Personalized recommendations improve over time
- [ ] Intuitive swipe experience on individual dishes

### Data Quality
- [ ] 95%+ menu items have complete nutrition data
- [ ] Accurate restaurant association for each menu item
- [ ] Consistent dietary/allergen tagging
- [ ] High-quality images for 90%+ menu items

## 🔧 Development Environment Setup

### Backend Setup
```bash
# Install new dependencies
cd backend
pip install sentence-transformers pandas numpy scikit-learn

# Run database migrations
python scripts/migrate_to_menu_items.py

# Start backend with new endpoints
MOCK_DATA=false python start.py
```

### Frontend_New Setup
```bash
# Install dependencies
cd frontend_new
npm install

# Create environment file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

## ⚠️ Potential Challenges

### 1. Data Quality
- **Challenge**: Converting restaurant-level data to detailed menu items
- **Solution**: Use AI (DeepSeek-V3) to extract nutrition data from descriptions
- **Fallback**: Manual data entry for popular items

### 2. Performance
- **Challenge**: Much larger dataset (menu items vs restaurants)
- **Solution**: Implement proper indexing, caching, and pagination
- **Monitoring**: Track query performance and optimize slow endpoints

### 3. Recommendation Accuracy
- **Challenge**: More complex recommendation logic for individual dishes
- **Solution**: Enhanced ML pipeline with dish-level embeddings
- **Iteration**: Continuous improvement based on user feedback

## 📋 Next Steps

1. **Create new backend models and endpoints** (Priority: HIGH)
2. **Migrate existing data to menu-item format** (Priority: HIGH)  
3. **Build API client for frontend_new** (Priority: HIGH)
4. **Implement conversational AI integration** (Priority: MEDIUM)
5. **Create comprehensive tests** (Priority: MEDIUM)
6. **Performance optimization** (Priority: LOW)

---

## 🎉 Expected Outcome

A fully integrated **menu-item focused** food discovery platform where users can:
- Swipe on individual dishes with detailed nutrition information
- Have natural conversations about food preferences
- Receive personalized recommendations at the dish level
- Get explanations for why specific dishes are recommended
- Track their preferences and dietary goals over time

The integration will create a more granular, personalized, and engaging food discovery experience compared to the current restaurant-focused approach.
