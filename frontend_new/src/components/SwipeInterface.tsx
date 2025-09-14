import React, { useState, useEffect } from 'react';
import { SwipeCard } from './SwipeCard';
import { ChatModal } from './ChatModal';
import { VoiceModal } from './VoiceModal';
import { OrderDetailsModal } from './OrderDetailsModal';
import { InitialPromptInterface } from './InitialPromptInterface';
import { LocationModal } from './LocationModal';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Input } from './ui/input';
import { RefreshCw, MapPin, MessageCircle, Mic, Plus } from 'lucide-react';
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

// User ID for API calls (in a real app, this would come from authentication)
const DEMO_USER_ID = 'demo-user-123';

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
  const [orderDetailsOpen, setOrderDetailsOpen] = useState(false);
  const [selectedMenuItem, setSelectedMenuItem] = useState<MenuItem | null>(null);
  const [location, setLocation] = useState<string>('Manhattan, NY');
  const [searchReason, setSearchReason] = useState<string>('');
  const [conversationActive, setConversationActive] = useState(hasInitialPrompt);
  const [lastSearchQuery, setLastSearchQuery] = useState<string>('');
  const [renderKey, setRenderKey] = useState(0);
  const [isLocationModalOpen, setIsLocationModalOpen] = useState(false);
  const [continueConversationInput, setContinueConversationInput] = useState('');

  // Load menu items on component mount and when preferences change
  useEffect(() => {
    console.log('🔍 DEBUG: userPreferences changed, calling loadMenuItems. Current index before:', currentIndex);
    // Don't reset index when preferences change during active session
    loadMenuItems(false);
  }, [userPreferences]);

  // Update conversation state when initial prompt changes
  useEffect(() => {
    console.log('🔍 DEBUG: useEffect triggered - hasInitialPrompt:', hasInitialPrompt, 'initialPrompt:', initialPrompt);
    setConversationActive(hasInitialPrompt);
    if (hasInitialPrompt && initialPrompt) {
      console.log('🔍 DEBUG: Calling handleConversationalSearch from useEffect');
      handleConversationalSearch(initialPrompt);
    }
  }, [hasInitialPrompt, initialPrompt]);

  const loadMenuItems = async (resetIndex: boolean = true) => {
    console.log('🔍 DEBUG: loadMenuItems called, resetIndex:', resetIndex);
    setIsLoading(true);
    
    try {
      let searchRequest;
      
      if (conversationActive && (chatHistory.length > 0 || lastSearchQuery)) {
        // Use conversational search if we have chat history or a search query
        const conversationalRequest = buildConversationalRequest(
          lastSearchQuery || 'show me food recommendations',
          chatHistory,
          DEMO_USER_ID,
          { location: DEFAULT_LOCATION, meal_context: getCurrentMealContext() }
        );
        
        console.log('🤖 Using AI recommendation engine:', conversationalRequest);
        
        const conversationalResponse = await EpicureAPI.aiRecommendation(conversationalRequest);
        
        console.log('🔍 DEBUG: AI recommendation response:', conversationalResponse);
        setMenuItems(conversationalResponse.menu_items);
        setSearchReason(conversationalResponse.search_reasoning);
        
        // Update chat history if AI provided a response
        if (conversationalResponse.ai_response && onChatHistoryUpdate) {
          const newAIMessage: Message = {
            id: Date.now().toString(),
            content: conversationalResponse.ai_response,
            sender: 'ai',
            timestamp: new Date()
          };
          onChatHistoryUpdate([...chatHistory, newAIMessage]);
        }
        
      } else {
        // Use regular menu item search
        console.log('🔍 DEBUG: Using regular search - conversationActive:', conversationActive, 'chatHistory.length:', chatHistory.length, 'lastSearchQuery:', lastSearchQuery);
        searchRequest = buildMenuSearchRequest(
          'recommended for you',
          userPreferences,
          DEFAULT_LOCATION,
          getCurrentMealContext()
        );
        
        console.log('🔍 Using regular search:', searchRequest);
        
        const response = await EpicureAPI.searchMenuItems(searchRequest);
        
        console.log('🔍 DEBUG: Regular search response:', response);
        setMenuItems(response.menu_items);
        setSearchReason(response.meta.recommendations_reason);
      }
      
      // Only reset index if explicitly requested (e.g., new search, not preference updates)
      if (resetIndex) {
        setCurrentIndex(0);
      }
      
    } catch (error) {
      console.error('❌ Failed to load menu items:', error);
      // TODO: Show error state to user
      setMenuItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConversationalSearch = async (message: string) => {
    console.log('🔍 DEBUG: Starting handleConversationalSearch with message:', message);
    setLastSearchQuery(message);
    
    try {
      const conversationalRequest = buildConversationalRequest(
        message,
        chatHistory,
        DEMO_USER_ID,
        { location: DEFAULT_LOCATION, meal_context: getCurrentMealContext() }
      );
      
      console.log('🔍 DEBUG: Built conversational request:', conversationalRequest);
      
      const response = await EpicureAPI.aiRecommendation(conversationalRequest);
      
      console.log('🔍 DEBUG: Received API response:', response);
      console.log('🔍 DEBUG: Menu items count:', response.menu_items?.length);
      console.log('🔍 DEBUG: First menu item:', response.menu_items?.[0]);
      
      // Update menu items with new search results
      setMenuItems(response.menu_items);
      setSearchReason(response.search_reasoning);
      setCurrentIndex(0);
      
      console.log('🔍 DEBUG: State updated - menuItems set to:', response.menu_items?.length, 'items');
      
      // Update chat history
      const userMessage: Message = {
        id: Date.now().toString(),
        content: message,
        sender: 'user',
        timestamp: new Date()
      };
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.ai_response,
        sender: 'ai',
        timestamp: new Date()
      };
      
      const newChatHistory = [...chatHistory, userMessage, aiMessage];
      onChatHistoryUpdate(newChatHistory);
      
    } catch (error) {
      console.error('❌ Conversational search failed:', error);
    }
  };

  const handleSwipe = async (direction: 'left' | 'right', menuItem: MenuItem) => {
    const action = direction === 'right' ? 'like' : 'dislike';
    
    // Record interaction with backend
    try {
      await EpicureAPI.recordMenuItemSwipe({
        user_id: DEMO_USER_ID,
        menu_item_id: menuItem.id,
        action: action,
        search_query: lastSearchQuery,
        position: currentIndex,
        conversation_context: conversationActive ? { 
          chat_history: chatHistory,
          initial_prompt: initialPrompt 
        } : undefined,
        timestamp: new Date().toISOString()
      });
      
      console.log(`📊 Recorded ${action} for ${menuItem.name}`);
    } catch (error) {
      console.error('Failed to record swipe:', error);
      // Continue with UI - don't block user interaction
    }

    // Handle like action
    if (direction === 'right') {
      onMenuItemLiked(menuItem);
    }
    
    // Move to next item
    setTimeout(() => {
      console.log('🔍 DEBUG: Moving to next item, current index:', currentIndex, 'menuItems.length:', menuItems.length);
      setCurrentIndex(prev => {
        const newIndex = prev + 1;
        console.log('🔍 DEBUG: Setting new index to:', newIndex);
        return newIndex;
      });
      // Force re-render
      setRenderKey(prev => prev + 1);
    }, 300);
  };

  const handleRefresh = () => {
    console.log('🔍 DEBUG: Refresh button clicked');
    loadMenuItems(true); // Reset index on manual refresh
  };

  const handleChatOpen = () => {
    setIsChatOpen(true);
  };

  const handleChatClose = () => {
    setIsChatOpen(false);
  };

  const handleVoiceOpen = () => {
    setIsVoiceOpen(true);
  };

  const handleVoiceClose = () => {
    setIsVoiceOpen(false);
  };

  const handleOrderDetailsOpen = (menuItem: MenuItem) => {
    setSelectedMenuItem(menuItem);
    setOrderDetailsOpen(true);
  };

  const handleOrderDetailsClose = () => {
    setOrderDetailsOpen(false);
    setSelectedMenuItem(null);
  };

  const handleLocationUpdate = (newLocation: string) => {
    setLocation(newLocation);
    setIsLocationModalOpen(false);
    // Optionally reload menu items with new location
    loadMenuItems(true);
  };

  const handleContinueConversationSubmit = () => {
    if (continueConversationInput.trim()) {
      handleConversationalSearch(continueConversationInput.trim());
      setContinueConversationInput('');
    }
  };

  const handleContinueConversationKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleContinueConversationSubmit();
    }
  };

  const getCurrentMealContext = (): string => {
    const hour = new Date().getHours();
    if (hour < 11) return 'breakfast';
    if (hour < 15) return 'lunch';
    if (hour < 18) return 'snack';
    return 'dinner';
  };

  const currentMenuItem = menuItems[currentIndex];
  
  // Debug currentMenuItem calculation
  console.log('🔍 DEBUG: currentMenuItem calculation - currentIndex:', currentIndex, 'menuItems.length:', menuItems.length, 'currentMenuItem:', currentMenuItem?.name || 'undefined');
  
  // Force re-render when currentIndex changes by using a key
  const cardKey = `${currentIndex}-${menuItems.length}-${currentMenuItem?.id || 'none'}-${renderKey}`;

  // Show initial prompt interface if user hasn't submitted a prompt yet
  if (!hasInitialPrompt) {
    return (
      <InitialPromptInterface 
        onPromptSubmit={onInitialPromptSubmit}
        onVoiceActivate={() => setIsVoiceOpen(true)}
      />
    );
  }

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-border bg-card space-y-4">
        {/* Location and Refresh */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            className="flex items-center gap-2 p-0 h-auto font-normal hover:bg-transparent"
            onClick={() => setIsLocationModalOpen(true)}
          >
            <MapPin className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">{location}</span>
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center gap-1"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>

        {/* Continue Conversation Input */}
        <div className="relative">
          <div className="flex items-center gap-2 bg-muted/50 hover:bg-muted/70 transition-colors rounded-2xl border border-border/50 p-3">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              disabled
            >
              <Plus className="w-4 h-4 text-muted-foreground" />
            </Button>
            
            <Input
              value={continueConversationInput}
              onChange={(e) => setContinueConversationInput(e.target.value)}
              onKeyPress={handleContinueConversationKeyPress}
              placeholder="Continue the conversation..."
              className="flex-1 border-0 bg-transparent focus-visible:ring-0 p-0 text-sm placeholder:text-muted-foreground"
            />
            
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={handleVoiceOpen}
            >
              <Mic className="w-4 h-4 text-muted-foreground" />
            </Button>
          </div>
        </div>

        {/* Discover Food Section */}
        <div className="space-y-2">
          <h2 className="text-lg font-medium text-foreground">Discover Food</h2>
          {menuItems.length > 0 && (
            <div className="text-sm text-muted-foreground">
              {menuItems.length} dishes nearby • Based on: '{lastSearchQuery || initialPrompt || 'your preferences'}'
            </div>
          )}
          {searchReason && (
            <div className="text-xs text-muted-foreground">
              {searchReason}
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4">
        {(() => {
          console.log('🔍 DEBUG: Render state - isLoading:', isLoading, 'menuItems.length:', menuItems.length, 'currentIndex:', currentIndex, 'currentMenuItem:', currentMenuItem);
          return null;
        })()}
        {isLoading ? (
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-muted-foreground" />
            <p className="text-muted-foreground">Finding perfect menu items...</p>
          </div>
        ) : currentMenuItem ? (
          <SwipeCard
            key={cardKey}
            menuItem={currentMenuItem}
            onSwipe={handleSwipe}
            onTap={() => handleOrderDetailsOpen(currentMenuItem)}
          />
        ) : (
          <Card className="w-full max-w-sm">
            <CardContent className="p-6 text-center">
              <p className="text-muted-foreground mb-4">
                {menuItems.length === 0 
                  ? "No menu items found matching your preferences." 
                  : "You've seen all available menu items!"}
              </p>
              <Button onClick={handleRefresh} variant="outline">
                <RefreshCw className="w-4 h-4 mr-2" />
                Find More
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Progress indicator */}
      {menuItems.length > 0 && (
        <div className="flex-shrink-0 p-4 bg-card border-t border-border">
          <div className="flex justify-center items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {Math.min(currentIndex + 1, menuItems.length)} of {menuItems.length}
            </span>
            <div className="flex gap-1">
              {menuItems.slice(0, Math.min(5, menuItems.length)).map((_, idx) => (
                <div
                  key={idx}
                  className={`w-2 h-2 rounded-full ${
                    idx === currentIndex ? 'bg-primary' : 'bg-muted'
                  }`}
                />
              ))}
              {menuItems.length > 5 && (
                <span className="text-xs text-muted-foreground ml-1">...</span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      <LocationModal
        isOpen={isLocationModalOpen}
        onClose={() => setIsLocationModalOpen(false)}
        currentLocation={location}
        onLocationUpdate={handleLocationUpdate}
      />

      <ChatModal
        isOpen={isChatOpen}
        onClose={handleChatClose}
        onUpdatePreferences={onUpdatePreferences}
        chatHistory={chatHistory}
        onChatUpdate={onChatHistoryUpdate}
        onStartNewChat={onStartNewChat}
      />

      <VoiceModal
        isOpen={isVoiceOpen}
        onClose={handleVoiceClose}
        onUpdatePreferences={onUpdatePreferences}
      />

      {selectedMenuItem && (
        <OrderDetailsModal
          menuItem={selectedMenuItem}
          isOpen={orderDetailsOpen}
          onClose={handleOrderDetailsClose}
        />
      )}
    </div>
  );
}
