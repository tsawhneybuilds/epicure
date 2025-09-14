import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { MapPin, DollarSign, Star, Navigation, ShoppingBag, Phone, Clock, ExternalLink, ChefHat, Utensils } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';

interface MenuItem {
  id: string;
  name: string;
  description: string;
  image: string;
  restaurant: {
    name: string;
    cuisine: string;
    distance: string;
    rating: number;
    price: string;
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
  highlights: string[];
  category: string;
  preparationTime?: string;
  isPopular?: boolean;
}

interface LikedScreenProps {
  likedMenuItems: MenuItem[];
  onRemoveLiked: (menuItemId: string) => void;
}

export function LikedScreen({ likedMenuItems, onRemoveLiked }: LikedScreenProps) {
  const [selectedMenuItem, setSelectedMenuItem] = useState<MenuItem | null>(null);

  const handleGetDirections = (menuItem: MenuItem) => {
    // Simulate opening Google Maps
    const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(menuItem.restaurant.name)}`;
    window.open(mapsUrl, '_blank');
  };

  const handleOrderUberEats = (menuItem: MenuItem) => {
    // Simulate opening UberEats (would normally use deep linking)
    const uberEatsUrl = `https://www.ubereats.com/search?q=${encodeURIComponent(menuItem.restaurant.name + ' ' + menuItem.name)}`;
    window.open(uberEatsUrl, '_blank');
  };

  const handleOrderDoorDash = (menuItem: MenuItem) => {
    // Simulate opening DoorDash (would normally use deep linking)
    const doorDashUrl = `https://www.doordash.com/search/?query=${encodeURIComponent(menuItem.restaurant.name + ' ' + menuItem.name)}`;
    window.open(doorDashUrl, '_blank');
  };

  const handleCall = (menuItem: MenuItem) => {
    // Generate a mock phone number for demo
    const mockPhone = '+1 (555) 123-4567';
    window.open(`tel:${mockPhone}`, '_self');
  };

  const simulateHealthTracking = (menuItem: MenuItem) => {
    // Simulate adding to Apple Health
    if (menuItem.calories) {
      // This would normally use HealthKit integration
      console.log(`Adding ${menuItem.calories} calories to Apple Health`);
      
      // Show a toast notification
      const event = new CustomEvent('show-toast', {
        detail: {
          title: 'Added to Health App',
          description: `${menuItem.name}: ${menuItem.calories} calories logged automatically`
        }
      });
      window.dispatchEvent(event);
    }
  };

  if (likedMenuItems.length === 0) {
    return (
      <div className="flex flex-col h-full">
        <div className="p-4 border-b">
          <h2>Your Liked Food</h2>
          <p className="text-sm text-muted-foreground">
            0 dishes you want to try
          </p>
        </div>
        
        <ScrollArea className="flex-1">
          <div className="flex flex-col items-center justify-center h-full p-8">
            <Card className="p-6 text-center max-w-md">
              <CardContent className="space-y-4">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto">
                  ❤️
                </div>
                <h3>No liked dishes yet</h3>
                <p className="text-muted-foreground">
                  Start swiping right on food you're interested in to see it here!
                </p>
              </CardContent>
            </Card>
          </div>
        </ScrollArea>
      </div>
    );
  }

  if (selectedMenuItem) {
    return (
      <div className="flex flex-col h-full">
        <div className="p-4 border-b flex items-center gap-4">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setSelectedMenuItem(null)}
          >
            ← Back
          </Button>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-4 space-y-6">
            {/* Header Image */}
            <div className="relative h-48 rounded-lg overflow-hidden">
              <ImageWithFallback
                src={selectedMenuItem.image}
                alt={selectedMenuItem.name}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 right-4">
                <Badge variant="secondary" className="bg-black/70 text-white">
                  ${selectedMenuItem.price}
                </Badge>
              </div>
              {selectedMenuItem.isPopular && (
                <div className="absolute top-4 left-4">
                  <Badge variant="secondary" className="bg-orange-500 text-white">
                    🔥 Popular
                  </Badge>
                </div>
              )}
            </div>

            {/* Food Info */}
            <div className="space-y-4">
              <div>
                <h2>{selectedMenuItem.name}</h2>
                <p className="text-muted-foreground">{selectedMenuItem.description}</p>
              </div>

              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <ChefHat className="w-4 h-4" />
                  {selectedMenuItem.restaurant.name}
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4" />
                  {selectedMenuItem.restaurant.rating}
                </div>
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {selectedMenuItem.restaurant.distance}
                </div>
              </div>

              <div className="flex items-center gap-4 text-sm">
                <Badge variant="outline">{selectedMenuItem.category}</Badge>
                <Badge variant="outline">{selectedMenuItem.restaurant.cuisine}</Badge>
                {selectedMenuItem.preparationTime && (
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {selectedMenuItem.preparationTime}
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <Button 
                onClick={() => handleGetDirections(selectedMenuItem)}
                className="flex items-center gap-2"
              >
                <Navigation className="w-4 h-4" />
                Directions
              </Button>
              <Button 
                variant="outline"
                onClick={() => handleCall(selectedMenuItem)}
                className="flex items-center gap-2"
              >
                <Phone className="w-4 h-4" />
                Call
              </Button>
            </div>

            <div className="space-y-2">
              <Button 
                onClick={() => handleOrderUberEats(selectedMenuItem)}
                className="w-full flex items-center gap-2 bg-black text-white hover:bg-gray-800"
              >
                <ShoppingBag className="w-4 h-4" />
                Order on Uber Eats
              </Button>
              <Button 
                onClick={() => handleOrderDoorDash(selectedMenuItem)}
                className="w-full flex items-center gap-2 bg-red-600 text-white hover:bg-red-700"
              >
                <ShoppingBag className="w-4 h-4" />
                Order on DoorDash
              </Button>
            </div>

            {/* Nutrition Info */}
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4>Nutrition Information</h4>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => simulateHealthTracking(selectedMenuItem)}
                  >
                    + Add to Health
                  </Button>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Calories</span>
                    <p className="font-medium">{selectedMenuItem.calories}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Protein</span>
                    <p className="font-medium">{selectedMenuItem.protein}g</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Carbs</span>
                    <p className="font-medium">{selectedMenuItem.carbs}g</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Fat</span>
                    <p className="font-medium">{selectedMenuItem.fat}g</p>
                  </div>
                  {selectedMenuItem.fiber && (
                    <div>
                      <span className="text-muted-foreground">Fiber</span>
                      <p className="font-medium">{selectedMenuItem.fiber}g</p>
                    </div>
                  )}
                  {selectedMenuItem.sodium && (
                    <div>
                      <span className="text-muted-foreground">Sodium</span>
                      <p className="font-medium">{selectedMenuItem.sodium}mg</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Dietary Tags */}
            {selectedMenuItem.dietary && selectedMenuItem.dietary.length > 0 && (
              <div>
                <h4 className="mb-2">Dietary Options</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedMenuItem.dietary.map((diet, index) => (
                    <Badge key={index} variant="secondary">
                      {diet}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Ingredients */}
            {selectedMenuItem.ingredients && selectedMenuItem.ingredients.length > 0 && (
              <div>
                <h4 className="mb-2">Key Ingredients</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedMenuItem.ingredients.map((ingredient, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {ingredient}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Highlights */}
            <div>
              <h4 className="mb-2">Highlights</h4>
              <div className="space-y-1">
                {selectedMenuItem.highlights.map((highlight, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full flex-shrink-0"></div>
                    {highlight}
                  </div>
                ))}
              </div>
            </div>

            <Button 
              variant="destructive" 
              className="w-full"
              onClick={() => {
                onRemoveLiked(selectedMenuItem.id);
                setSelectedMenuItem(null);
              }}
            >
              Remove from Liked
            </Button>
          </div>
        </ScrollArea>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <h2>Your Liked Food</h2>
        <p className="text-sm text-muted-foreground">
          {likedMenuItems.length} dishes you want to try
        </p>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {likedMenuItems.map((menuItem) => (
            <Card 
              key={menuItem.id} 
              className="overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => setSelectedMenuItem(menuItem)}
            >
              <div className="flex">
                <div className="w-24 h-24 flex-shrink-0">
                  <ImageWithFallback
                    src={menuItem.image}
                    alt={menuItem.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <CardContent className="flex-1 p-4">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium">{menuItem.name}</h4>
                        <p className="text-sm text-muted-foreground">
                          {menuItem.restaurant.name} • {menuItem.restaurant.cuisine}
                        </p>
                      </div>
                      <ExternalLink className="w-4 h-4 text-muted-foreground" />
                    </div>
                    
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-3 h-3" />
                        ${menuItem.price}
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3" />
                        {menuItem.restaurant.rating}
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {menuItem.restaurant.distance}
                      </div>
                    </div>

                    <div className="text-xs text-muted-foreground">
                      {menuItem.calories} cal • {menuItem.protein}g protein
                      {menuItem.dietary.length > 0 && ` • ${menuItem.dietary[0]}`}
                    </div>
                  </div>
                </CardContent>
              </div>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}