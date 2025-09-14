import React, { useState, useRef } from 'react';
import { motion, PanInfo, useMotionValue, useTransform } from 'motion/react';
import { MapPin, DollarSign, Clock, RotateCcw, Star, Zap, Flame } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface Restaurant {
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
}

interface SwipeCardProps {
  restaurant: Restaurant;
  onSwipe: (direction: 'left' | 'right', restaurant: Restaurant) => void;
  userPreferences: any;
  onDoubleClick?: () => void;
}

export function SwipeCard({ restaurant, onSwipe, userPreferences, onDoubleClick }: SwipeCardProps) {
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
      onSwipe(direction, restaurant);
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
      } else if (clickCount === 1 && onDoubleClick) {
        // Double click - open order details
        onDoubleClick();
      }
      setClickCount(0);
    }, 250);
  };

  // Determine what info to show based on user preferences
  const getHighlightInfo = () => {
    const info = [];
    
    if (userPreferences?.showMacros && restaurant.protein) {
      info.push(`${restaurant.protein}g protein`);
    }
    if (userPreferences?.showCalories && restaurant.calories) {
      info.push(`${restaurant.calories} cal`);
    }
    if (userPreferences?.showWaitTime && restaurant.waitTime) {
      info.push(`${restaurant.waitTime} wait`);
    }
    if (userPreferences?.showDietary && restaurant.dietary?.length) {
      info.push(restaurant.dietary[0]);
    }
    
    // Always show top highlights if we don't have enough preference-based info
    const remaining = 3 - info.length;
    if (remaining > 0) {
      info.push(...restaurant.highlights.slice(0, remaining));
    }
    
    return info.slice(0, 3);
  };

  const renderFrontCard = () => (
    <Card className="overflow-hidden shadow-lg cursor-pointer" onClick={handleCardClick}>
      <div className="relative h-64">
        <ImageWithFallback
          src={restaurant.image}
          alt={restaurant.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-4 right-4">
          <Badge variant="secondary" className="bg-black/70 text-white">
            ⭐ {restaurant.rating}
          </Badge>
        </div>
        <div className="absolute top-4 left-4">
          <Badge variant="secondary" className="bg-black/50 text-white text-xs">
            <RotateCcw className="w-3 h-3 mr-1" />
            Tap for details
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
            <h3>{restaurant.name}</h3>
            <p className="text-sm text-muted-foreground">{restaurant.cuisine}</p>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-1 text-muted-foreground">
              <MapPin className="w-4 h-4" />
              {restaurant.distance}
            </div>
            <div className="flex items-center gap-1 text-muted-foreground">
              <DollarSign className="w-4 h-4" />
              {restaurant.price}
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
          <h3>{restaurant.name}</h3>
          <Badge variant="outline">
            <RotateCcw className="w-3 h-3 mr-1" />
            Flip back
          </Badge>
        </div>
        
        <div className="space-y-4 flex-1">
          {/* Key Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4 text-yellow-500" />
                <span className="text-sm">{restaurant.rating} rating</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-blue-500" />
                <span className="text-sm">{restaurant.distance}</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-green-500" />
                <span className="text-sm">{restaurant.price}</span>
              </div>
              {restaurant.waitTime && (
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-orange-500" />
                  <span className="text-sm">{restaurant.waitTime}</span>
                </div>
              )}
            </div>
          </div>

          {/* Nutrition Info */}
          {(restaurant.calories || restaurant.protein || restaurant.carbs || restaurant.fat) && (
            <div className="border-t pt-4">
              <h4 className="mb-3 flex items-center gap-2">
                <Flame className="w-4 h-4 text-red-500" />
                Nutrition per serving
              </h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {restaurant.calories && (
                  <div>
                    <span className="text-muted-foreground">Calories</span>
                    <p className="font-medium">{restaurant.calories}</p>
                  </div>
                )}
                {restaurant.protein && (
                  <div>
                    <span className="text-muted-foreground">Protein</span>
                    <p className="font-medium">{restaurant.protein}g</p>
                  </div>
                )}
                {restaurant.carbs && (
                  <div>
                    <span className="text-muted-foreground">Carbs</span>
                    <p className="font-medium">{restaurant.carbs}g</p>
                  </div>
                )}
                {restaurant.fat && (
                  <div>
                    <span className="text-muted-foreground">Fat</span>
                    <p className="font-medium">{restaurant.fat}g</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Dietary Info */}
          {restaurant.dietary && restaurant.dietary.length > 0 && (
            <div className="border-t pt-4">
              <h4 className="mb-3 flex items-center gap-2">
                <Zap className="w-4 h-4 text-purple-500" />
                Dietary
              </h4>
              <div className="flex flex-wrap gap-2">
                {restaurant.dietary.map((diet, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {diet}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Highlights */}
          <div className="border-t pt-4">
            <h4 className="mb-3">Why you'll love it</h4>
            <div className="space-y-1">
              {restaurant.highlights.map((highlight, index) => (
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