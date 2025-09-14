"""
Menu Item Service - Handles menu item search, filtering, and recommendations
"""
import json
import time
import struct
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.menu_item import (
    MenuItem, 
    MenuItemSearchRequest, 
    MenuItemSearchResponse,
    RestaurantInfo,
    MenuItemInteraction
)
from ..core.config import settings


class MenuItemService:
    """Service for menu item operations"""
    
    def __init__(self):
        self.use_mock_data = settings.MOCK_DATA
    
    def _extract_coordinates_from_postgis(self, postgis_hex: str) -> Optional[Dict[str, float]]:
        """
        Extract lat/lng coordinates from PostGIS geometry hex string
        PostGIS stores coordinates in WKB (Well-Known Binary) format
        """
        if not postgis_hex:
            return None
        
        try:
            # Remove the '0101000020E6100000' prefix (SRID and geometry type)
            # and decode the hex string
            hex_data = postgis_hex[18:]  # Remove the prefix
            binary_data = bytes.fromhex(hex_data)
            
            # Parse the binary data to get coordinates
            # PostGIS stores coordinates as double precision (8 bytes each)
            if len(binary_data) >= 16:  # Need at least 16 bytes for lat/lng
                # Unpack as little-endian doubles
                lng, lat = struct.unpack('<dd', binary_data[:16])
                return {"lat": lat, "lng": lng}
        except Exception as e:
            print(f"Failed to parse PostGIS coordinates: {e}")
        
        return None
        
    async def search_menu_items(self, request: MenuItemSearchRequest) -> MenuItemSearchResponse:
        """
        Search for menu items based on query, filters, and personalization
        """
        start_time = time.time()
        
        if self.use_mock_data:
            menu_items = await self._get_mock_menu_items(request)
        else:
            menu_items = await self._search_supabase_menu_items(request)
        
        # Apply filters
        filtered_items = self._apply_filters(menu_items, request.filters)
        
        # Apply personalization and ranking
        ranked_items = await self._apply_personalization(filtered_items, request.personalization)
        
        # Apply sorting and pagination
        sorted_items = self._apply_sorting(ranked_items, request.sort_by, request.sort_order)
        paginated_items = sorted_items[request.offset:request.offset + request.limit]
        
        # Generate metadata
        search_time_ms = int((time.time() - start_time) * 1000)
        meta = self._generate_search_meta(
            total_results=len(filtered_items),
            search_time_ms=search_time_ms,
            request=request,
            filtered_count=len(filtered_items)
        )
        
        return MenuItemSearchResponse(
            menu_items=paginated_items,
            meta=meta
        )
    
    async def get_menu_item_by_id(self, menu_item_id: str) -> Optional[MenuItem]:
        """Get a specific menu item by ID"""
        if self.use_mock_data:
            mock_items = await self._get_mock_menu_items(MenuItemSearchRequest(
                location={"lat": 40.7580, "lng": -73.9855}
            ))
            return next((item for item in mock_items if item.id == menu_item_id), None)
        else:
            return await self._get_supabase_menu_item(menu_item_id)
    
    async def record_interaction(self, interaction: MenuItemInteraction) -> bool:
        """Record user interaction with a menu item"""
        if self.use_mock_data:
            print(f"🎯 Mock: Recorded {interaction.action} for menu item {interaction.menu_item_id} by user {interaction.user_id}")
            return True
        else:
            return await self._record_supabase_interaction(interaction)
    
    async def get_user_liked_items(self, user_id: str) -> List[MenuItem]:
        """Get menu items liked by a user"""
        if self.use_mock_data:
            # Return a subset of mock items as "liked"
            mock_items = await self._get_mock_menu_items(MenuItemSearchRequest(
                location={"lat": 40.7580, "lng": -73.9855}
            ))
            return mock_items[:3]  # Return first 3 as liked items
        else:
            return await self._get_supabase_liked_items(user_id)
    
    def _apply_filters(self, menu_items: List[MenuItem], filters: Dict[str, Any]) -> List[MenuItem]:
        """Apply filters to menu items list"""
        if not filters:
            return menu_items
        
        filtered = menu_items
        
        # Nutrition filters
        if max_calories := filters.get('max_calories'):
            filtered = [item for item in filtered if item.calories <= max_calories]
        
        if min_protein := filters.get('min_protein'):
            filtered = [item for item in filtered if item.protein >= min_protein]
        
        if max_price := filters.get('max_price'):
            filtered = [item for item in filtered if item.price <= max_price]
        
        # Dietary restrictions
        if dietary_restrictions := filters.get('dietary_restrictions'):
            filtered = [
                item for item in filtered 
                if any(diet.lower() in [d.lower() for d in item.dietary] for diet in dietary_restrictions)
            ]
        
        # Categories
        if categories := filters.get('categories'):
            filtered = [
                item for item in filtered 
                if item.category.lower() in [c.lower() for c in categories]
            ]
        
        # Allergen-free
        if allergen_free := filters.get('allergen_free'):
            filtered = [
                item for item in filtered
                if not any(allergen.lower() in [a.lower() for a in item.allergens] for allergen in allergen_free)
            ]
        
        return filtered
    
    async def _apply_personalization(self, menu_items: List[MenuItem], personalization: Dict[str, Any]) -> List[MenuItem]:
        """Apply personalization and scoring to menu items"""
        if not personalization:
            return menu_items
        
        # For mock data, just return items as-is with some basic scoring logic
        user_preferences = personalization.get('preferences', {})
        context = personalization.get('context', '')
        
        # Simple mock personalization logic
        for item in menu_items:
            base_score = item.restaurant.rating / 5.0  # Normalize rating to 0-1
            
            # Boost based on dietary preferences
            if user_preferences.get('dietary') == 'vegetarian' and 'vegetarian' in [d.lower() for d in item.dietary]:
                base_score += 0.2
            
            # Boost based on context
            if context == 'post_workout' and item.protein >= 25:
                base_score += 0.3
            
            # Store score for sorting (we'll add this to the model later)
            item.popularity_score = min(base_score, 1.0)
        
        return menu_items
    
    def _apply_sorting(self, menu_items: List[MenuItem], sort_by: str, sort_order: str) -> List[MenuItem]:
        """Apply sorting to menu items"""
        reverse = sort_order == "desc"
        
        if sort_by == "price":
            return sorted(menu_items, key=lambda x: x.price, reverse=reverse)
        elif sort_by == "calories":
            return sorted(menu_items, key=lambda x: x.calories, reverse=reverse)
        elif sort_by == "protein":
            return sorted(menu_items, key=lambda x: x.protein, reverse=reverse)
        elif sort_by == "rating":
            return sorted(menu_items, key=lambda x: x.restaurant.rating, reverse=reverse)
        else:  # relevance
            return sorted(menu_items, key=lambda x: x.popularity_score or 0.5, reverse=reverse)
    
    def _generate_search_meta(self, total_results: int, search_time_ms: int, request: MenuItemSearchRequest, filtered_count: int) -> Dict[str, Any]:
        """Generate search metadata"""
        filters_applied = []
        if request.filters:
            if 'max_calories' in request.filters:
                filters_applied.append(f"max_calories: {request.filters['max_calories']}")
            if 'min_protein' in request.filters:
                filters_applied.append(f"min_protein: {request.filters['min_protein']}g")
            if 'dietary_restrictions' in request.filters:
                filters_applied.append(f"dietary: {', '.join(request.filters['dietary_restrictions'])}")
        
        # Generate personalization reason
        reason = "Showing popular menu items in your area"
        if request.personalization:
            context = request.personalization.get('context', '')
            if context == 'post_workout':
                reason = "High-protein options perfect for post-workout recovery"
            elif request.query and 'healthy' in request.query.lower():
                reason = "Healthy menu items with balanced nutrition"
            elif request.filters and 'dietary_restrictions' in request.filters:
                dietary = request.filters['dietary_restrictions'][0]
                reason = f"Great {dietary} options you'll love"
        
        return {
            "total_results": total_results,
            "search_time_ms": search_time_ms,
            "personalization_score": 0.85,  # Mock score
            "filters_applied": filters_applied,
            "recommendations_reason": reason,
            "mock_data": self.use_mock_data
        }
    
    async def _get_mock_menu_items(self, request: MenuItemSearchRequest) -> List[MenuItem]:
        """Generate mock menu items for testing"""
        
        return [
            MenuItem(
                id="item-1",
                name="Protein Power Bowl",
                description="Quinoa bowl with grilled chicken, roasted vegetables, avocado, and tahini dressing",
                image="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400",
                restaurant=RestaurantInfo(
                    id="rest-1",
                    name="Green Fuel Kitchen",
                    cuisine="Healthy Bowls",
                    distance="0.3 mi",
                    rating=4.8,
                    price_range="$$",
                    address="123 Health St, NYC",
                    lat=40.758,
                    lng=-73.9855,
                    phone="(555) 123-4567"
                ),
                price=14.99,
                calories=520,
                protein=35.0,
                carbs=42.0,
                fat=18.0,
                fiber=8.0,
                sugar=6.0,
                sodium=650.0,
                dietary=["High Protein", "Gluten Free"],
                ingredients=["quinoa", "chicken breast", "avocado", "bell peppers", "tahini"],
                allergens=["sesame"],
                highlights=["35g protein", "Complete meal", "Post-workout friendly"],
                category="bowls",
                preparation_time="12 min",
                is_popular=True,
                cuisine_tags=["healthy", "mediterranean"],
                meal_time=["lunch", "post-workout"]
            ),
            
            MenuItem(
                id="item-2", 
                name="Vegan Buddha Bowl",
                description="Colorful bowl with tempeh, roasted sweet potato, kale, edamame, and miso dressing",
                image="https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400",
                restaurant=RestaurantInfo(
                    id="rest-2",
                    name="Plant Paradise",
                    cuisine="Vegan",
                    distance="0.5 mi", 
                    rating=4.6,
                    price_range="$$",
                    address="456 Green Ave, NYC",
                    lat=40.6782,
                    lng=-73.9442,
                    phone="(555) 234-5678"
                ),
                price=12.99,
                calories=380,
                protein=18.0,
                carbs=52.0,
                fat=12.0,
                fiber=12.0,
                sugar=14.0,
                sodium=420.0,
                dietary=["Vegan", "Organic", "Gluten Free"],
                ingredients=["tempeh", "sweet potato", "kale", "edamame", "miso"],
                allergens=["soy"],
                highlights=["Plant-based protein", "Antioxidant rich", "Organic ingredients"],
                category="bowls",
                preparation_time="10 min",
                is_popular=True,
                cuisine_tags=["vegan", "asian-fusion"],
                meal_time=["lunch", "dinner"]
            ),
            
            MenuItem(
                id="item-3",
                name="Classic Margherita Pizza",
                description="Wood-fired pizza with fresh mozzarella, basil, and San Marzano tomato sauce",
                image="https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400",
                restaurant=RestaurantInfo(
                    id="rest-3",
                    name="Nonna's Kitchen",
                    cuisine="Italian",
                    distance="0.7 mi",
                    rating=4.7,
                    price_range="$$",
                    address="789 Little Italy St, NYC",
                    lat=40.7282,
                    lng=-73.7949, 
                    phone="(555) 345-6789"
                ),
                price=16.99,
                calories=680,
                protein=28.0,
                carbs=78.0,
                fat=24.0,
                fiber=4.0,
                sugar=8.0,
                sodium=1200.0,
                dietary=["Vegetarian"],
                ingredients=["mozzarella", "basil", "tomato sauce", "pizza dough", "olive oil"],
                allergens=["gluten", "dairy"],
                highlights=["Wood-fired", "Fresh mozzarella", "Traditional recipe"],
                category="pizza",
                preparation_time="15 min",
                is_popular=True,
                cuisine_tags=["italian", "comfort"],
                meal_time=["lunch", "dinner"]
            ),
            
            MenuItem(
                id="item-4",
                name="Acai Power Smoothie Bowl",
                description="Thick acai smoothie topped with granola, fresh berries, coconut, and honey",
                image="https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400",
                restaurant=RestaurantInfo(
                    id="rest-4",
                    name="Sunrise Smoothies",
                    cuisine="Healthy Cafe",
                    distance="0.4 mi",
                    rating=4.5,
                    price_range="$",
                    address="321 Wellness Blvd, NYC",
                    lat=40.7505,
                    lng=-73.9934,
                    phone="(555) 456-7890"
                ),
                price=9.99,
                calories=320,
                protein=12.0,
                carbs=48.0,
                fat=10.0,
                fiber=8.0,
                sugar=28.0,
                sodium=85.0,
                dietary=["Vegetarian", "Antioxidant Rich"],
                ingredients=["acai", "banana", "granola", "blueberries", "coconut flakes"],
                allergens=["nuts"],
                highlights=["Antioxidant superfood", "Natural energy", "Refreshing"],
                category="breakfast",
                preparation_time="5 min",
                is_popular=False,
                cuisine_tags=["healthy", "tropical"],
                meal_time=["breakfast", "pre-workout"]
            ),
            
            MenuItem(
                id="item-5",
                name="Spicy Korean Bibimbap",
                description="Mixed rice bowl with seasoned vegetables, beef bulgogi, fried egg, and gochujang",
                image="https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=400",
                restaurant=RestaurantInfo(
                    id="rest-5",
                    name="Seoul Kitchen", 
                    cuisine="Korean",
                    distance="0.8 mi",
                    rating=4.4,
                    price_range="$$",
                    address="654 K-Town Ave, NYC",
                    lat=40.7614,
                    lng=-73.9776,
                    phone="(555) 567-8901"
                ),
                price=15.99,
                calories=620,
                protein=32.0,
                carbs=68.0,
                fat=22.0,
                fiber=6.0,
                sugar=12.0,
                sodium=980.0,
                dietary=["High Protein", "Spicy"],
                ingredients=["beef bulgogi", "rice", "spinach", "carrots", "egg", "gochujang"],
                allergens=["gluten", "soy", "egg"],
                highlights=["Korean BBQ flavor", "Complete meal", "Probiotic vegetables"],
                category="bowls",
                preparation_time="18 min", 
                is_popular=True,
                cuisine_tags=["korean", "spicy", "comfort"],
                spice_level="medium",
                meal_time=["lunch", "dinner"]
            ),
            
            MenuItem(
                id="item-6",
                name="Truffle Mushroom Risotto",
                description="Creamy arborio rice with wild mushrooms, truffle oil, and parmesan cheese",
                image="https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=400",
                restaurant=RestaurantInfo(
                    id="rest-6",
                    name="Bella Vista",
                    cuisine="Italian",
                    distance="0.6 mi",
                    rating=4.9,
                    price_range="$$$",
                    address="321 Little Italy, NYC",
                    lat=40.7505,
                    lng=-73.9934,
                    phone="(555) 678-9012"
                ),
                price=22.99,
                calories=580,
                protein=18.0,
                carbs=72.0,
                fat=24.0,
                fiber=3.0,
                sugar=4.0,
                sodium=890.0,
                dietary=["Vegetarian", "Gluten Free"],
                ingredients=["arborio rice", "wild mushrooms", "truffle oil", "parmesan", "vegetable stock"],
                allergens=["dairy"],
                highlights=["Truffle infused", "Creamy texture", "Gourmet experience"],
                category="pasta",
                preparation_time="25 min",
                is_popular=True,
                cuisine_tags=["italian", "gourmet", "comfort"],
                spice_level="mild",
                meal_time=["dinner"]
            ),
            
            MenuItem(
                id="item-7",
                name="Avocado Toast Deluxe",
                description="Sourdough toast with smashed avocado, cherry tomatoes, hemp seeds, and balsamic glaze",
                image="https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?w=400",
                restaurant=RestaurantInfo(
                    id="rest-7",
                    name="Morning Glory Cafe",
                    cuisine="Breakfast",
                    distance="0.2 mi",
                    rating=4.3,
                    price_range="$",
                    address="789 Brunch St, NYC",
                    lat=40.7614,
                    lng=-73.9776,
                    phone="(555) 789-0123"
                ),
                price=8.99,
                calories=320,
                protein=12.0,
                carbs=28.0,
                fat=18.0,
                fiber=8.0,
                sugar=6.0,
                sodium=420.0,
                dietary=["Vegetarian", "Healthy"],
                ingredients=["sourdough bread", "avocado", "cherry tomatoes", "hemp seeds", "balsamic"],
                allergens=["gluten"],
                highlights=["Healthy fats", "Fresh ingredients", "Instagram worthy"],
                category="breakfast",
                preparation_time="8 min",
                is_popular=False,
                cuisine_tags=["healthy", "brunch", "instagram"],
                spice_level="mild",
                meal_time=["breakfast", "brunch"]
            ),
            
            MenuItem(
                id="item-8",
                name="Wagyu Beef Burger",
                description="Premium wagyu beef patty with aged cheddar, caramelized onions, and truffle aioli",
                image="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
                restaurant=RestaurantInfo(
                    id="rest-8",
                    name="Burger Palace",
                    cuisine="American",
                    distance="0.9 mi",
                    rating=4.6,
                    price_range="$$",
                    address="456 Meat Ave, NYC",
                    lat=40.7505,
                    lng=-73.9934,
                    phone="(555) 890-1234"
                ),
                price=18.99,
                calories=780,
                protein=45.0,
                carbs=52.0,
                fat=42.0,
                fiber=3.0,
                sugar=8.0,
                sodium=1200.0,
                dietary=["High Protein"],
                ingredients=["wagyu beef", "aged cheddar", "caramelized onions", "truffle aioli", "brioche bun"],
                allergens=["gluten", "dairy", "egg"],
                highlights=["Premium wagyu", "Gourmet toppings", "Juicy patty"],
                category="sandwiches",
                preparation_time="15 min",
                is_popular=True,
                cuisine_tags=["american", "gourmet", "comfort"],
                spice_level="mild",
                meal_time=["lunch", "dinner"]
            ),
            
            MenuItem(
                id="item-9",
                name="Chocolate Lava Cake",
                description="Warm chocolate cake with molten center, vanilla ice cream, and berry compote",
                image="https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400",
                restaurant=RestaurantInfo(
                    id="rest-9",
                    name="Sweet Dreams Desserts",
                    cuisine="Desserts",
                    distance="0.4 mi",
                    rating=4.7,
                    price_range="$$",
                    address="123 Sugar St, NYC",
                    lat=40.7614,
                    lng=-73.9776,
                    phone="(555) 901-2345"
                ),
                price=12.99,
                calories=480,
                protein=8.0,
                carbs=65.0,
                fat=22.0,
                fiber=4.0,
                sugar=52.0,
                sodium=180.0,
                dietary=["Vegetarian"],
                ingredients=["dark chocolate", "butter", "eggs", "flour", "vanilla ice cream", "berries"],
                allergens=["gluten", "dairy", "egg"],
                highlights=["Molten center", "Rich chocolate", "Perfect temperature"],
                category="desserts",
                preparation_time="12 min",
                is_popular=True,
                cuisine_tags=["dessert", "chocolate", "indulgent"],
                spice_level="mild",
                meal_time=["dessert"]
            ),
            
            MenuItem(
                id="item-10",
                name="Green Goddess Smoothie",
                description="Spinach, kale, mango, banana, and coconut water blend with chia seeds",
                image="https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=400",
                restaurant=RestaurantInfo(
                    id="rest-10",
                    name="Vitality Juice Bar",
                    cuisine="Healthy",
                    distance="0.3 mi",
                    rating=4.2,
                    price_range="$",
                    address="567 Wellness Way, NYC",
                    lat=40.7505,
                    lng=-73.9934,
                    phone="(555) 012-3456"
                ),
                price=7.99,
                calories=180,
                protein=6.0,
                carbs=38.0,
                fat=2.0,
                fiber=8.0,
                sugar=28.0,
                sodium=85.0,
                dietary=["Vegan", "Gluten Free", "Organic"],
                ingredients=["spinach", "kale", "mango", "banana", "coconut water", "chia seeds"],
                allergens=[],
                highlights=["Superfood blend", "Natural energy", "Vitamin packed"],
                category="beverages",
                preparation_time="3 min",
                is_popular=False,
                cuisine_tags=["healthy", "vegan", "smoothie"],
                spice_level="mild",
                meal_time=["breakfast", "snack", "pre-workout"]
            )
        ]
    
    # Supabase integration methods
    async def _search_supabase_menu_items(self, request: MenuItemSearchRequest) -> List[MenuItem]:
        """Search menu items in Supabase database"""
        from ..core.supabase import get_supabase_client
        
        client = get_supabase_client()
        
        try:
            # Build the query
            query = client.table('menu_items').select('''
                id, name, description, price, image_url,
                estimated_calories, estimated_protein_g, estimated_carbs_g, estimated_fat_g,
                estimated_fiber_g, estimated_sugar_g, estimated_sodium_mg,
                inferred_dietary_tags, inferred_cuisine_type, inferred_health_tags,
                inferred_spice_level, inferred_meal_category, inferred_cooking_methods,
                inferred_allergens, tag_confidence, nutrition_confidence,
                restaurant_id,
                restaurants(id, name, cuisine, price_level, rating, address, phone, location)
            ''')
            
            # Apply semantic search and tagging
            if request.query and request.query.strip():
                original_query = request.query.strip()
                translated_query = request.personalization.get('translated_query', '') if request.personalization else ''
                
                # Use semantic search with original query (for embeddings if available)
                # For now, use intelligent keyword matching with original query
                search_terms = original_query.lower()
                
                # If we have specific filters (like min_protein), prioritize those over text search
                has_specific_filters = any([
                    request.filters.get('min_protein'),
                    request.filters.get('max_calories'),
                    request.filters.get('dietary_restrictions'),
                    request.filters.get('max_price')
                ])
                
                if has_specific_filters and any(term in search_terms for term in ['high protein', 'protein', 'low calorie', 'healthy']):
                    # For generic health terms with specific filters, don't apply text search
                    # Let the filters do the work
                    pass
                elif 'pizza' in search_terms:
                    # Pizza-specific search using name first, then meal category
                    query = query.or_('name.ilike.%pizza%,inferred_meal_category.ilike.%pizza%')
                elif 'burger' in search_terms:
                    # Burger-specific search
                    query = query.or_('name.ilike.%burger%,inferred_meal_category.ilike.%burger%')
                elif 'sushi' in search_terms:
                    # Sushi-specific search
                    query = query.or_('name.ilike.%sushi%,inferred_cuisine_type.ilike.%japanese%')
                elif 'chicken' in search_terms:
                    # Chicken search using name and description
                    query = query.or_('name.ilike.%chicken%,description.ilike.%chicken%')
                elif 'salad' in search_terms:
                    # Salad search using name and meal category
                    query = query.or_('name.ilike.%salad%,inferred_meal_category.ilike.%salad%')
                elif 'healthy' in search_terms:
                    # Healthy options using health tags
                    query = query.or_('inferred_health_tags.cs.{"healthy","low-calorie","high-protein"}')
                elif 'vegetarian' in search_terms or 'vegan' in search_terms:
                    # Vegetarian/vegan search using dietary tags
                    query = query.or_('inferred_dietary_tags.cs.{"vegetarian","vegan"}')
                else:
                    # General semantic search using name and description with original query
                    query = query.or_(f'name.ilike.%{search_terms}%,description.ilike.%{search_terms}%')
            
            # Apply filters
            if request.filters:
                if max_calories := request.filters.get('max_calories'):
                    query = query.lte('estimated_calories', max_calories)
                if min_protein := request.filters.get('min_protein'):
                    query = query.gte('estimated_protein_g', min_protein)
                if max_price := request.filters.get('max_price'):
                    query = query.lte('price', max_price)
                if dietary_restrictions := request.filters.get('dietary_restrictions'):
                    # Use overlap operator for array fields
                    query = query.overlaps('inferred_dietary_tags', dietary_restrictions)
                if categories := request.filters.get('categories'):
                    query = query.in_('inferred_meal_category', categories)
                if allergen_free := request.filters.get('allergen_free'):
                    # Exclude items with these allergens
                    for allergen in allergen_free:
                        query = query.not_.contains('inferred_allergens', [allergen])
            
            # Prioritize items with nutrition data (when not using mock data)
            if not self.use_mock_data:
                # Filter to items that have meaningful nutrition data (not null and not zero)
                query = query.not_.is_('estimated_calories', 'null').gt('estimated_calories', 0)
            
            # Apply sorting
            if request.sort_by == "price":
                query = query.order('price', desc=(request.sort_order == "desc"))
            elif request.sort_by == "calories":
                query = query.order('estimated_calories', desc=(request.sort_order == "desc"))
            elif request.sort_by == "protein":
                query = query.order('estimated_protein_g', desc=(request.sort_order == "desc"))
            elif request.sort_by == "rating":
                query = query.order('restaurants.rating', desc=(request.sort_order == "desc"))
            else:  # relevance - prioritize items with nutrition data
                # Order by nutrition confidence (items with data will have higher confidence)
                query = query.order('nutrition_confidence', desc=True)
                # Then by calories for items with data
                query = query.order('estimated_calories', desc=True)
            
            # Apply pagination
            query = query.range(request.offset, request.offset + request.limit - 1)
            
            # Execute query
            response = query.execute()
            
            # Deduplicate items by name and restaurant before conversion
            seen_items = set()
            unique_items_data = []
            
            for item_data in response.data:
                # Create a unique key based on name and restaurant
                restaurant_name = item_data.get('restaurants', {}).get('name', '') if item_data.get('restaurants') else ''
                unique_key = f"{item_data.get('name', '')}|{restaurant_name}"
                
                if unique_key not in seen_items:
                    seen_items.add(unique_key)
                    unique_items_data.append(item_data)
            
            print(f"Deduplication: {len(response.data)} items -> {len(unique_items_data)} unique items")
            
            # Convert to MenuItem objects
            menu_items = []
            for item_data in unique_items_data:
                menu_item = self._convert_supabase_to_menu_item(item_data)
                if menu_item:
                    menu_items.append(menu_item)
            
            return menu_items
            
        except Exception as e:
            print(f"❌ Supabase search error: {e}")
            # Fallback to mock data if Supabase fails
            return await self._get_mock_menu_items(request)
    
    def _convert_supabase_to_menu_item(self, item_data: dict) -> Optional[MenuItem]:
        """Convert Supabase menu item data to MenuItem model"""
        try:
            # Extract restaurant data
            restaurant_data = item_data.get('restaurants', {})
            
            # Map price level to price range
            price_level = restaurant_data.get('price_level', 2)
            price_range_map = {1: '$', 2: '$$', 3: '$$$', 4: '$$$$'}
            price_range = price_range_map.get(price_level, '$$')
            
            # Extract coordinates from PostGIS location field
            location_data = self._extract_coordinates_from_postgis(restaurant_data.get('location'))
            lat = location_data.get('lat') if location_data else None
            lng = location_data.get('lng') if location_data else None
            
            # Create restaurant info
            restaurant_info = RestaurantInfo(
                id=restaurant_data.get('id', ''),
                name=restaurant_data.get('name', 'Unknown Restaurant'),
                cuisine=restaurant_data.get('cuisine', 'Unknown'),
                distance="0.5 mi",  # TODO: Calculate actual distance
                rating=float(restaurant_data.get('rating', 4.0)) if restaurant_data.get('rating') is not None else 4.0,
                price_range=price_range,
                address=restaurant_data.get('address'),
                phone=restaurant_data.get('phone'),
                lat=lat,
                lng=lng
            )
            
            # Create menu item
            menu_item = MenuItem(
                id=item_data.get('id', ''),
                name=item_data.get('name', ''),
                description=item_data.get('description') or '',
                image=item_data.get('image_url') or 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
                restaurant=restaurant_info,
                price=float(item_data.get('price', 0)) if item_data.get('price') is not None else 0.0,
                calories=int(item_data.get('estimated_calories', 0)) if item_data.get('estimated_calories') is not None else 0,
                protein=float(item_data.get('estimated_protein_g', 0)) if item_data.get('estimated_protein_g') is not None else 0,
                carbs=float(item_data.get('estimated_carbs_g', 0)) if item_data.get('estimated_carbs_g') is not None else 0,
                fat=float(item_data.get('estimated_fat_g', 0)) if item_data.get('estimated_fat_g') is not None else 0,
                fiber=float(item_data.get('estimated_fiber_g')) if item_data.get('estimated_fiber_g') is not None else None,
                sugar=float(item_data.get('estimated_sugar_g')) if item_data.get('estimated_sugar_g') is not None else None,
                sodium=float(item_data.get('estimated_sodium_mg')) if item_data.get('estimated_sodium_mg') is not None else None,
                dietary=item_data.get('inferred_dietary_tags') or [],
                ingredients=[],  # TODO: Add ingredients if available
                allergens=item_data.get('inferred_allergens') or [],
                highlights=item_data.get('inferred_health_tags') or [],
                category=item_data.get('inferred_meal_category') or 'general',
                preparation_time=None,  # TODO: Add if available
                is_popular=(item_data.get('tag_confidence', 0) or 0) > 0.8,
                cuisine_tags=[item_data.get('inferred_cuisine_type', '')] if item_data.get('inferred_cuisine_type') else [],
                spice_level=item_data.get('inferred_spice_level'),
                meal_time=[item_data.get('inferred_meal_category', '')] if item_data.get('inferred_meal_category') else []
            )
            
            return menu_item
            
        except Exception as e:
            print(f"❌ Error converting menu item: {e}")
            return None

    async def _get_supabase_menu_item(self, menu_item_id: str) -> Optional[MenuItem]:
        """Get menu item from Supabase by ID"""
        from ..core.supabase import get_supabase_client
        
        client = get_supabase_client()
        
        try:
            response = client.table('menu_items').select('''
                id, name, description, price, image_url,
                estimated_calories, estimated_protein_g, estimated_carbs_g, estimated_fat_g,
                estimated_fiber_g, estimated_sugar_g, estimated_sodium_mg,
                inferred_dietary_tags, inferred_cuisine_type, inferred_health_tags,
                inferred_spice_level, inferred_meal_category, inferred_cooking_methods,
                inferred_allergens, tag_confidence, nutrition_confidence,
                restaurant_id,
                restaurants(id, name, cuisine, price_level, rating, address, phone, location)
            ''').eq('id', menu_item_id).execute()
            
            if response.data:
                return self._convert_supabase_to_menu_item(response.data[0])
            return None
            
        except Exception as e:
            print(f"❌ Error getting menu item: {e}")
            return None
    
    async def _record_supabase_interaction(self, interaction: MenuItemInteraction) -> bool:
        """Record interaction in Supabase"""
        from ..core.supabase import get_supabase_client
        
        client = get_supabase_client()
        
        try:
            # For now, just log the interaction
            # TODO: Create user_interactions table in Supabase
            print(f"📊 Recording interaction: {interaction.action} for menu item {interaction.menu_item_id} by user {interaction.user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error recording interaction: {e}")
            return False
    
    async def _get_supabase_liked_items(self, user_id: str) -> List[MenuItem]:
        """Get liked items from Supabase"""
        from ..core.supabase import get_supabase_client
        
        client = get_supabase_client()
        
        try:
            # For now, return a subset of menu items as "liked"
            # TODO: Create user_likes table in Supabase
            request = MenuItemSearchRequest(
                location={"lat": 40.7580, "lng": -73.9855}
            )
            all_items = await self._search_supabase_menu_items(request)
            return all_items[:3]  # Return first 3 as liked items
            
        except Exception as e:
            print(f"❌ Error getting liked items: {e}")
            return []


# Global service instance
menu_item_service = MenuItemService()
