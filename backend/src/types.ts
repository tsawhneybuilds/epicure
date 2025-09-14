export interface BackendRestaurant {
  id: string;
  name: string;
  lat: number;
  lng: number;
  address?: string;
  phone?: string;
  yelp?: {
    rating?: number;
    price?: string;
  };
  google_rating?: number;
}

export interface BackendMenuItem {
  id: string;
  restaurantId: string;
  menuId: string;
  section: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  tags?: string[];
  allergens?: string[];
  confidence?: number;
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
}

export interface FrontendRestaurant {
  id: string;
  name: string;
  cuisine: string;
  image: string;
  distance: string;
  price: string;
  rating: number;
  waitTime?: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
  dietary?: string[];
  highlights: string[];
  address?: string;
  phone?: string;
}

export interface RecommendationRequest {
  query: string;
  location: { lat: number; lng: number };
  preferences: any;
  userProfile: any;
  limit?: number;
}

export interface RecommendationResponse {
  restaurants: FrontendRestaurant[];
  total: number;
  sessionId: string;
  explanations: Record<string, any>;
}
