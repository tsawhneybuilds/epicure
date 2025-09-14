/**
 * API client for Epicure backend - Menu-item focused version
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Types matching the backend MenuItem model
export interface MenuItem {
  id: string;
  name: string;
  description: string;
  image: string;
  restaurant: {
    id: string;
    name: string;
    cuisine: string;
    distance: string;
    rating: number;
    price_range: string; // $, $$, $$$
    address?: string;
    lat?: number;
    lng?: number;
    phone?: string;
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
  allergens: string[];
  highlights: string[];
  category: string;
  preparation_time?: string;
  is_popular?: boolean;
  cuisine_tags?: string[];
  spice_level?: string;
  meal_time?: string[];
}

export interface MenuItemSearchRequest {
  query?: string;
  location: {
    lat: number;
    lng: number;
  };
  filters?: {
    max_calories?: number;
    min_protein?: number;
    max_price?: number;
    dietary_restrictions?: string[];
    categories?: string[];
    allergen_free?: string[];
    max_prep_time?: number;
    spice_level?: string;
    meal_time?: string;
  };
  personalization?: {
    user_id?: string;
    preferences?: any;
    context?: string;
    health_goals?: string[];
  };
  sort_by?: string;
  sort_order?: string;
  limit?: number;
  offset?: number;
}

export interface MenuItemSearchResponse {
  menu_items: MenuItem[];
  meta: {
    total_results: number;
    search_time_ms: number;
    personalization_score: number;
    filters_applied: string[];
    recommendations_reason: string;
    mock_data?: boolean;
  };
}

export interface ConversationalSearchRequest {
  message: string;
  context?: any;
  chat_history?: Array<{role: string, content: string}>;
  user_id?: string;
}

export interface ConversationalSearchResponse {
  ai_response: string;
  suggested_search?: any;
  menu_items: MenuItem[];
  conversation_id: string;
  preferences_extracted: any;
  search_reasoning: string;
}

export interface MenuItemInteraction {
  user_id: string;
  menu_item_id: string;
  action: string; // 'like', 'dislike', 'order', 'save', 'view'
  search_query?: string;
  position?: number;
  conversation_context?: any;
  time_spent_viewing?: number;
  timestamp?: string;
  session_id?: string;
}

class EpicureAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Menu Item Search & Discovery
  async searchMenuItems(request: MenuItemSearchRequest): Promise<MenuItemSearchResponse> {
    console.log('🔍 API: Searching menu items:', request);
    return this.request<MenuItemSearchResponse>('/menu-items/search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getMenuItem(menuItemId: string): Promise<MenuItem> {
    return this.request<MenuItem>(`/menu-items/${menuItemId}`);
  }

  async getUserLikedMenuItems(userId: string): Promise<MenuItem[]> {
    return this.request<MenuItem[]>(`/menu-items/users/${userId}/liked`);
  }

  // Conversational AI Integration
  async conversationalFoodSearch(request: ConversationalSearchRequest): Promise<ConversationalSearchResponse> {
    console.log('💬 API: Conversational search:', request);
    return this.request<ConversationalSearchResponse>('/ai/search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // AI-Powered Recommendation Engine
  async aiRecommendation(request: ConversationalSearchRequest): Promise<ConversationalSearchResponse> {
    console.log('🤖 API: AI Recommendation:', request);
    return this.request<ConversationalSearchResponse>('/ai/recommend', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async refineMenuSearch(refinementData: any): Promise<any> {
    return this.request('/ai/refine-search', {
      method: 'POST',
      body: JSON.stringify(refinementData),
    });
  }

  async explainRecommendation(menuItemId: string, userPreferences: any, searchContext: any): Promise<any> {
    return this.request('/ai/explain-recommendation', {
      method: 'POST',
      body: JSON.stringify({
        menu_item_id: menuItemId,
        user_preferences: userPreferences,
        search_context: searchContext
      }),
    });
  }

  async compareMenuItems(menuItemIds: string[], criteria: string[]): Promise<any> {
    return this.request('/ai/compare-items', {
      method: 'POST',
      body: JSON.stringify({
        menu_item_ids: menuItemIds,
        criteria: criteria
      }),
    });
  }

  // Interaction Tracking
  async recordMenuItemSwipe(interaction: MenuItemInteraction): Promise<any> {
    console.log('📊 API: Recording swipe interaction:', interaction);
    return this.request('/menu-items/interactions/swipe', {
      method: 'POST',
      body: JSON.stringify(interaction),
    });
  }

  // Personalized Recommendations
  async getPersonalizedRecommendations(userData: any): Promise<any> {
    return this.request('/menu-items/recommend', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getTrendingMenuItems(params?: { limit?: number; category?: string; time_period?: string }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.category) queryParams.set('category', params.category);
    if (params?.time_period) queryParams.set('time_period', params.time_period);
    
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return this.request(`/menu-items/trending${query}`);
  }

  // Metadata & Categories
  async getMenuCategories(): Promise<any> {
    return this.request('/menu-items/categories');
  }

  async getDietaryOptions(): Promise<any> {
    return this.request('/menu-items/dietary-options');
  }

  async getMenuItemsStats(): Promise<any> {
    return this.request('/menu-items/stats');
  }

  // Authentication
  async createUser(email?: string, appleId?: string): Promise<any> {
    return this.request('/users/create', {
      method: 'POST',
      body: JSON.stringify({ email, apple_id: appleId }),
    });
  }

  async loginUser(email?: string, appleId?: string): Promise<any> {
    return this.request('/users/login', {
      method: 'POST',
      body: JSON.stringify({ email, apple_id: appleId }),
    });
  }

  // User Management (with authentication)
  async getUserProfile(userId: string, authToken: string): Promise<any> {
    return this.request(`/users/${userId}/profile`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
  }

  async updateUserProfile(userId: string, profileData: any, authToken: string): Promise<any> {
    return this.request(`/users/${userId}/profile`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify(profileData),
    });
  }

  async updateUserPreferences(userId: string, preferences: any, authToken: string): Promise<any> {
    return this.request(`/users/${userId}/preferences`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({ preferences }),
    });
  }

  // Health Data Integration
  async importHealthData(source: string, data: any): Promise<any> {
    return this.request('/health/import', {
      method: 'POST',
      body: JSON.stringify({ source, data }),
    });
  }

  // Chat Messages (for persistent chat history)
  async sendChatMessage(message: string, context?: any): Promise<any> {
    return this.request('/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message, context }),
    });
  }

  // Backend Health Check
  async healthCheck(): Promise<any> {
    return this.request('/health');
  }
}

// Global API instance
export const EpicureAPI = new EpicureAPIClient();

// Default location (Manhattan, NYC)
export const DEFAULT_LOCATION = {
  lat: 40.7580,
  lng: -73.9855
};

// Helper functions for building requests
export const buildMenuSearchRequest = (
  query: string,
  userPreferences: any,
  userLocation: any = DEFAULT_LOCATION,
  context: string = 'general'
): MenuItemSearchRequest => {
  const filters: any = {};
  
  // Map user preferences to filters
  if (userPreferences?.budgetFriendly) {
    filters.max_price = 15;
  }
  
  if (userPreferences?.dietary === 'vegetarian') {
    filters.dietary_restrictions = ['vegetarian'];
  }
  
  if (userPreferences?.healthFocused) {
    filters.max_calories = 600;
    filters.min_protein = 15;
  }
  
  // Context-based adjustments
  if (context === 'post_workout') {
    filters.min_protein = 25;
    filters.max_calories = 700;
  }
  
  return {
    query,
    location: userLocation,
    filters,
    personalization: {
      preferences: userPreferences,
      context
    },
    limit: 20
  };
};

export const buildConversationalRequest = (
  message: string,
  chatHistory: any[],
  userId: string,
  context: any = {}
): ConversationalSearchRequest => {
  return {
    message,
    context: {
      ...context,
      timestamp: new Date().toISOString(),
      location: DEFAULT_LOCATION
    },
    chat_history: chatHistory.map(msg => ({
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.content
    })),
    user_id: userId
  };
};

export default EpicureAPI;
