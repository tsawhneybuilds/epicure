import React, { useState, useRef } from 'react';
import { motion, PanInfo, useMotionValue, useTransform } from 'motion/react';
import { MapPin, DollarSign, Clock, RotateCcw, Star, Zap, Flame, Utensils, ChefHat, Navigation } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface MenuItem {
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
    price_range: string;
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

interface SwipeCardProps {
  menuItem: MenuItem;
  onSwipe: (direction: 'left' | 'right', menuItem: MenuItem) => void;
  onTap?: () => void;
}

export function SwipeCard({ menuItem, onSwipe, onTap }: SwipeCardProps) {
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null);
  const [isFlipped, setIsFlipped] = useState(false);
  const [clickCount, setClickCount] = useState(0);
  const cardRef = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-25, 25]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);

  const handleDragEnd = (event: any, info: PanInfo) => {
    const threshold = 100;
    const direction = info.offset.x > threshold ? 'right' : info.offset.x < -threshold ? 'left' : null;
    
    if (direction) {
      setExitDirection(direction);
      onSwipe(direction, menuItem);
    }
  };

  const handleCardClick = (e: React.MouseEvent) => {
    // Prevent flip if dragging
    if (Math.abs(x.get()) > 10) return;
    e.stopPropagation();
    
    setClickCount(prev => prev + 1);
    
    setTimeout(() => {
      if (clickCount === 0) {
        // Single click - flip card
        setIsFlipped(!isFlipped);
      } else if (clickCount === 1 && onTap) {
        // Double click - open order details
        onTap();
      }
      setClickCount(0);
    }, 250);
  };

  // Determine what info to show - prioritize nutrition and highlights
  const getHighlightInfo = () => {
    const info = [];
    
    // Always show protein if available
    if (menuItem.protein) {
      info.push(`${menuItem.protein}g protein`);
    }
    
    // Show calories if available
    if (menuItem.calories) {
      info.push(`${menuItem.calories} cal`);
    }
    
    // Show preparation time if available
    if (menuItem.preparation_time) {
      info.push(`${menuItem.preparation_time}`);
    }
    
    // Fill remaining slots with highlights
    const remaining = 3 - info.length;
    if (remaining > 0) {
      info.push(...menuItem.highlights.slice(0, remaining));
    }
    
    return info.slice(0, 3);
  };

  const openDirections = () => {
    const { lat, lng, address } = menuItem.restaurant;
    
    if (lat && lng) {
      // Use precise coordinates for directions
      const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
      window.open(mapsUrl, '_blank');
    } else if (address) {
      // Fallback to address search
      const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
      window.open(mapsUrl, '_blank');
    }
  };

  const renderFrontCard = () => (
    <Card className="overflow-hidden shadow-lg cursor-pointer" onClick={handleCardClick}>
      <div className="relative h-64">
        <ImageWithFallback
          src={menuItem.image}
          alt={menuItem.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-4 right-4">
          <Badge variant="secondary" className="bg-black/70 text-white">
            ${menuItem.price}
          </Badge>
        </div>
        {menuItem.is_popular && (
          <div className="absolute top-4 left-4">
            <Badge variant="secondary" className="bg-orange-500 text-white text-xs">
              🔥 Popular
            </Badge>
          </div>
        )}
        <div className="absolute top-16 left-4">
          <Badge variant="secondary" className="bg-black/50 text-white text-xs">
            <RotateCcw className="w-3 h-3 mr-1" />
            Tap for nutrition
          </Badge>
        </div>
        <div className="absolute bottom-4 left-4 right-4">
          <div className="flex gap-2 flex-wrap">
            {getHighlightInfo().map((highlight, index) => (
              <Badge key={index} variant="secondary" className="bg-white/90 text-black text-xs">
                {highlight}
              </Badge>
            ))}
          </div>
        </div>
      </div>
      
      <CardContent className="p-4">
        <div className="space-y-3">
          <div>
            <h3>{menuItem.name}</h3>
            <p className="text-sm text-muted-foreground">{menuItem.description}</p>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Utensils className="w-4 h-4" />
              {menuItem.restaurant.name}
            </div>
            <div className="flex items-center gap-1 text-muted-foreground">
              <MapPin className="w-4 h-4" />
              {menuItem.restaurant.distance}
            </div>
          </div>
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Star className="w-4 h-4" />
              {menuItem.restaurant.rating} • {menuItem.restaurant.cuisine}
            </div>
            <div className="flex items-center gap-1 text-muted-foreground">
              <Badge variant="outline" className="text-xs">
                {menuItem.category}
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderBackCard = () => (
    <Card className="overflow-hidden shadow-lg cursor-pointer bg-muted/50" onClick={handleCardClick}>
      <CardContent className="p-6 h-full flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h3>{menuItem.name}</h3>
          <Badge variant="outline">
            <RotateCcw className="w-3 h-3 mr-1" />
            Flip back
          </Badge>
        </div>
        
        <div className="space-y-4 flex-1">
          {/* Restaurant Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <ChefHat className="w-4 h-4 text-blue-500" />
                <span className="text-sm">{menuItem.restaurant.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4 text-yellow-500" />
                <span className="text-sm">{menuItem.restaurant.rating} rating</span>
              </div>
            </div>
            <div className="space-y-2">

              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-green-500" />
                <span className="text-sm">{menuItem.restaurant.distance}</span>
              </div>
              {(menuItem.restaurant.lat && menuItem.restaurant.lng) || menuItem.restaurant.address ? (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    openDirections();
                  }}
                  className="flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded-md text-sm hover:bg-blue-600 transition-colors"
                >
                  <Navigation className="w-4 h-4" />
                  Directions
                </button>
              ) : null}

              {menuItem.preparation_time && (
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-orange-500" />
                  <span className="text-sm">{menuItem.preparation_time}</span>
                </div>
              )}
            </div>
          </div>

          {/* Nutrition Info */}
          <div className="border-t pt-4">
            <h4 className="mb-3 flex items-center gap-2">
              <Flame className="w-4 h-4 text-red-500" />
              Nutrition Facts
            </h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-muted-foreground">Calories</span>
                <p className="font-medium">{menuItem.calories}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Protein</span>
                <p className="font-medium">{menuItem.protein}g</p>
              </div>
              <div>
                <span className="text-muted-foreground">Carbs</span>
                <p className="font-medium">{menuItem.carbs}g</p>
              </div>
              <div>
                <span className="text-muted-foreground">Fat</span>
                <p className="font-medium">{menuItem.fat}g</p>
              </div>
              {menuItem.fiber && (
                <div>
                  <span className="text-muted-foreground">Fiber</span>
                  <p className="font-medium">{menuItem.fiber}g</p>
                </div>
              )}
              {menuItem.sodium && (
                <div>
                  <span className="text-muted-foreground">Sodium</span>
                  <p className="font-medium">{menuItem.sodium}mg</p>
                </div>
              )}
            </div>
          </div>

          {/* Dietary Info */}
          {menuItem.dietary && menuItem.dietary.length > 0 && (
            <div className="border-t pt-4">
              <h4 className="mb-3 flex items-center gap-2">
                <Zap className="w-4 h-4 text-purple-500" />
                Dietary Tags
              </h4>
              <div className="flex flex-wrap gap-2">
                {menuItem.dietary.map((diet, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {diet}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Ingredients */}
          {menuItem.ingredients && menuItem.ingredients.length > 0 && (
            <div className="border-t pt-4">
              <h4 className="mb-3">Key Ingredients</h4>
              <div className="flex flex-wrap gap-2">
                {menuItem.ingredients.slice(0, 6).map((ingredient, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {ingredient}
                  </Badge>
                ))}
                {menuItem.ingredients.length > 6 && (
                  <Badge variant="outline" className="text-xs">
                    +{menuItem.ingredients.length - 6} more
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Highlights */}
          <div className="border-t pt-4">
            <h4 className="mb-3">Why you'll love it</h4>
            <div className="space-y-1">
              {menuItem.highlights.map((highlight, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full flex-shrink-0"></div>
                  {highlight}
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="relative w-full h-[600px] flex items-center justify-center">
      <motion.div
        ref={cardRef}
        className="absolute w-full max-w-sm"
        style={{ x, rotate, opacity }}
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        onDragEnd={handleDragEnd}
        animate={exitDirection ? { 
          x: exitDirection === 'right' ? 1000 : -1000,
          opacity: 0,
          transition: { duration: 0.3 }
        } : {}}
      >
        <motion.div
          animate={{ rotateY: isFlipped ? 180 : 0 }}
          transition={{ duration: 0.6 }}
          style={{ transformStyle: "preserve-3d" }}
        >
          <div style={{ backfaceVisibility: "hidden" }}>
            {renderFrontCard()}
          </div>
          <div 
            style={{ 
              backfaceVisibility: "hidden", 
              transform: "rotateY(180deg)",
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0
            }}
          >
            {renderBackCard()}
          </div>
        </motion.div>
      </motion.div>

      {/* Swipe indicators */}
      <motion.div
        className="absolute top-1/2 left-8 transform -translate-y-1/2 px-4 py-2 bg-red-500 text-white rounded-lg opacity-0 pointer-events-none"
        style={{ opacity: useTransform(x, [-100, 0], [1, 0]) }}
      >
        PASS
      </motion.div>
      <motion.div
        className="absolute top-1/2 right-8 transform -translate-y-1/2 px-4 py-2 bg-green-500 text-white rounded-lg opacity-0 pointer-events-none"
        style={{ opacity: useTransform(x, [0, 100], [0, 1]) }}
      >
        LIKE
      </motion.div>
    </div>
  );
}