import React, { useState, useEffect } from 'react';
import { SwipeCard } from './SwipeCard';
import { ChatModal } from './ChatModal';
import { VoiceModal } from './VoiceModal';
import { OrderDetailsModal } from './OrderDetailsModal';
import { InitialPromptInterface } from './InitialPromptInterface';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { RefreshCw, MapPin, MessageCircle, Mic } from 'lucide-react';
import { motion } from 'motion/react';
import { EpicureAPI, MenuItem, buildMenuSearchRequest, buildConversationalRequest, DEFAULT_LOCATION } from '../utils/api';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface SwipeInterfaceProps {
  userPreferences: any;
  userProfile: any;
  onUpdatePreferences: (preferences: any) => void;
  onMenuItemLiked: (menuItem: MenuItem) => void;
  chatHistory: Message[];
  onChatHistoryUpdate: (messages: Message[]) => void;
  hasInitialPrompt: boolean;
  initialPrompt: string;
  onInitialPromptSubmit: (prompt: string) => void;
  onStartNewChat: () => void;
}

// Mock restaurant data
const MOCK_RESTAURANTS: Restaurant[] = [
  {
    id: '1',
    name: 'Green Bowl Kitchen',
    cuisine: 'Healthy Bowls',
    image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
    distance: '0.3 mi',
    price: '$$',
    rating: 4.8,
    waitTime: '15 min',
    calories: 420,
    protein: 28,
    carbs: 35,
    fat: 18,
    dietary: ['Vegetarian', 'Gluten-free'],
    highlights: ['High protein', 'Fresh ingredients', 'Quick service']
  },
  {
    id: '2',
    name: 'Muscle Fuel',
    cuisine: 'Protein-focused',
    image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400',
    distance: '0.5 mi',
    price: '$$$',
    rating: 4.6,
    waitTime: '10 min',
    calories: 580,
    protein: 45,
    carbs: 22,
    fat: 15,
    dietary: ['High protein'],
    highlights: ['45g protein', 'Keto-friendly', 'Post-workout']
  },
  {
    id: '3',
    name: 'Budget Bites',
    cuisine: 'American',
    image: 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400',
    distance: '0.8 mi',
    price: '$',
    rating: 4.2,
    waitTime: '20 min',
    calories: 650,
    protein: 25,
    carbs: 58,
    fat: 28,
    dietary: [],
    highlights: ['Great value', 'Large portions', 'Comfort food']
  },
  {
    id: '4',
    name: 'Zen Garden',
    cuisine: 'Vegan',
    image: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400',
    distance: '1.2 mi',
    price: '$$',
    rating: 4.7,
    waitTime: '25 min',
    calories: 380,
    protein: 18,
    carbs: 42,
    fat: 12,
    dietary: ['Vegan', 'Organic'],
    highlights: ['Plant-based', 'Organic', 'Low calorie']
  },
  {
    id: '5',
    name: 'Quick Bite Express',
    cuisine: 'Fast Casual',
    image: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400',
    distance: '0.2 mi',
    price: '$',
    rating: 4.1,
    waitTime: '5 min',
    calories: 520,
    protein: 22,
    carbs: 48,
    fat: 24,
    dietary: [],
    highlights: ['Super fast', 'Always open', 'Customizable']
  },
  {
    id: '6',
    name: 'Macro Perfect',
    cuisine: 'Meal Prep',
    image: 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400',
    distance: '0.7 mi',
    price: '$$',
    rating: 4.9,
    waitTime: '12 min',
    calories: 450,
    protein: 35,
    carbs: 30,
    fat: 20,
    dietary: ['Macro-tracked'],
    highlights: ['Exact macros', 'Meal prep', 'Portion controlled']
  }
];

export function SwipeInterface({ 
  userPreferences, 
  userProfile, 
  onUpdatePreferences, 
  onMenuItemLiked, 
  chatHistory, 
  onChatHistoryUpdate, 
  hasInitialPrompt, 
  initialPrompt, 
  onInitialPromptSubmit, 
  onStartNewChat 
}: SwipeInterfaceProps) {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);
  const [location, setLocation] = useState<string>('Manhattan, NY');
  const [searchMode, setSearchMode] = useState<'chat' | 'voice'>('chat');
  const [orderDetailsOpen, setOrderDetailsOpen] = useState(false);
  const [selectedMenuItem, setSelectedMenuItem] = useState<MenuItem | null>(null);
  const [searchReason, setSearchReason] = useState<string>('');
  const [conversationActive, setConversationActive] = useState(hasInitialPrompt);

  useEffect(() => {
    loadRestaurants();
  }, []);

  useEffect(() => {
    // Use mock location directly to avoid geolocation timeouts
    const mockLocations = [
      'Manhattan, NY',
      'Brooklyn, NY', 
      'San Francisco, CA',
      'Los Angeles, CA',
      'Chicago, IL',
      'Boston, MA'
    ];
    const randomLocation = mockLocations[Math.floor(Math.random() * mockLocations.length)];
    setLocation(randomLocation);
  }, []);

  const loadRestaurants = () => {
    setIsLoading(true);
    // Simulate API call with filtering based on preferences
    setTimeout(() => {
      try {
        let filteredRestaurants = [...MOCK_RESTAURANTS];
        
        // Filter based on user preferences
        if (userPreferences?.budgetFriendly) {
          filteredRestaurants = filteredRestaurants.filter(r => r.price === '$' || r.price === '$$');
        }
        
        if (userPreferences?.dietary === 'vegetarian') {
          filteredRestaurants = filteredRestaurants.filter(r => 
            r.dietary?.some(d => d.toLowerCase().includes('vegan') || d.toLowerCase().includes('vegetarian'))
          );
        }
        
        if (userPreferences?.quickService) {
          filteredRestaurants = filteredRestaurants.sort((a, b) => {
            const aTime = parseInt(a.waitTime?.split(' ')[0] || '99');
            const bTime = parseInt(b.waitTime?.split(' ')[0] || '99');
            return aTime - bTime;
          });
        }

        // Shuffle for variety
        filteredRestaurants = filteredRestaurants.sort(() => Math.random() - 0.5);
        
        setRestaurants(filteredRestaurants);
        setCurrentIndex(0);
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading restaurants:', error);
        setRestaurants(MOCK_RESTAURANTS);
        setCurrentIndex(0);
        setIsLoading(false);
      }
    }, 500);
  };

  const handleSwipe = (direction: 'left' | 'right', restaurant: Restaurant) => {
    if (direction === 'right') {
      onRestaurantLiked(restaurant);
    }
    
    setTimeout(() => {
      setCurrentIndex(prev => prev + 1);
    }, 300);
  };

  const handleRefresh = () => {
    loadRestaurants();
  };

  const handleOpenSearch = () => {
    // Reset to initial prompt interface for new search
    setHasInitialPrompt(false);
    setInitialPrompt('');
  };

  const handleRestaurantDoubleClick = (restaurant: Restaurant) => {
    setSelectedRestaurant(restaurant);
    setOrderDetailsOpen(true);
  };

  const handleInitialPromptSubmit = (prompt: string) => {
    setInitialPrompt(prompt);
    setHasInitialPrompt(true);
    // Process the prompt and load restaurants
    loadRestaurants();
  };

  const handleInitialVoiceActivate = () => {
    setIsVoiceOpen(true);
  };

  const currentRestaurant = restaurants[currentIndex];

  // Show initial prompt interface if user hasn't submitted a prompt yet
  if (!hasInitialPrompt) {
    return (
      <>
        <InitialPromptInterface 
          onPromptSubmit={handleInitialPromptSubmit}
          onVoiceActivate={handleInitialVoiceActivate}
        />
        
        {/* Voice Modal for initial prompt */}
        <VoiceModal
          isOpen={isVoiceOpen}
          onClose={() => setIsVoiceOpen(false)}
          onUpdatePreferences={(preferences) => {
            onUpdatePreferences(preferences);
            // Simulate voice input providing a prompt
            setInitialPrompt("Voice search activated");
            setHasInitialPrompt(true);
            loadRestaurants();
          }}
        />
      </>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
        <p className="text-muted-foreground">Finding perfect matches based on your request...</p>
      </div>
    );
  }

  if (!currentRestaurant) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 space-y-6">
        <Card className="p-6 text-center max-w-md">
          <CardContent className="space-y-4">
            <h3>No more restaurants!</h3>
            <p className="text-muted-foreground">
              You've seen all available options. Want to see more?
            </p>
            <Button onClick={handleRefresh} className="w-full">
              <RefreshCw className="w-4 h-4 mr-2" />
              Load More Restaurants
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with Location */}
      <div className="p-4 border-b space-y-4">
        <div className="flex items-center justify-between">
          <Button 
            variant="ghost" 
            className="flex items-center gap-2 p-0 h-auto font-normal hover:bg-transparent"
            onClick={() => {
              const newLocation = prompt('Enter your location:', location);
              if (newLocation && newLocation.trim()) {
                setLocation(newLocation.trim());
              }
            }}
          >
            <MapPin className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium">{location}</span>
          </Button>
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>

        {/* Search Box with Voice Toggle */}
        <div className="bg-muted/50 hover:bg-muted/70 transition-colors rounded-2xl border border-border/50">
          <div className="flex items-center">
            <div 
              onClick={handleOpenSearch}
              className="flex-1 flex items-center gap-3 p-4 cursor-pointer"
            >
              <MessageCircle className="w-5 h-5 text-muted-foreground" />
              <span className="text-muted-foreground">
                Start a new search...
              </span>
            </div>
            
            {/* Voice Toggle - Secondary */}
            <div className="px-3 py-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsVoiceOpen(true)}
                className="p-2 h-auto"
                title="Use voice search"
              >
                <Mic className="w-4 h-4 text-muted-foreground" />
              </Button>
            </div>
          </div>
        </div>

        <div>
          <h2>Discover Food</h2>
          <p className="text-sm text-muted-foreground">
            {restaurants.length - currentIndex} restaurants nearby • Based on: "{initialPrompt}"
          </p>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="relative min-h-full">
          <SwipeCard
            key={currentRestaurant.id}
            restaurant={currentRestaurant}
            onSwipe={handleSwipe}
            userPreferences={userPreferences}
            onDoubleClick={() => handleRestaurantDoubleClick(currentRestaurant)}
          />
        </div>
      </ScrollArea>

      {/* Chat Modal */}
      <ChatModal
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        onUpdatePreferences={onUpdatePreferences}
      />

      {/* Voice Modal */}
      <VoiceModal
        isOpen={isVoiceOpen}
        onClose={() => setIsVoiceOpen(false)}
        onUpdatePreferences={onUpdatePreferences}
      />

      {/* Order Details Modal */}
      <OrderDetailsModal
        restaurant={selectedRestaurant}
        isOpen={orderDetailsOpen}
        onClose={() => setOrderDetailsOpen(false)}
      />
    </div>
  );
}