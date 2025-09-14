/**
 * API utilities for connecting to Epicure backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface ApiRestaurant {
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

export interface SearchRequest {
  query?: string;
  location: {
    lat: number;
    lng: number;
  };
  filters?: {
    max_price?: number;
    dietary_restrictions?: string[];
    max_calories?: number;
    min_protein?: number;
  };
  limit?: number;
}

export interface SearchResponse {
  restaurants: ApiRestaurant[];
  meta: {
    total_results: number;
    search_time_ms: number;
    filters_applied: string[];
    personalization_score: number;
    mock_data?: boolean;
  };
}

export class EpicureAPI {
  private static async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  static async searchRestaurants(request: SearchRequest): Promise<SearchResponse> {
    return this.request<SearchResponse>('/restaurants/search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  static async getRestaurantStats() {
    return this.request('/restaurants/stats');
  }

  static async sendChatMessage(message: string, context?: any) {
    return this.request('/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message, context }),
    });
  }

  static async getUserProfile(userId: string) {
    return this.request(`/users/${userId}/profile`);
  }

  static async recordSwipe(userId: string, restaurantId: string, action: string, context?: any) {
    return this.request(`/users/${userId}/interactions/swipe`, {
      method: 'POST',
      body: JSON.stringify({ restaurant_id: restaurantId, action, context }),
    });
  }

  static async getLikedRestaurants(userId: string) {
    return this.request(`/users/${userId}/interactions/liked`);
  }

  static async importHealthData(source: string, data: any) {
    return this.request('/health/import', {
      method: 'POST',
      body: JSON.stringify({ source, data }),
    });
  }
}

// Default location (Manhattan, NYC)
export const DEFAULT_LOCATION = {
  lat: 40.7580,
  lng: -73.9855
};
