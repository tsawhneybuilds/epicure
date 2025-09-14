import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { X, MapPin, Phone, ExternalLink } from 'lucide-react';
import { motion } from 'motion/react';

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

interface OrderDetailsModalProps {
  restaurant: Restaurant | null;
  isOpen: boolean;
  onClose: () => void;
}

export function OrderDetailsModal({ restaurant, isOpen, onClose }: OrderDetailsModalProps) {
  if (!isOpen || !restaurant) return null;

  const handleOrderDoorDash = () => {
    // In a real app, this would open DoorDash with the restaurant
    window.open(`https://doordash.com/search/?query=${encodeURIComponent(restaurant.name)}`, '_blank');
  };

  const handleOrderUberEats = () => {
    // In a real app, this would open Uber Eats with the restaurant
    window.open(`https://ubereats.com/search/?query=${encodeURIComponent(restaurant.name)}`, '_blank');
  };

  const handleGetDirections = () => {
    // In a real app, this would open Google Maps with directions
    window.open(`https://maps.google.com/search/${encodeURIComponent(restaurant.name)}`, '_blank');
  };

  const handleCallRestaurant = () => {
    // Mock phone number for demo
    window.open('tel:+1-555-0123');
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
            src={restaurant.image}
            alt={restaurant.name}
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
            <p className="text-white text-sm font-medium">{restaurant.price} • {restaurant.distance}</p>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Restaurant Info */}
          <div>
            <h2 className="text-xl font-medium mb-1">{restaurant.name}</h2>
            <p className="text-muted-foreground">{restaurant.cuisine}</p>
            <div className="flex items-center gap-4 mt-2 text-sm">
              <span className="text-yellow-600">★ {restaurant.rating}</span>
              {restaurant.waitTime && (
                <span className="text-muted-foreground">{restaurant.waitTime}</span>
              )}
            </div>
          </div>

          {/* Nutrition Info */}
          {restaurant.calories && (
            <Card>
              <CardContent className="p-4">
                <h3 className="font-medium mb-3">Nutrition (Recommended Dish)</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Calories</p>
                    <p className="font-medium">{restaurant.calories}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Protein</p>
                    <p className="font-medium">{restaurant.protein}g</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Carbs</p>
                    <p className="font-medium">{restaurant.carbs}g</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Fat</p>
                    <p className="font-medium">{restaurant.fat}g</p>
                  </div>
                </div>
              </CardContent>
            </Card>
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
            <h3 className="font-medium">Contact & Directions</h3>
            
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
          {restaurant.highlights.length > 0 && (
            <div>
              <h3 className="font-medium mb-3">Why We Recommend This</h3>
              <div className="flex flex-wrap gap-2">
                {restaurant.highlights.map((highlight, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-accent text-accent-foreground text-xs rounded-full"
                  >
                    {highlight}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}