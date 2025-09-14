"""
Enhanced AI Service with Tool Calling for Research and Menu Analysis
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from groq import AsyncGroq
from app.core.config import settings
from app.models.user import ExtractedPreferences
from app.services.menu_item_service import MenuItemService
import logging

logger = logging.getLogger(__name__)

class EnhancedAIService:
    """Enhanced AI service with tool calling capabilities for research and analysis"""
    
    def __init__(self):
        self.use_mock = settings.MOCK_DATA or not settings.GROQ_API_KEY
        self.menu_service = MenuItemService()
        
        if not self.use_mock:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            self.primary_model = "llama-3.1-70b-versatile"
            self.fallback_model = "llama-3.1-8b-instant"
            logger.info("Enhanced AI Service initialized with Groq")
        else:
            logger.info("Enhanced AI Service initialized with mock data")
    
    async def enhanced_conversational_search(
        self, 
        message: str, 
        user_id: str, 
        context: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Enhanced conversational search with tool calling capabilities"""
        
        if self.use_mock:
            return await self._mock_enhanced_search(message, user_id, context, chat_history)
        else:
            return await self._real_enhanced_search(message, user_id, context, chat_history)
    
    async def _mock_enhanced_search(
        self, 
        message: str, 
        user_id: str, 
        context: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Mock enhanced search with simulated tool calling"""
        
        # Simulate tool calling for research
        research_results = await self._mock_research_tools(message, context)
        
        # Extract preferences
        preferences = await self._extract_preferences_with_tools(message, context, research_results)
        
        # Search menu items
        menu_items = await self._search_with_enhanced_filters(preferences, context, user_id)
        
        # Generate enhanced response
        ai_response = await self._generate_enhanced_response(message, preferences, menu_items, research_results)
        
        return {
            "ai_response": ai_response,
            "menu_items": menu_items,
            "preferences_extracted": preferences,
            "research_insights": research_results,
            "search_reasoning": f"Found {len(menu_items)} items based on your request and research insights",
            "tools_used": ["menu_research", "preference_analysis", "nutrition_analysis"]
        }
    
    async def _mock_research_tools(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate research tools for menu analysis"""
        
        message_lower = message.lower()
        insights = {
            "nutritional_analysis": {},
            "trending_items": [],
            "dietary_recommendations": [],
            "price_insights": {},
            "restaurant_insights": {}
        }
        
        # Simulate nutritional analysis
        if any(word in message_lower for word in ['protein', 'workout', 'gym', 'fitness']):
            insights["nutritional_analysis"] = {
                "focus": "high_protein",
                "recommended_protein": "25-40g per meal",
                "best_sources": ["grilled chicken", "salmon", "quinoa", "greek yogurt"]
            }
        
        # Simulate trending items
        if any(word in message_lower for word in ['popular', 'trending', 'best']):
            insights["trending_items"] = [
                "Protein Power Bowl",
                "Truffle Mushroom Risotto", 
                "Grilled Salmon",
                "Quinoa Buddha Bowl"
            ]
        
        # Simulate dietary recommendations
        if any(word in message_lower for word in ['vegetarian', 'vegan', 'plant']):
            insights["dietary_recommendations"] = [
                "Focus on complete proteins like quinoa and beans",
                "Include healthy fats from avocados and nuts",
                "Ensure adequate B12 and iron intake"
            ]
        
        # Simulate price insights
        if any(word in message_lower for word in ['budget', 'cheap', 'affordable']):
            insights["price_insights"] = {
                "budget_range": "$10-15",
                "best_value_items": ["Grain Bowls", "Pasta Dishes", "Sandwiches"],
                "splurge_worthy": ["Premium Proteins", "Artisanal Pizzas"]
            }
        
        return insights
    
    async def _extract_preferences_with_tools(
        self, 
        message: str, 
        context: Dict[str, Any], 
        research_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract preferences using research insights"""
        
        message_lower = message.lower()
        preferences = {
            "health_priority": "medium",
            "dietary_restrictions": [],
            "budget": None,
            "urgency": "normal",
            "cuisine_preferences": [],
            "nutrition_goals": []
        }
        
        # Enhanced preference extraction using research insights
        if research_results.get("nutritional_analysis", {}).get("focus") == "high_protein":
            preferences["health_priority"] = "high"
            preferences["nutrition_goals"].append("muscle_gain")
            preferences["min_protein"] = 25
        
        if research_results.get("dietary_recommendations"):
            if "vegetarian" in message_lower:
                preferences["dietary_restrictions"].append("vegetarian")
            if "vegan" in message_lower:
                preferences["dietary_restrictions"].append("vegan")
        
        if research_results.get("price_insights"):
            preferences["max_price"] = 15
            preferences["budget"] = 15
        
        return preferences
    
    async def _search_with_enhanced_filters(
        self, 
        preferences: Dict[str, Any], 
        context: Dict[str, Any], 
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Search menu items with enhanced filtering"""
        
        # Use the existing menu service but with enhanced filtering
        from app.models.menu_item import MenuItemSearchRequest
        
        search_request = MenuItemSearchRequest(
            query="enhanced search",
            location=context.get("location", {"lat": 40.7580, "lng": -73.9855}),
            filters={
                "max_calories": preferences.get("max_calories"),
                "min_protein": preferences.get("min_protein"),
                "max_price": preferences.get("max_price"),
                "dietary_restrictions": preferences.get("dietary_restrictions")
            },
            personalization={
                "user_id": user_id,
                "preferences": preferences,
                "context": context.get("meal_context", "general")
            }
        )
        
        response = await self.menu_service.search_menu_items(search_request)
        return [item.model_dump() for item in response.menu_items]
    
    async def _generate_enhanced_response(
        self, 
        message: str, 
        preferences: Dict[str, Any], 
        menu_items: List[Dict[str, Any]], 
        research_results: Dict[str, Any]
    ) -> str:
        """Generate enhanced AI response with research insights"""
        
        message_lower = message.lower()
        
        # Base response
        if any(word in message_lower for word in ['protein', 'workout', 'gym', 'fitness']):
            protein_insights = research_results.get("nutritional_analysis", {})
            return f"Perfect! I found high-protein options that align with your fitness goals. Based on my research, I'm showing dishes with {protein_insights.get('recommended_protein', '25g+')} protein to fuel your workouts. These items are optimized for muscle recovery and growth."
        
        elif any(word in message_lower for word in ['vegetarian', 'vegan', 'plant']):
            dietary_recs = research_results.get("dietary_recommendations", [])
            return f"Excellent! I'm showing you delicious plant-based options with rich flavors and complete nutrition. My research shows these items provide optimal protein combinations and essential nutrients for a balanced vegetarian diet."
        
        elif any(word in message_lower for word in ['budget', 'cheap', 'affordable']):
            price_insights = research_results.get("price_insights", {})
            return f"I've found great value options that don't compromise on quality or taste. Based on current market analysis, these items offer the best value in the {price_insights.get('budget_range', '$10-15')} range."
        
        elif any(word in message_lower for word in ['popular', 'trending', 'best']):
            trending = research_results.get("trending_items", [])
            return f"Great choice! I'm showing you the most popular and trending items right now. These dishes are highly rated by customers and represent the best of what's currently available in your area."
        
        else:
            return f"I've found some amazing dishes based on your preferences and current research insights! Swipe right on items you love, and I'll learn your taste preferences to show better recommendations."
    
    async def _real_enhanced_search(
        self, 
        message: str, 
        user_id: str, 
        context: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Real enhanced search with actual tool calling (when AI models are available)"""
        
        # This would implement real AI tool calling when models are working
        # For now, fall back to mock implementation
        return await self._mock_enhanced_search(message, user_id, context, chat_history)
    
    # Tool calling methods for research
    async def call_menu_research_tool(self, query: str, location: Dict[str, float]) -> Dict[str, Any]:
        """Tool for researching menu items and trends"""
        # Simulate menu research
        return {
            "trending_items": ["Protein Power Bowl", "Truffle Mushroom Risotto"],
            "popular_cuisines": ["Mediterranean", "Asian Fusion"],
            "price_trends": {"average": 18.50, "range": "$12-25"}
        }
    
    async def call_nutrition_analysis_tool(self, menu_item: str) -> Dict[str, Any]:
        """Tool for analyzing nutrition content"""
        # Simulate nutrition analysis
        return {
            "protein_content": "high" if "protein" in menu_item.lower() else "medium",
            "calorie_density": "moderate",
            "micronutrients": ["iron", "vitamin B12", "omega-3"]
        }
    
    async def call_restaurant_insights_tool(self, restaurant_name: str) -> Dict[str, Any]:
        """Tool for getting restaurant insights"""
        # Simulate restaurant research
        return {
            "rating": 4.5,
            "specialties": ["Fresh ingredients", "Quick service"],
            "price_level": "$$",
            "popular_items": ["Signature bowls", "Artisanal pizzas"]
        }
