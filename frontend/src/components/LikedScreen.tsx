import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { MapPin, DollarSign, Star, Navigation, ShoppingBag, Phone, Clock, ExternalLink } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';

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
  address?: string;
  phone?: string;
}

interface LikedScreenProps {
  likedRestaurants: Restaurant[];
  onRemoveLiked: (restaurantId: string) => void;
}

export function LikedScreen({ likedRestaurants, onRemoveLiked }: LikedScreenProps) {
  const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);

  const handleGetDirections = (restaurant: Restaurant) => {
    // Simulate opening Google Maps
    const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(restaurant.name)}`;
    window.open(mapsUrl, '_blank');
  };

  const handleOrderUberEats = (restaurant: Restaurant) => {
    // Simulate opening UberEats (would normally use deep linking)
    const uberEatsUrl = `https://www.ubereats.com/search?q=${encodeURIComponent(restaurant.name)}`;
    window.open(uberEatsUrl, '_blank');
  };

  const handleOrderDoorDash = (restaurant: Restaurant) => {
    // Simulate opening DoorDash (would normally use deep linking)
    const doorDashUrl = `https://www.doordash.com/search/?query=${encodeURIComponent(restaurant.name)}`;
    window.open(doorDashUrl, '_blank');
  };

  const handleCall = (restaurant: Restaurant) => {
    if (restaurant.phone) {
      window.open(`tel:${restaurant.phone}`, '_self');
    }
  };

  const simulateHealthTracking = (restaurant: Restaurant) => {
    // Simulate adding to Apple Health
    if (restaurant.calories) {
      // This would normally use HealthKit integration
      console.log(`Adding ${restaurant.calories} calories to Apple Health`);
      
      // Show a toast notification
      const event = new CustomEvent('show-toast', {
        detail: {
          title: 'Added to Health App',
          description: `${restaurant.calories} calories logged automatically`
        }
      });
      window.dispatchEvent(event);
    }
  };

  if (likedRestaurants.length === 0) {
    return (
      <div className="flex flex-col h-full">
        <div className="p-4 border-b">
          <h2>Your Liked Restaurants</h2>
          <p className="text-sm text-muted-foreground">
            0 restaurants you want to try
          </p>
        </div>
        
        <ScrollArea className="flex-1">
          <div className="flex flex-col items-center justify-center h-full p-8">
            <Card className="p-6 text-center max-w-md">
              <CardContent className="space-y-4">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto">
                  ❤️
                </div>
                <h3>No liked restaurants yet</h3>
                <p className="text-muted-foreground">
                  Start swiping right on restaurants you're interested in to see them here!
                </p>
              </CardContent>
            </Card>
          </div>
        </ScrollArea>
      </div>
    );
  }

  if (selectedRestaurant) {
    return (
      <div className="flex flex-col h-full">
        <div className="p-4 border-b flex items-center gap-4">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setSelectedRestaurant(null)}
          >
            ← Back
          </Button>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-4 space-y-6">
            {/* Header Image */}
            <div className="relative h-48 rounded-lg overflow-hidden">
              <ImageWithFallback
                src={selectedRestaurant.image}
                alt={selectedRestaurant.name}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 right-4">
                <Badge variant="secondary" className="bg-black/70 text-white">
                  ⭐ {selectedRestaurant.rating}
                </Badge>
              </div>
            </div>

            {/* Restaurant Info */}
            <div className="space-y-4">
              <div>
                <h2>{selectedRestaurant.name}</h2>
                <p className="text-muted-foreground">{selectedRestaurant.cuisine}</p>
              </div>

              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {selectedRestaurant.distance}
                </div>
                <div className="flex items-center gap-1">
                  <DollarSign className="w-4 h-4" />
                  {selectedRestaurant.price}
                </div>
                {selectedRestaurant.waitTime && (
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {selectedRestaurant.waitTime}
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <Button 
                onClick={() => handleGetDirections(selectedRestaurant)}
                className="flex items-center gap-2"
              >
                <Navigation className="w-4 h-4" />
                Directions
              </Button>
              <Button 
                variant="outline"
                onClick={() => handleCall(selectedRestaurant)}
                className="flex items-center gap-2"
              >
                <Phone className="w-4 h-4" />
                Call
              </Button>
            </div>

            <div className="space-y-2">
              <Button 
                onClick={() => handleOrderUberEats(selectedRestaurant)}
                className="w-full flex items-center gap-2 bg-black text-white hover:bg-gray-800"
              >
                <ShoppingBag className="w-4 h-4" />
                Order on Uber Eats
              </Button>
              <Button 
                onClick={() => handleOrderDoorDash(selectedRestaurant)}
                className="w-full flex items-center gap-2 bg-red-600 text-white hover:bg-red-700"
              >
                <ShoppingBag className="w-4 h-4" />
                Order on DoorDash
              </Button>
            </div>

            {/* Nutrition Info */}
            {(selectedRestaurant.calories || selectedRestaurant.protein) && (
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4>Nutrition Information</h4>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => simulateHealthTracking(selectedRestaurant)}
                    >
                      + Add to Health
                    </Button>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {selectedRestaurant.calories && (
                      <div>
                        <span className="text-muted-foreground">Calories</span>
                        <p className="font-medium">{selectedRestaurant.calories}</p>
                      </div>
                    )}
                    {selectedRestaurant.protein && (
                      <div>
                        <span className="text-muted-foreground">Protein</span>
                        <p className="font-medium">{selectedRestaurant.protein}g</p>
                      </div>
                    )}
                    {selectedRestaurant.carbs && (
                      <div>
                        <span className="text-muted-foreground">Carbs</span>
                        <p className="font-medium">{selectedRestaurant.carbs}g</p>
                      </div>
                    )}
                    {selectedRestaurant.fat && (
                      <div>
                        <span className="text-muted-foreground">Fat</span>
                        <p className="font-medium">{selectedRestaurant.fat}g</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Dietary Tags */}
            {selectedRestaurant.dietary && selectedRestaurant.dietary.length > 0 && (
              <div>
                <h4 className="mb-2">Dietary Options</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedRestaurant.dietary.map((diet, index) => (
                    <Badge key={index} variant="secondary">
                      {diet}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Highlights */}
            <div>
              <h4 className="mb-2">Highlights</h4>
              <div className="space-y-1">
                {selectedRestaurant.highlights.map((highlight, index) => (
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
                onRemoveLiked(selectedRestaurant.id);
                setSelectedRestaurant(null);
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
        <h2>Your Liked Restaurants</h2>
        <p className="text-sm text-muted-foreground">
          {likedRestaurants.length} restaurants you want to try
        </p>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {likedRestaurants.map((restaurant) => (
            <Card 
              key={restaurant.id} 
              className="overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => setSelectedRestaurant(restaurant)}
            >
              <div className="flex">
                <div className="w-24 h-24 flex-shrink-0">
                  <ImageWithFallback
                    src={restaurant.image}
                    alt={restaurant.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <CardContent className="flex-1 p-4">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium">{restaurant.name}</h4>
                        <p className="text-sm text-muted-foreground">{restaurant.cuisine}</p>
                      </div>
                      <ExternalLink className="w-4 h-4 text-muted-foreground" />
                    </div>
                    
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3" />
                        {restaurant.rating}
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {restaurant.distance}
                      </div>
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-3 h-3" />
                        {restaurant.price}
                      </div>
                    </div>

                    {restaurant.calories && (
                      <div className="text-xs text-muted-foreground">
                        {restaurant.calories} cal
                        {restaurant.protein && ` • ${restaurant.protein}g protein`}
                      </div>
                    )}
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