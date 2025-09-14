# Epicure Recommendation Engine

## Architecture Overview: Embedding + Tag Inference + Weighted Scoring + Hard Constraints

The Epicure recommendation engine uses a hybrid approach combining semantic similarity, zero-shot tag classification, and multi-factor scoring to deliver personalized food recommendations.

### Core Components

| Component | Responsibility |
|-----------|----------------|
| **Item Encoder** | Compute and store embeddings for each dish (name + description) |
| **Goal Parser / Tag Inferencer** | Infer tags/labels from user goals + current input using zero-shot classification |
| **Filters** | Apply hard constraints (hours, diet, budget, distance) |
| **Scoring Engine** | Weighted combination of semantic similarity, tags, rating, price, distance |
| **Swipe/Feedback Logger** | Record impressions, positions, user actions for learning |
| **API Backend** | Search endpoint returning ranked items with score explanations |

## Data Store & Models

### Vector Database
- **Platform**: Supabase (PostgreSQL) with pgvector extension
- **Embeddings**: 384-dimensional vectors from sentence transformers
- **Similarity**: Cosine similarity search with IVFFLAT indexing

### ML Models
- **Zero-shot Classifier**: `facebook/bart-large-mnli` for tag inference
- **Embedding Model**: `all-MiniLM-L6-v2` (384d) or OpenAI text-embedding-ada-002
- **Future**: XGBoost learning-to-rank model trained on user feedback

## Feature Engineering

### Per (User, Item) Features:

1. **Embedding Similarity** (Weight: 0.4)
   - Cosine similarity between user goal embedding and item embedding
   - Captures semantic intent matching

2. **Tag Match Score** (Weight: 0.3)
   - Zero-shot classification probability overlap
   - Tags: `[high protein, low sugar, vegan, gluten-free, budget-friendly, quick-service]`

3. **Rating Normalized** (Weight: 0.1)
   - Restaurant/item rating scaled to 0-1
   - Boosts popular, well-reviewed items

4. **Price Fit** (Weight: 0.1)
   - Distance from user's budget preference
   - Formula: `1 - abs(item_price - user_budget_target) / user_budget_max`

5. **Distance Fit** (Weight: 0.1)
   - Walking distance penalty
   - Formula: `max(0, 1 - distance_meters / user_max_distance)`

### Hard Constraints (Filters)
- **Opening Hours**: Restaurant open at search time
- **Diet/Allergen**: Must match user's dietary restrictions
- **Max Budget**: Item price ≤ user's budget ceiling
- **Max Distance**: Walking distance ≤ user's preferred radius

## Implementation Plan

### Phase 0: Infrastructure Setup (~1 day)

**Tasks:**
- [x] Enable pgvector in Supabase
- [x] Import restaurant and menu item data
- [ ] Set up Hugging Face pipeline for zero-shot classification
- [ ] Generate embeddings for all menu items
- [ ] Create vector indexes for similarity search

**Deliverables:**
- Database with 2,000+ restaurants and 6,267+ menu items
- All items have embeddings stored
- Zero-shot classifier API endpoint ready

### Phase 1: Core Ranking & Swipe Interface (~1-2 days)

**Tasks:**
- [ ] Implement hard filter logic
- [ ] Build scoring function with manual weight tuning
- [ ] Create `/api/search` endpoint
- [ ] Update frontend to use real data API
- [ ] Add "why this pick" explanation chips
- [ ] Implement impression and feedback logging

**Search Endpoint (Frontend-Compatible):**
```typescript
POST /api/recommendations/search
{
  query: string, // "high protein lunch under $15"
  location: {lat: number, lng: number},
  preferences: FrontendPreferences, // Direct from frontend
  userProfile: UserProfile,
  limit?: number
}

Response: {
  restaurants: Array<FrontendRestaurant>, // Transformed to frontend format
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
```

**Frontend Updates:**
- Replace mock data with API calls
- Add loading states and error handling
- Display explanation chips on cards
- Implement feedback logging on swipes

### Phase 2: Optimization & Enhancement (~2-3 days)

**Tasks:**
- [ ] Review misranking cases and adjust weights
- [ ] Optimize zero-shot classifier prompts
- [ ] Add "soft" budget and distance preferences
- [ ] Implement "recent liked item" similarity boost
- [ ] Add cross-encoder re-ranking for top-K items
- [ ] Performance optimization and caching

**Advanced Features:**
- **Recent Likes Boost**: Items similar to recently liked dishes get +0.1 score
- **Diversity Injection**: Occasionally show lower-scored items (10% exploration rate)
- **Time-based Preferences**: Learn user's meal timing preferences
- **Cuisine Variety**: Prevent showing too many similar cuisines

### Phase 3: Learning-to-Rank & Feedback Loop (~1 week)

**Tasks:**
- [ ] Collect sufficient impression and feedback data
- [ ] Train XGBoost ranking model on logged data
- [ ] Implement collaborative filtering for cold start
- [ ] Add A/B testing framework
- [ ] Build offline evaluation metrics

**ML Pipeline:**
```python
# Training data features
features = [
    'embedding_similarity',
    'tag_match_score', 
    'rating_normalized',
    'price_fit_score',
    'distance_fit_score',
    'user_cuisine_affinity',
    'time_of_day_match',
    'recent_likes_similarity'
]

# Target: user feedback (like=1, dislike=0, order=2)
# Model: XGBoost with ranking objective
model = XGBRanker(
    objective='rank:pairwise',
    eval_metric='ndcg',
    learning_rate=0.1,
    max_depth=6
)
```

## Scoring Pipeline (Pseudo-Code)

```python
def search_and_rank(
    query: str, 
    location: tuple, 
    frontend_preferences: dict, 
    user_profile: dict
) -> dict:
    # 1. Translate frontend preferences to ML format
    preference_translator = PreferenceTranslationService()
    ml_request = preference_translator.translate_frontend_preferences(
        frontend_preferences, user_profile, query
    )
    user_goal_text = ml_request.query_string
    
    # 2. Tag inference for user intent
    candidate_labels = [
        'high protein', 'low sugar', 'vegan', 'gluten-free',
        'budget-friendly', 'quick-service', 'healthy', 'comfort-food'
    ]
    goal_tag_probs = zero_shot_classifier(
        user_goal_text, 
        candidate_labels, 
        multi_label=True
    )
    
    # 3. Generate user intent embedding
    user_goal_embedding = embedding_model.encode(user_goal_text)
    
    # 4. Apply hard filters to restaurants (not just menu items)
    candidates = db.query_restaurants_with_menu_items(
        location=location,
        max_distance=ml_request.filters.max_distance,
        max_price=ml_request.filters.max_price,
        dietary_restrictions=ml_request.filters.dietary,
        allergens=ml_request.filters.allergens,
        open_now=True
    )
    
    # 5. Score each restaurant candidate
    scored_restaurants = []
    for restaurant in candidates:
        # Get representative menu items for this restaurant
        menu_items = restaurant.menu_items
        
        # Compute restaurant-level embedding (average of menu items)
        restaurant_embedding = compute_restaurant_embedding(menu_items)
        
        # Embedding similarity
        embedding_sim = cosine_similarity(
            user_goal_embedding, 
            restaurant_embedding
        )
        
        # Tag match score (based on menu items)
        restaurant_text = f"{restaurant.name} {' '.join([item.name + ' ' + item.description for item in menu_items[:5]])}"
        restaurant_tag_probs = zero_shot_classifier(
            restaurant_text, 
            candidate_labels, 
            multi_label=True
        )
        tag_match = compute_tag_overlap(goal_tag_probs, restaurant_tag_probs)
        
        # Other features
        rating_norm = (restaurant.google_rating or restaurant.yelp_rating or 4.0) / 5.0
        avg_price = sum(item.price for item in menu_items) / len(menu_items)
        price_fit = compute_price_fit(ml_request.filters.max_price, avg_price)
        distance_fit = compute_distance_fit(
            location, 
            (restaurant.lat, restaurant.lng), 
            ml_request.filters.max_distance
        )
        
        # Recent likes similarity boost
        recent_boost = compute_recent_likes_boost(user_profile['id'], restaurant)
        
        # Final weighted score
        final_score = (
            0.4 * embedding_sim +
            0.3 * tag_match +
            0.1 * rating_norm +
            0.1 * price_fit +
            0.1 * distance_fit +
            recent_boost
        )
        
        scored_restaurants.append({
            'restaurant': restaurant,
            'menu_items': menu_items,
            'score': final_score,
            'features': {
                'embedding_similarity': embedding_sim,
                'tag_match': tag_match,
                'rating': rating_norm,
                'price_fit': price_fit,
                'distance_fit': distance_fit
            }
        })
    
    # 6. Sort and take top K
    top_restaurants = sorted(scored_restaurants, key=lambda x: x['score'], reverse=True)[:50]
    
    # 7. Transform to frontend format
    transformer = DataTransformService()
    frontend_restaurants = [
        transformer.transform_to_frontend_format(
            scored['restaurant'], 
            scored['menu_items'], 
            location
        ) for scored in top_restaurants
    ]
    
    # 8. Log impressions
    session_id = log_search_session(user_profile['id'], query, location)
    for idx, scored in enumerate(top_restaurants):
        log_impression(
            session_id=session_id,
            user_id=user_profile['id'],
            restaurant_id=scored['restaurant'].id,
            position=idx + 1,
            score=scored['score'],
            features=scored['features']
        )
    
    return {
        'restaurants': frontend_restaurants,
        'total': len(frontend_restaurants),
        'sessionId': session_id,
        'explanations': {
            restaurant.id: {
                'tags': extract_matched_tags(scored['features']['tag_match']),
                'similarity': scored['features']['embedding_similarity'],
                'reasons': generate_explanation_reasons(scored['features'])
            } for restaurant, scored in zip(frontend_restaurants, top_restaurants)
        }
    }
```

## Database Schema for ML

```sql
-- Pre-computed embeddings
ALTER TABLE menu_items ADD COLUMN embedding vector(384);

-- Tag inference cache
CREATE TABLE item_tags (
    id uuid PRIMARY KEY,
    menu_item_id uuid REFERENCES menu_items(id),
    tag text NOT NULL,
    confidence numeric NOT NULL,
    created_at timestamptz DEFAULT NOW()
);

-- User goal embeddings (cached)
CREATE TABLE user_goal_embeddings (
    id uuid PRIMARY KEY,
    user_id uuid REFERENCES users(id),
    goal_text text NOT NULL,
    embedding vector(384),
    created_at timestamptz DEFAULT NOW()
);

-- ML model performance tracking
CREATE TABLE model_performance (
    id uuid PRIMARY KEY,
    model_name text,
    version text,
    metric_name text,
    metric_value numeric,
    evaluated_at timestamptz DEFAULT NOW()
);
```

## Metrics & Evaluation

### Online Metrics
- **Swipe-to-Like Ratio**: Percentage of shown items that get liked
- **Order Conversion Rate**: Percentage of likes that lead to orders
- **Session Engagement**: Time spent, items viewed per session
- **Position Bias**: Click-through rate by position in swipe deck

### Offline Metrics
- **NDCG@10**: Normalized Discounted Cumulative Gain for ranking quality
- **Coverage**: Percentage of items that get shown to users
- **Diversity**: Average intra-list distance of recommended items
- **Fairness**: Distribution of recommendations across restaurants

### A/B Testing Framework
```typescript
interface ExperimentConfig {
  name: string;
  variants: {
    control: ScoringWeights;
    treatment: ScoringWeights;
  };
  trafficAllocation: number; // 0.1 = 10% of users
  metrics: string[];
  duration: number; // days
}
```

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Zero-shot tag inference is noisy** | Medium | Lower tag weight (0.3→0.2), collect user corrections, expand label set |
| **Embedding semantic mismatch** | High | Test with domain-specific models, add cross-encoder re-ranking |
| **Cold start for new users** | Medium | Higher weight on content features, ask onboarding questions |
| **Search latency > 500ms** | High | Precompute embeddings, optimize vector indexes, cache frequent queries |
| **Position bias in feedback** | Medium | Log position, randomize order occasionally, debias in training |

## Hackathon Timeline (48-72 hours)

### Day 1: Foundation (8 hours)
- **Hours 1-2**: Set up Supabase with pgvector, import restaurant data
- **Hours 3-4**: Generate embeddings for all menu items
- **Hours 5-6**: Implement basic search endpoint with filtering
- **Hours 7-8**: Update frontend to consume real API

### Day 2: Intelligence (8 hours)
- **Hours 1-3**: Implement zero-shot tag classifier
- **Hours 4-5**: Build weighted scoring function
- **Hours 6-7**: Add explanation/reasoning to recommendations
- **Hours 8**: Test and tune initial weights

### Day 3: Polish & Demo (8 hours)
- **Hours 1-2**: Implement feedback logging
- **Hours 3-4**: Add performance optimizations
- **Hours 5-6**: Create demo data and user flows
- **Hours 7-8**: Prepare presentation and metrics

### Demo Features
1. **Live Search**: "Find high-protein lunch under $15 near me"
2. **Explainable Results**: Show why each item was recommended
3. **Real Data**: 2,000+ NYC restaurants with real menus
4. **Smart Filtering**: Location, diet, budget, hours constraints
5. **Learning Ready**: Feedback logging for future ML improvements

## Success Criteria

### Technical
- [ ] Sub-500ms search response time
- [ ] 95%+ uptime during demo
- [ ] Accurate location-based filtering
- [ ] Meaningful recommendation explanations

### Product
- [ ] Intuitive swipe interface
- [ ] Relevant recommendations for test queries
- [ ] Smooth user onboarding flow
- [ ] Clear value proposition demo

### Future Scalability
- [ ] ML pipeline ready for production
- [ ] Feedback loop implemented
- [ ] A/B testing framework sketched
- [ ] Performance monitoring in place

This recommendation engine leverages cutting-edge ML techniques while being practical for a hackathon timeline, using your comprehensive restaurant dataset to deliver personalized, explainable food recommendations.
