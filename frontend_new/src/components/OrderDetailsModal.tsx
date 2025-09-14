import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { X, MapPin, Phone, ExternalLink, ChefHat, Clock, Utensils } from 'lucide-react';
import { motion } from 'motion/react';

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

interface OrderDetailsModalProps {
  menuItem: MenuItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export function OrderDetailsModal({ menuItem, isOpen, onClose }: OrderDetailsModalProps) {
  if (!isOpen || !menuItem) return null;

  const handleOrderDoorDash = () => {
    // In a real app, this would open DoorDash with the specific menu item
    window.open(`https://doordash.com/search/?query=${encodeURIComponent(menuItem.restaurant.name + ' ' + menuItem.name)}`, '_blank');
  };

  const handleOrderUberEats = () => {
    // In a real app, this would open Uber Eats with the specific menu item
    window.open(`https://ubereats.com/search/?query=${encodeURIComponent(menuItem.restaurant.name + ' ' + menuItem.name)}`, '_blank');
  };

  const handleGetDirections = () => {
    // In a real app, this would open Google Maps with directions to the restaurant
    window.open(`https://maps.google.com/search/${encodeURIComponent(menuItem.restaurant.name)}`, '_blank');
  };

  const handleCallRestaurant = () => {
    // Mock phone number for demo
    window.open('tel:+1-555-0123');
  };

  const simulateHealthTracking = () => {
    // Simulate adding to Apple Health
    console.log(`Adding ${menuItem.calories} calories to Apple Health`);
    
    // Show a toast notification
    const event = new CustomEvent('show-toast', {
      detail: {
        title: 'Added to Health App',
        description: `${menuItem.name}: ${menuItem.calories} calories logged automatically`
      }
    });
    window.dispatchEvent(event);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-background rounded-2xl max-w-md w-full max-h-[80vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="relative">
          <img
            src={menuItem.image}
            alt={menuItem.name}
            className="w-full h-48 object-cover rounded-t-2xl"
          />
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="absolute top-4 right-4 bg-black/20 text-white hover:bg-black/40 rounded-full w-8 h-8 p-0"
          >
            <X className="w-4 h-4" />
          </Button>
          <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-sm rounded-lg px-3 py-1">
            <p className="text-white text-sm font-medium">${menuItem.price} • {menuItem.restaurant.distance}</p>
          </div>
          {menuItem.isPopular && (
            <div className="absolute top-4 left-4">
              <Badge className="bg-orange-500 text-white">
                🔥 Popular
              </Badge>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Menu Item Info */}
          <div>
            <h2 className="text-xl font-medium mb-1">{menuItem.name}</h2>
            <p className="text-muted-foreground mb-2">{menuItem.description}</p>
            
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline">{menuItem.category}</Badge>
              {menuItem.dietary.slice(0, 2).map((diet, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {diet}
                </Badge>
              ))}
            </div>

            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1">
                <ChefHat className="w-4 h-4" />
                {menuItem.restaurant.name}
              </div>
              <span className="text-yellow-600">★ {menuItem.restaurant.rating}</span>
              {menuItem.preparationTime && (
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {menuItem.preparationTime}
                </div>
              )}
            </div>
          </div>

          {/* Nutrition Info */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium">Nutrition Facts</h3>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={simulateHealthTracking}
                >
                  + Add to Health
                </Button>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Calories</p>
                  <p className="font-medium">{menuItem.calories}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Protein</p>
                  <p className="font-medium">{menuItem.protein}g</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Carbs</p>
                  <p className="font-medium">{menuItem.carbs}g</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Fat</p>
                  <p className="font-medium">{menuItem.fat}g</p>
                </div>
                {menuItem.fiber && (
                  <div>
                    <p className="text-muted-foreground">Fiber</p>
                    <p className="font-medium">{menuItem.fiber}g</p>
                  </div>
                )}
                {menuItem.sodium && (
                  <div>
                    <p className="text-muted-foreground">Sodium</p>
                    <p className="font-medium">{menuItem.sodium}mg</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Ingredients */}
          {menuItem.ingredients.length > 0 && (
            <div>
              <h3 className="font-medium mb-3">Key Ingredients</h3>
              <div className="flex flex-wrap gap-2">
                {menuItem.ingredients.slice(0, 8).map((ingredient, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {ingredient}
                  </Badge>
                ))}
                {menuItem.ingredients.length > 8 && (
                  <Badge variant="outline" className="text-xs">
                    +{menuItem.ingredients.length - 8} more
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Order Options */}
          <div className="space-y-3">
            <h3 className="font-medium">Order Options</h3>
            
            <Button
              onClick={handleOrderDoorDash}
              className="w-full h-12 bg-red-600 hover:bg-red-700 text-white rounded-xl"
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              Order on DoorDash
            </Button>
            
            <Button
              onClick={handleOrderUberEats}
              className="w-full h-12 bg-black hover:bg-gray-800 text-white rounded-xl"
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              Order on Uber Eats
            </Button>
          </div>

          {/* Contact Options */}
          <div className="space-y-3">
            <h3 className="font-medium">Restaurant Info</h3>
            
            <div className="grid grid-cols-2 gap-3">
              <Button
                onClick={handleGetDirections}
                variant="outline"
                className="h-12 rounded-xl"
              >
                <MapPin className="w-4 h-4 mr-2" />
                Directions
              </Button>
              
              <Button
                onClick={handleCallRestaurant}
                variant="outline"
                className="h-12 rounded-xl"
              >
                <Phone className="w-4 h-4 mr-2" />
                Call
              </Button>
            </div>
          </div>

          {/* Highlights */}
          {menuItem.highlights.length > 0 && (
            <div>
              <h3 className="font-medium mb-3">Why We Recommend This</h3>
              <div className="space-y-1">
                {menuItem.highlights.map((highlight, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full flex-shrink-0"></div>
                    {highlight}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}