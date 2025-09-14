/**
 * Integration tests for frontend_new ↔ backend communication
 * Run with: node test_integration.js
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

class IntegrationTester {
  constructor() {
    this.testResults = [];
    this.passedTests = 0;
    this.failedTests = 0;
  }

  async runAllTests() {
    console.log('🧪 Starting Frontend_New ↔ Backend Integration Tests');
    console.log('=' .repeat(60));

    await this.testBackendHealth();
    await this.testMenuItemSearch();
    await this.testConversationalAI();
    await this.testMenuItemInteractions();
    await this.testPersonalizedRecommendations();
    await this.testMetadataEndpoints();

    this.printResults();
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  async test(name, testFn) {
    console.log(`\n🔍 Testing: ${name}`);
    try {
      await testFn();
      console.log(`✅ PASS: ${name}`);
      this.testResults.push({ name, status: 'PASS' });
      this.passedTests++;
    } catch (error) {
      console.log(`❌ FAIL: ${name}`);
      console.log(`   Error: ${error.message}`);
      this.testResults.push({ name, status: 'FAIL', error: error.message });
      this.failedTests++;
    }
  }

  async testBackendHealth() {
    await this.test('Backend Health Check', async () => {
      try {
        const response = await this.request('/health');
        if (response.status !== 'healthy') {
          throw new Error('Backend health check failed');
        }
        console.log('   ℹ️ Backend is running and responding');
      } catch (error) {
        // Health endpoint might not exist, try a simpler test
        const response = await this.request('/menu-items/stats');
        if (response.total_menu_items) {
          console.log('   ℹ️ Backend is responding (via stats endpoint)');
        } else {
          throw error;
        }
      }
    });
  }

  async testMenuItemSearch() {
    await this.test('Menu Item Search API', async () => {
      const searchRequest = {
        query: 'high protein healthy food',
        location: { lat: 40.7580, lng: -73.9855 },
        filters: {
          min_protein: 20,
          max_calories: 600,
          dietary_restrictions: ['vegetarian']
        },
        limit: 5
      };

      const response = await this.request('/menu-items/search', {
        method: 'POST',
        body: JSON.stringify(searchRequest)
      });

      // Validate response structure
      if (!response.menu_items || !Array.isArray(response.menu_items)) {
        throw new Error('Invalid response structure: missing menu_items array');
      }

      if (!response.meta || typeof response.meta !== 'object') {
        throw new Error('Invalid response structure: missing meta object');
      }

      // Validate menu item structure
      if (response.menu_items.length > 0) {
        const item = response.menu_items[0];
        const requiredFields = ['id', 'name', 'description', 'restaurant', 'price', 'calories', 'protein'];
        
        for (const field of requiredFields) {
          if (!(field in item)) {
            throw new Error(`Menu item missing required field: ${field}`);
          }
        }

        // Validate restaurant nested object
        if (!item.restaurant || !item.restaurant.name || !item.restaurant.cuisine) {
          throw new Error('Menu item restaurant info incomplete');
        }

        console.log(`   ℹ️ Found ${response.menu_items.length} menu items`);
        console.log(`   ℹ️ Sample item: ${item.name} (${item.protein}g protein, ${item.calories} cal)`);
        console.log(`   ℹ️ Search reason: ${response.meta.recommendations_reason}`);
      }
    });
  }

  async testConversationalAI() {
    await this.test('Conversational AI Search', async () => {
      const conversationalRequest = {
        message: 'I need something quick and healthy for lunch, preferably high in protein',
        context: {
          location: { lat: 40.7580, lng: -73.9855 },
          meal_context: 'lunch'
        },
        chat_history: [],
        user_id: 'test-user-123'
      };

      const response = await this.request('/ai/search', {
        method: 'POST',
        body: JSON.stringify(conversationalRequest)
      });

      // Validate response structure
      const requiredFields = ['ai_response', 'menu_items', 'conversation_id', 'search_reasoning'];
      for (const field of requiredFields) {
        if (!(field in response)) {
          throw new Error(`Conversational response missing required field: ${field}`);
        }
      }

      if (!Array.isArray(response.menu_items)) {
        throw new Error('menu_items should be an array');
      }

      if (typeof response.ai_response !== 'string' || response.ai_response.length === 0) {
        throw new Error('ai_response should be a non-empty string');
      }

      console.log(`   ℹ️ AI Response: ${response.ai_response.slice(0, 100)}...`);
      console.log(`   ℹ️ Found ${response.menu_items.length} menu items via conversation`);
      console.log(`   ℹ️ Conversation ID: ${response.conversation_id}`);
    });
  }

  async testMenuItemInteractions() {
    await this.test('Menu Item Interaction Recording', async () => {
      const interaction = {
        user_id: 'test-user-123',
        menu_item_id: 'item-1',
        action: 'like',
        search_query: 'high protein lunch',
        position: 1,
        conversation_context: {
          test: true
        },
        timestamp: new Date().toISOString()
      };

      const response = await this.request('/menu-items/interactions/swipe', {
        method: 'POST',
        body: JSON.stringify(interaction)
      });

      if (!response.status || response.status !== 'success') {
        throw new Error('Interaction recording failed');
      }

      console.log(`   ℹ️ Successfully recorded ${interaction.action} interaction`);
    });
  }

  async testPersonalizedRecommendations() {
    await this.test('Personalized Recommendations', async () => {
      const recommendationRequest = {
        user_id: 'test-user-123',
        context: {
          location: { lat: 40.7580, lng: -73.9855 },
          meal_context: 'post_workout'
        },
        preferences: {
          dietary: 'vegetarian',
          health_focused: true,
          budget_friendly: false
        },
        limit: 3
      };

      const response = await this.request('/menu-items/recommend', {
        method: 'POST',
        body: JSON.stringify(recommendationRequest)
      });

      if (!response.recommendations || !Array.isArray(response.recommendations)) {
        throw new Error('Invalid recommendations response');
      }

      if (!response.reasoning || typeof response.reasoning !== 'string') {
        throw new Error('Missing reasoning for recommendations');
      }

      console.log(`   ℹ️ Got ${response.recommendations.length} personalized recommendations`);
      console.log(`   ℹ️ Reasoning: ${response.reasoning}`);
    });
  }

  async testMetadataEndpoints() {
    await this.test('Metadata Endpoints', async () => {
      // Test categories
      const categories = await this.request('/menu-items/categories');
      if (!categories.categories || !Array.isArray(categories.categories)) {
        throw new Error('Invalid categories response');
      }

      // Test dietary options
      const dietaryOptions = await this.request('/menu-items/dietary-options');
      if (!dietaryOptions.dietary_options || !Array.isArray(dietaryOptions.dietary_options)) {
        throw new Error('Invalid dietary options response');
      }

      // Test stats
      const stats = await this.request('/menu-items/stats');
      if (!stats.total_menu_items || typeof stats.total_menu_items !== 'number') {
        throw new Error('Invalid stats response');
      }

      console.log(`   ℹ️ Found ${categories.categories.length} categories`);
      console.log(`   ℹ️ Found ${dietaryOptions.dietary_options.length} dietary options`);
      console.log(`   ℹ️ Total menu items in system: ${stats.total_menu_items}`);
    });
  }

  printResults() {
    console.log('\n' + '=' .repeat(60));
    console.log('🎯 Integration Test Results');
    console.log('=' .repeat(60));
    
    this.testResults.forEach(result => {
      const icon = result.status === 'PASS' ? '✅' : '❌';
      console.log(`${icon} ${result.name}`);
      if (result.error) {
        console.log(`     ${result.error}`);
      }
    });

    console.log('\n📊 Summary:');
    console.log(`   ✅ Passed: ${this.passedTests}`);
    console.log(`   ❌ Failed: ${this.failedTests}`);
    console.log(`   📈 Success Rate: ${Math.round((this.passedTests / (this.passedTests + this.failedTests)) * 100)}%`);

    if (this.failedTests === 0) {
      console.log('\n🎉 All integration tests passed! Frontend_new ↔ Backend integration is working!');
    } else {
      console.log('\n⚠️ Some tests failed. Check the backend connection and API endpoints.');
    }
  }
}

// Check if running in Node.js environment
if (typeof window === 'undefined') {
  // Node.js environment - need to install node-fetch
  console.log('Note: This test requires node-fetch. Install with: npm install node-fetch');
  console.log('For now, run the tests via browser console or update to use a proper test framework.');
} else {
  // Browser environment - run tests
  const tester = new IntegrationTester();
  tester.runAllTests().catch(error => {
    console.error('Test runner failed:', error);
  });
}

// Export for use in other contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = IntegrationTester;
}
