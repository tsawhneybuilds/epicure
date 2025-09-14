# Epicure Frontend-Backend Integration Analysis

## 🔍 Critical Integration Issues & Solutions

After deep analysis of the frontend code and backend/recommendation engine plans, I've identified several critical integration points that need careful attention for seamless operation.

## 📊 Data Structure Mismatches

### Issue 1: Frontend Restaurant Interface vs Backend Data

**Frontend Expects:**
```typescript
interface Restaurant {
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
  address?: string;      // LikedScreen only
  phone?: string;        // LikedScreen only
}
```

**Backend Data Structure (venues_enriched.jsonl):**
```json
{
  "id": "uuid",
  "name": "Restaurant Name",
  "lat": 40.7208901,
  "lng": -74.0003925,
  "website": "url",
  "phone": "phone",
  "google_rating": null,
  "google_hours": null,
  "yelp": {"rating": null, "price": null}
}
```

**Menu Items (menu_items.csv):**
```
id,menu_id,section,name,description,price,currency,tags,allergens,confidence,last_seen
```

### 🔧 Solution: Data Transformation Layer

Create a data transformation service that maps backend data to frontend expectations:

```typescript
// backend/src/services/DataTransformService.ts
interface BackendRestaurant {
  id: string;
  name: string;
  lat: number;
  lng: number;
  website?: string;
  phone?: string;
  google_rating?: number;
  google_hours?: any;
  yelp: {
    rating?: number;
    price?: string;
  };
}

interface BackendMenuItem {
  id: string;
  menu_id: string;
  section: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  tags: string;
  allergens: string;
  confidence: number;
}

class DataTransformService {
  transformRestaurant(
    restaurant: BackendRestaurant, 
    menuItems: BackendMenuItem[],
    userLocation: {lat: number, lng: number}
  ): FrontendRestaurant {
    return {
      id: restaurant.id,
      name: restaurant.name,
      cuisine: this.inferCuisine(restaurant.name, menuItems),
      image: this.getRestaurantImage(restaurant),
      distance: this.calculateDistance(restaurant, userLocation),
      price: this.normalizePriceLevel(restaurant.yelp.price, menuItems),
      rating: restaurant.google_rating || restaurant.yelp.rating || 4.0,
      waitTime: this.estimateWaitTime(restaurant),
      calories: this.getAverageCalories(menuItems),
      protein: this.getAverageProtein(menuItems),
      carbs: this.getAverageCarbs(menuItems),
      fat: this.getAverageFat(menuItems),
      dietary: this.extractDietaryFlags(menuItems),
      highlights: this.generateHighlights(restaurant, menuItems),
      address: this.formatAddress(restaurant),
      phone: restaurant.phone
    };
  }

  private inferCuisine(name: string, menuItems: BackendMenuItem[]): string {
    // Use menu item names/descriptions to infer cuisine type
    const cuisineKeywords = {
      'Italian': ['pizza', 'pasta', 'risotto', 'prosciutto'],
      'Asian': ['sushi', 'ramen', 'kimchi', 'pad thai'],
      'Mexican': ['taco', 'burrito', 'quesadilla', 'salsa'],
      'American': ['burger', 'fries', 'sandwich', 'wings'],
      'French': ['croissant', 'baguette', 'fromage', 'wine'],
      'Mediterranean': ['hummus', 'falafel', 'pita', 'olive'],
      'Indian': ['curry', 'naan', 'tandoori', 'masala']
    };
    
    // Score each cuisine based on menu items
    // Return highest scoring cuisine or 'Contemporary' as default
  }

  private calculateDistance(
    restaurant: BackendRestaurant, 
    userLocation: {lat: number, lng: number}
  ): string {
    const distance = this.haversineDistance(
      userLocation.lat, userLocation.lng,
      restaurant.lat, restaurant.lng
    );
    return distance < 1 ? `${Math.round(distance * 5280)}ft` : `${distance.toFixed(1)}mi`;
  }

  private normalizePriceLevel(
    yelpPrice?: string, 
    menuItems: BackendMenuItem[]
  ): string {
    if (yelpPrice) return yelpPrice;
    
    // Calculate average price from menu items
    const avgPrice = menuItems.reduce((sum, item) => sum + item.price, 0) / menuItems.length;
    
    if (avgPrice < 15) return '$';
    if (avgPrice < 30) return '$$';
    if (avgPrice < 50) return '$$$';
    return '$$$$';
  }

  private generateHighlights(
    restaurant: BackendRestaurant, 
    menuItems: BackendMenuItem[]
  ): string[] {
    const highlights = [];
    
    if (restaurant.google_rating && restaurant.google_rating > 4.5) {
      highlights.push('Highly rated');
    }
    
    if (menuItems.some(item => item.allergens.includes('vegan'))) {
      highlights.push('Vegan options');
    }
    
    if (menuItems.some(item => item.allergens.includes('gluten-free'))) {
      highlights.push('Gluten-free');
    }
    
    const avgPrice = menuItems.reduce((sum, item) => sum + item.price, 0) / menuItems.length;
    if (avgPrice < 20) {
      highlights.push('Budget-friendly');
    }
    
    return highlights.slice(0, 3);
  }
}
```

## 🔄 User Preference Mapping

### Issue 2: Frontend Preferences vs Recommendation Engine

**Frontend Preferences (from ChatModal/VoiceModal):**
```typescript
{
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
```

**Recommendation Engine Expects:**
```typescript
{
  userId: string;
  query: string;
  goals: string[];
  location: {lat: number, lng: number};
  filters: {
    maxPrice?: number;
    maxDistance?: number;
    dietary?: string[];
    allergens?: string[];
  };
}
```

### 🔧 Solution: Preference Translation Service

```typescript
// backend/src/services/PreferenceTranslationService.ts
class PreferenceTranslationService {
  translateFrontendPreferences(
    frontendPrefs: any,
    userProfile: any,
    query: string
  ): RecommendationRequest {
    return {
      userId: userProfile.id,
      query: this.buildQueryString(frontendPrefs, query),
      goals: this.extractGoals(frontendPrefs, userProfile),
      location: userProfile.currentLocation,
      filters: this.buildFilters(frontendPrefs, userProfile)
    };
  }

  private buildQueryString(prefs: any, originalQuery: string): string {
    let queryParts = [originalQuery];
    
    if (prefs.mealTime) queryParts.push(prefs.mealTime);
    if (prefs.cuisinePreference) queryParts.push(prefs.cuisinePreference);
    if (prefs.quickService) queryParts.push('quick service');
    if (prefs.budgetFriendly) queryParts.push('affordable');
    
    return queryParts.filter(Boolean).join(' ');
  }

  private extractGoals(prefs: any, userProfile: any): string[] {
    const goals = [...(userProfile.goals || [])];
    
    if (prefs.trackMacros) goals.push('track_macros');
    if (prefs.dietary === 'vegetarian') goals.push('vegetarian');
    if (prefs.dietary === 'vegan') goals.push('vegan');
    if (prefs.budgetFriendly) goals.push('budget_conscious');
    
    return goals;
  }

  private buildFilters(prefs: any, userProfile: any): SearchFilters {
    return {
      maxPrice: prefs.budgetFriendly ? 25 : userProfile.budget_max,
      maxDistance: prefs.quickService ? 800 : userProfile.preferred_distance_m,
      dietary: this.extractDietaryRestrictions(prefs, userProfile),
      allergens: userProfile.allergens || []
    };
  }
}
```

## 🚀 API Endpoint Modifications

### Issue 3: Frontend expects different API structure

**Current Frontend Mock Data Loading:**
```typescript
const loadRestaurants = () => {
  setIsLoading(true);
  setTimeout(() => {
    let filteredRestaurants = [...MOCK_RESTAURANTS];
    // Filter logic...
    setRestaurants(filteredRestaurants);
    setIsLoading(false);
  }, 500);
};
```

### 🔧 Solution: Update API Endpoints

```typescript
// New API endpoint structure
POST /api/recommendations/search
{
  query: string;
  location: {lat: number, lng: number};
  preferences: FrontendPreferences;
  userProfile: UserProfile;
  limit?: number;
}

Response: {
  restaurants: FrontendRestaurant[];
  total: number;
  sessionId: string;
  explanations: {
    [restaurantId: string]: {
      tags: string[];
      similarity: number;
      reasons: string[];
    }
  };
}
```

**Updated Frontend Service:**
```typescript
// frontend/src/services/api.ts
class ApiService {
  async getRecommendations(
    query: string,
    location: {lat: number, lng: number},
    preferences: any,
    userProfile: any
  ): Promise<{restaurants: Restaurant[], explanations: any}> {
    const response = await fetch('/api/recommendations/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userProfile.token}`
      },
      body: JSON.stringify({
        query,
        location,
        preferences,
        userProfile,
        limit: 50
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch recommendations');
    }
    
    return response.json();
  }

  async recordFeedback(
    restaurantId: string,
    feedbackType: 'like' | 'dislike' | 'order',
    sessionId: string
  ): Promise<void> {
    await fetch('/api/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        restaurantId,
        feedbackType,
        sessionId
      })
    });
  }
}
```

## 🔄 Real-time Location Updates

### Issue 4: Frontend location handling vs backend geospatial queries

**Current Frontend:**
```typescript
const mockLocations = ['Manhattan, NY', 'Brooklyn, NY'];
const randomLocation = mockLocations[Math.floor(Math.random() * mockLocations.length)];
setLocation(randomLocation);
```

### 🔧 Solution: Implement proper geolocation

```typescript
// frontend/src/hooks/useLocation.ts
export const useLocation = () => {
  const [location, setLocation] = useState<{lat: number, lng: number} | null>(null);
  const [address, setAddress] = useState<string>('Getting location...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const coords = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          setLocation(coords);
          
          // Reverse geocode to get address
          const address = await reverseGeocode(coords);
          setAddress(address);
        },
        (error) => {
          console.error('Geolocation error:', error);
          // Fallback to NYC center
          const fallback = { lat: 40.7580, lng: -73.9855 };
          setLocation(fallback);
          setAddress('New York, NY');
          setError('Location access denied - using NYC as default');
        }
      );
    }
  }, []);

  return { location, address, error };
};
```

## 🎯 Authentication Integration

### Issue 5: Frontend mock auth vs backend real auth

**Current Frontend:**
```typescript
const handleLogin = () => {
  // Simulate login - in a real app this would authenticate
  setIsReturningUser(true);
  setUserProfile({...mockProfile});
  setCurrentScreen('home');
};
```

### 🔧 Solution: Implement Supabase Auth

```typescript
// frontend/src/services/auth.ts
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.REACT_APP_SUPABASE_URL!,
  process.env.REACT_APP_SUPABASE_ANON_KEY!
);

export class AuthService {
  async signInWithApple(): Promise<User> {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'apple',
      options: {
        scopes: 'name email'
      }
    });
    
    if (error) throw error;
    return data.user!;
  }

  async signInWithEmail(email: string, password: string): Promise<User> {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });
    
    if (error) throw error;
    return data.user!;
  }

  async signUpWithEmail(email: string, password: string): Promise<User> {
    const { data, error } = await supabase.auth.signUp({
      email,
      password
    });
    
    if (error) throw error;
    return data.user!;
  }

  async getCurrentUser(): Promise<User | null> {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
  }

  async signOut(): Promise<void> {
    await supabase.auth.signOut();
  }
}
```

## 📱 Error Handling & Edge Cases

### Issue 6: Robust error handling across the stack

### 🔧 Solution: Comprehensive error boundaries

```typescript
// frontend/src/components/ErrorBoundary.tsx (enhanced)
export class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null, errorInfo: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    
    // Log to backend analytics
    fetch('/api/errors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      })
    }).catch(() => {}); // Silent fail for error logging
    
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-background">
          <Card className="p-6 max-w-md mx-auto">
            <CardContent className="text-center space-y-4">
              <h2 className="text-xl font-semibold">Something went wrong</h2>
              <p className="text-muted-foreground">
                We're sorry for the inconvenience. The error has been logged and we're working on a fix.
              </p>
              <Button 
                onClick={() => window.location.reload()}
                className="w-full"
              >
                Refresh App
              </Button>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## 🔄 Data Synchronization

### Issue 7: Keeping frontend state in sync with backend

### 🔧 Solution: State management with React Query

```typescript
// frontend/src/hooks/useRecommendations.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useRecommendations = (
  query: string,
  location: {lat: number, lng: number},
  preferences: any,
  userProfile: any
) => {
  return useQuery({
    queryKey: ['recommendations', query, location, preferences],
    queryFn: () => apiService.getRecommendations(query, location, preferences, userProfile),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000)
  });
};

export const useLikeRestaurant = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ restaurantId, sessionId }: { restaurantId: string, sessionId: string }) =>
      apiService.recordFeedback(restaurantId, 'like', sessionId),
    onSuccess: () => {
      // Invalidate and refetch recommendations
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      queryClient.invalidateQueries({ queryKey: ['liked-restaurants'] });
    }
  });
};
```

## 🎯 Performance Optimizations

### Issue 8: Ensuring fast load times and smooth UX

### 🔧 Solution: Multiple optimization strategies

```typescript
// frontend/src/components/SwipeInterface.tsx (optimized)
export function SwipeInterface({ userPreferences, userProfile, onUpdatePreferences, onRestaurantLiked }: SwipeInterfaceProps) {
  const { location } = useLocation();
  const [currentQuery, setCurrentQuery] = useState('');
  
  // Use React Query for data fetching
  const { data, isLoading, error } = useRecommendations(
    currentQuery, 
    location, 
    userPreferences, 
    userProfile
  );
  
  // Preload next batch of recommendations
  const queryClient = useQueryClient();
  useEffect(() => {
    if (currentIndex > restaurants.length - 10) {
      queryClient.prefetchQuery({
        queryKey: ['recommendations', currentQuery + '_next', location, userPreferences],
        queryFn: () => apiService.getRecommendations(
          currentQuery, 
          location, 
          { ...userPreferences, offset: restaurants.length }, 
          userProfile
        )
      });
    }
  }, [currentIndex, restaurants.length]);

  // Optimistic updates for likes
  const likeMutation = useLikeRestaurant();
  const handleSwipe = useCallback((direction: 'left' | 'right', restaurant: Restaurant) => {
    if (direction === 'right') {
      // Optimistic update
      onRestaurantLiked(restaurant);
      
      // Backend update
      likeMutation.mutate({ 
        restaurantId: restaurant.id, 
        sessionId: data?.sessionId 
      });
    }
    
    setCurrentIndex(prev => prev + 1);
  }, [data?.sessionId, likeMutation, onRestaurantLiked]);

  // Memoize expensive operations
  const transformedRestaurants = useMemo(() => 
    data?.restaurants || [],
    [data?.restaurants]
  );

  return (
    <div className="flex flex-col h-full">
      {/* Render logic */}
    </div>
  );
}
```

## 🛠 Development Setup Integration

### Issue 9: Coordinating frontend and backend development

### 🔧 Solution: Docker Compose development environment

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/epicure_dev
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    volumes:
      - ./backend:/app
      - /app/node_modules
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:3001
      - REACT_APP_SUPABASE_URL=${SUPABASE_URL}
      - REACT_APP_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  db:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=epicure_dev
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## ✅ Integration Checklist

### Phase 1: Foundation (Day 1)
- [ ] Set up Supabase with pgvector extension
- [ ] Create data transformation service
- [ ] Import restaurant and menu data
- [ ] Implement basic API endpoints
- [ ] Update frontend to use real API

### Phase 2: Intelligence (Day 2)
- [ ] Implement preference translation service
- [ ] Set up recommendation engine
- [ ] Add ML-powered ranking
- [ ] Implement feedback logging
- [ ] Add error handling

### Phase 3: Polish (Day 3)
- [ ] Implement real authentication
- [ ] Add performance optimizations
- [ ] Set up proper location services
- [ ] Add comprehensive error boundaries
- [ ] Test full user flow

## 🚨 Critical Success Factors

1. **Data Consistency**: Ensure all data transformations preserve semantic meaning
2. **Performance**: Keep API response times under 500ms
3. **Error Recovery**: Graceful degradation when services fail
4. **User Experience**: Seamless transitions between mock and real data
5. **Scalability**: Architecture supports 10x growth in users and data

This integration analysis ensures that the frontend, backend, and recommendation engine work seamlessly together while maintaining the excellent user experience already built into the frontend.
