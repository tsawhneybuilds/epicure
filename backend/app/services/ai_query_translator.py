"""
AI Query Translator Service
Translates natural language user input into structured parameters for the recommendation engine
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.models.user import ExtractedPreferences
import logging

logger = logging.getLogger(__name__)

class AIQueryTranslator:
    """AI service that translates user natural language into recommendation engine parameters"""
    
    def __init__(self):
        self.use_mock = settings.MOCK_DATA or not settings.GROQ_API_KEY
        
        if not self.use_mock:
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            self.primary_model = "llama-3.1-8b-instant"
            self.fallback_model = "llama-3.1-8b-instant"
            logger.info("AI Query Translator initialized with Groq")
        else:
            logger.info("AI Query Translator initialized with mock data")
    
    async def translate_user_query(
        self, 
        user_message: str, 
        context: Dict[str, Any] = None,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Translate natural language user input into structured recommendation engine parameters
        
        Returns:
        {
            "search_query": "structured query string",
            "filters": {...},
            "personalization": {...},
            "ai_response": "friendly response to user",
            "translation_confidence": 0.95
        }
        """
        
        if self.use_mock:
            return await self._mock_translate_query(user_message, context, chat_history)
        else:
            return await self._real_translate_query(user_message, context, chat_history)
    
    async def _mock_translate_query(
        self, 
        user_message: str, 
        context: Dict[str, Any] = None,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Mock query translation using keyword analysis"""
        
        message_lower = user_message.lower()
        context = context or {}
        
        # Initialize translation result
        translation = {
            "search_query": "",
            "filters": {},
            "personalization": {
                "user_id": context.get("user_id", "demo-user"),
                "context": context.get("meal_context", "general")
            },
            "ai_response": "",
            "translation_confidence": 0.9
        }
        
        # Extract search query components
        query_parts = []
        
        # Protein/fitness related
        if any(word in message_lower for word in ['protein', 'workout', 'gym', 'fitness', 'muscle', 'recovery']):
            query_parts.append("high protein")
            translation["filters"]["min_protein"] = 25
            translation["ai_response"] = "Perfect! I'm searching for high-protein options that align with your fitness goals."
        
        # Dietary restrictions
        dietary_restrictions = []
        if 'vegan' in message_lower:
            dietary_restrictions.append('vegan')
            query_parts.append("vegan")
        if 'vegetarian' in message_lower:
            dietary_restrictions.append('vegetarian')
            query_parts.append("vegetarian")
        if 'gluten' in message_lower:
            dietary_restrictions.append('gluten-free')
            query_parts.append("gluten-free")
        
        if dietary_restrictions:
            translation["filters"]["dietary_restrictions"] = dietary_restrictions
            if not translation["ai_response"]:
                translation["ai_response"] = f"Great! I'm finding delicious {', '.join(dietary_restrictions)} options for you."
        
        # Budget/price related
        if any(word in message_lower for word in ['budget', 'cheap', 'affordable', 'under']):
            if '$' in user_message:
                import re
                price_match = re.search(r'\$(\d+)', user_message)
                if price_match:
                    max_price = float(price_match.group(1))
                    translation["filters"]["max_price"] = max_price
                    query_parts.append(f"under ${max_price}")
            else:
                translation["filters"]["max_price"] = 15
                query_parts.append("budget-friendly")
            
            if not translation["ai_response"]:
                translation["ai_response"] = "I'm finding great value options that don't compromise on quality or taste."
        
        # Speed/urgency
        if any(word in message_lower for word in ['quick', 'fast', 'hurry', 'asap', 'rush']):
            query_parts.append("quick")
            translation["personalization"]["urgency"] = "high"
            if not translation["ai_response"]:
                translation["ai_response"] = "I understand you're in a rush! Finding quick-prep options for you."
        
        # Health/nutrition
        if any(word in message_lower for word in ['healthy', 'clean', 'nutrition', 'low-calorie']):
            query_parts.append("healthy")
            translation["filters"]["max_calories"] = 600
            if not translation["ai_response"]:
                translation["ai_response"] = "I'm curating healthy menu items with balanced nutrition for you."
        
        # Specific food items (prioritize these over general cuisine)
        if 'pizza' in message_lower:
            query_parts.append("pizza")
            translation["ai_response"] = "I'm finding delicious pizza options for you."
        elif 'burger' in message_lower:
            query_parts.append("burger")
            translation["ai_response"] = "I'm finding great burger options for you."
        elif 'sushi' in message_lower:
            query_parts.append("sushi")
            translation["ai_response"] = "I'm finding fresh sushi options for you."
        elif 'salad' in message_lower:
            query_parts.append("salad")
            translation["ai_response"] = "I'm finding healthy salad options for you."
        else:
            # Cuisine types (fallback)
            cuisine_keywords = {
                'italian': ['italian', 'pasta', 'risotto'],
                'asian': ['asian', 'chinese', 'japanese', 'thai', 'ramen'],
                'mexican': ['mexican', 'taco', 'burrito', 'quesadilla'],
                'mediterranean': ['mediterranean', 'greek', 'hummus', 'falafel'],
                'american': ['american', 'sandwich', 'grilled']
            }
            
            for cuisine, keywords in cuisine_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    query_parts.append(cuisine)
                    translation["personalization"]["cuisine_preference"] = cuisine
                if not translation["ai_response"]:
                    translation["ai_response"] = f"I'm finding delicious {cuisine} options for you."
                break
        
        # Popular/trending
        if any(word in message_lower for word in ['popular', 'trending', 'best', 'recommended']):
            query_parts.append("popular")
            translation["personalization"]["sort_by"] = "popularity"
            if not translation["ai_response"]:
                translation["ai_response"] = "I'm showing you the most popular and highly-rated items right now."
        
        # Build final search query
        if query_parts:
            translation["search_query"] = " ".join(query_parts)
        else:
            translation["search_query"] = "recommended for you"
            translation["ai_response"] = "I'm finding some amazing dishes based on your preferences!"
        
        # Add location context
        if context.get("location"):
            translation["personalization"]["location"] = context["location"]
        
        return translation
    
    async def _real_translate_query(
        self, 
        user_message: str, 
        context: Dict[str, Any] = None,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Real AI-powered query translation (when models are available)"""
        
        # For now, fall back to mock implementation
        return await self._mock_translate_query(user_message, context, chat_history)
    
    def get_translation_confidence(self, user_message: str, translation: Dict[str, Any]) -> float:
        """Calculate confidence score for the translation"""
        
        # Simple confidence scoring based on how many parameters were extracted
        confidence_factors = []
        
        if translation.get("filters"):
            confidence_factors.append(0.3)
        
        if translation.get("personalization", {}).get("cuisine_preference"):
            confidence_factors.append(0.2)
        
        if len(translation.get("search_query", "").split()) > 1:
            confidence_factors.append(0.2)
        
        if any(keyword in user_message.lower() for keyword in ['protein', 'vegetarian', 'budget', 'quick', 'healthy']):
            confidence_factors.append(0.3)
        
        return min(sum(confidence_factors), 1.0)
    
    async def validate_translation(self, translation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the translation result"""
        
        # Ensure required fields
        if not translation.get("search_query"):
            translation["search_query"] = "recommended for you"
        
        if not translation.get("ai_response"):
            translation["ai_response"] = "I'm finding some great options for you!"
        
        # Clean filters
        filters = translation.get("filters", {})
        if filters.get("min_protein") and filters["min_protein"] < 0:
            filters["min_protein"] = 25
        
        if filters.get("max_price") and filters["max_price"] < 0:
            filters["max_price"] = 20
        
        if filters.get("max_calories") and filters["max_calories"] < 0:
            filters["max_calories"] = 800
        
        translation["filters"] = filters
        
        # Update confidence
        translation["translation_confidence"] = self.get_translation_confidence(
            translation.get("original_message", ""), 
            translation
        )
        
        return translation
