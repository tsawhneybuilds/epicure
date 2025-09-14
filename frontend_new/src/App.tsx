import React, { useState, useEffect } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { LandingScreen } from './components/LandingScreen';
import { LoginScreen } from './components/LoginScreen';
import { EmailSignupScreen } from './components/EmailSignupScreen';
import { OnboardingScreen } from './components/OnboardingScreen';
import { SyncSuccessScreen } from './components/SyncSuccessScreen';
import { NotificationScreen } from './components/NotificationScreen';
import { SwipeInterface } from './components/SwipeInterface';
import { UserProfile } from './components/UserProfile';
import { LikedScreen } from './components/LikedScreen';
import { Home, User, Heart } from 'lucide-react';
import { Button } from './components/ui/button';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner@2.0.3';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { EpicureAPI } from './utils/api';

type Screen = 'landing' | 'login' | 'email-signup' | 'onboarding' | 'sync-success' | 'notifications' | 'home' | 'liked' | 'profile';

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

interface UserProfileType {
  age: string;
  height: string;
  weight: string;
  gender: string;
  activityLevel: string;
  goals: string[];
}

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

function AppContent() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('landing');
  const [userProfile, setUserProfile] = useState<UserProfileType | null>(null);
  const [userPreferences, setUserPreferences] = useState<any>({});
  const [learnedInsights, setLearnedInsights] = useState<any[]>([]);
  const [likedMenuItems, setLikedMenuItems] = useState<MenuItem[]>([]);
  const [isReturningUser, setIsReturningUser] = useState(false);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [fromEmailSignup, setFromEmailSignup] = useState(false);
  
  // Chat state - persistent across navigation
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [hasInitialPrompt, setHasInitialPrompt] = useState(false);
  const [initialPrompt, setInitialPrompt] = useState('');
  
  const { user, authToken, isAuthenticated, isLoading } = useAuth();

  // Load user profile and personalization data when authenticated
  useEffect(() => {
    const loadUserData = async () => {
      if (user?.id && authToken) {
        try {
          const profileResponse = await EpicureAPI.getUserProfile(user.id, authToken);
          
          if (profileResponse.profile) {
            setUserProfile(profileResponse.profile);
          }
          
          if (profileResponse.preferences) {
            setUserPreferences(profileResponse.preferences);
          }
          
          // Extract learned insights from personalization data
          if (profileResponse.preferences?.personalization_data?.learned_insights) {
            const insights = profileResponse.preferences.personalization_data.learned_insights;
            const insightStrings = [];
            
            // Convert structured insights to display strings
            if (insights.food_preferences?.track_macros) {
              insightStrings.push("I carefully track my nutrition and macros");
            }
            if (insights.food_preferences?.calorie_deficit) {
              insightStrings.push("I'm focused on maintaining a calorie deficit for weight management");
            }
            if (insights.food_preferences?.muscle_gain) {
              insightStrings.push("I'm focused on building muscle and strength");
            }
            if (insights.dining_habits?.budget_conscious) {
              insightStrings.push("I prefer budget-friendly dining options");
            }
            if (insights.dining_habits?.quick_meals) {
              insightStrings.push("I value quick service when dining out");
            }
            if (insights.food_preferences?.vegetarian) {
              insightStrings.push("I follow a vegetarian lifestyle");
            }
            if (insights.lifestyle_patterns?.active_lifestyle) {
              insightStrings.push("I'm very active and exercise regularly");
            } else if (insights.lifestyle_patterns?.moderate_activity) {
              insightStrings.push("I maintain a moderately active lifestyle");
            }
            
            setLearnedInsights(insightStrings);
          }
        } catch (error) {
          console.error('Failed to load user data:', error);
        }
      }
    };

    loadUserData();
  }, [user?.id, authToken]);

  const handleCreateProfile = () => {
    setIsReturningUser(false);
    setIsEditingProfile(false);
    setCurrentScreen('onboarding');
  };

  const handleEmailSignup = () => {
    setCurrentScreen('email-signup');
  };

  const handleShowLogin = () => {
    setCurrentScreen('login');
  };

  const handleLogin = () => {
    // User is now authenticated, check if they have a profile
    setIsReturningUser(true);
    setCurrentScreen('home');
  };

  const handleBackToLanding = () => {
    setCurrentScreen('landing');
  };

  const handleEmailSignupComplete = () => {
    setIsReturningUser(false);
    setIsEditingProfile(false);
    setFromEmailSignup(true);
    setCurrentScreen('onboarding');
  };

  const handleOnboardingComplete = (profile: UserProfileType) => {
    setUserProfile(profile);
    setFromEmailSignup(false); // Reset the flag
    if (isEditingProfile) {
      // If we're editing profile, go directly back to profile screen
      setIsEditingProfile(false);
      setCurrentScreen('profile');
    } else {
      // If it's initial onboarding, continue with sync-success flow
      setCurrentScreen('sync-success');
    }
  };

  const handleSyncComplete = () => {
    setCurrentScreen('notifications');
  };

  const handleNotificationsComplete = () => {
    setCurrentScreen('home');
  };

  const handleUpdatePreferences = (preferences: any) => {
    setUserPreferences(prev => ({ ...prev, ...preferences }));
    
    // Extract learned insights if they exist in the preferences
    if (preferences.learnedInsights) {
      setLearnedInsights(preferences.learnedInsights);
    }
  };

  const handleEditProfile = () => {
    setIsEditingProfile(true);
    setIsReturningUser(true);
    setCurrentScreen('onboarding');
  };

  const handleMenuItemLiked = (menuItem: MenuItem) => {
    setLikedMenuItems(prev => [...prev, menuItem]);
    toast.success(`Added ${menuItem.name} to your liked list!`);
  };

  const handleRemoveLiked = (menuItemId: string) => {
    setLikedMenuItems(prev => prev.filter(item => item.id !== menuItemId));
    toast.success('Removed from liked list');
  };

  const handleChatHistoryUpdate = (newMessages: Message[]) => {
    setChatHistory(newMessages);
  };

  const handleInitialPromptSubmit = (prompt: string) => {
    console.log('📝 App: Received initial prompt:', prompt);
    setInitialPrompt(prompt);
    setHasInitialPrompt(true);
    
    // Initialize chat history with the initial prompt
    const userMessage: Message = {
      id: Date.now().toString(),
      content: prompt,
      sender: 'user',
      timestamp: new Date()
    };
    
    const aiResponse: Message = {
      id: (Date.now() + 1).toString(),
      content: generateInitialAIResponse(prompt),
      sender: 'ai',
      timestamp: new Date()
    };
    
    setChatHistory([userMessage, aiResponse]);
  };

  const handleStartNewChat = () => {
    setChatHistory([]);
    setHasInitialPrompt(false);
    setInitialPrompt('');
  };

  const generateInitialAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('protein') || input.includes('workout') || input.includes('gym')) {
      return "Perfect! I found menu items with high-protein options perfect for your fitness goals. I'll prioritize showing protein content and post-workout friendly meals.";
    }
    
    if (input.includes('vegan') || input.includes('vegetarian') || input.includes('plant')) {
      return "Great choice! I'm showing you the best plant-based dishes nearby with detailed dietary information and fresh, healthy options.";
    }
    
    if (input.includes('quick') || input.includes('fast') || input.includes('meeting') || input.includes('busy')) {
      return "I understand you're in a hurry! Here are fast food options nearby with short preparation times and quick service.";
    }
    
    if (input.includes('budget') || input.includes('cheap') || input.includes('under') || input.includes('$')) {
      return "I've found great budget-friendly dishes that won't break the bank. I'll highlight pricing and value for each item.";
    }
    
    if (input.includes('healthy') || input.includes('clean') || input.includes('low carb')) {
      return "Excellent! I'm showing you healthy menu items with detailed nutrition info so you can make informed choices.";
    }
    
    return "Got it! I've found some great food options based on your request. Swipe right on dishes you like, and feel free to ask me to refine your search anytime!";
  };

  // Listen for health tracking events
  useEffect(() => {
    const handleHealthTrack = (event: CustomEvent) => {
      try {
        if (event?.detail?.title) {
          toast.success(event.detail.title, {
            description: event.detail.description
          });
        }
      } catch (error) {
        console.warn('Toast error:', error);
      }
    };

    // Only add the health tracking listener
    window.addEventListener('show-toast', handleHealthTrack as EventListener);
    
    return () => {
      try {
        window.removeEventListener('show-toast', handleHealthTrack as EventListener);
      } catch (error) {
        console.warn('Event cleanup error:', error);
      }
    };
  }, []);

  if (currentScreen === 'landing') {
    return (
      <LandingScreen 
        onCreateProfile={handleCreateProfile}
        onEmailSignup={handleEmailSignup}
        onLogin={handleShowLogin}
      />
    );
  }

  if (currentScreen === 'login') {
    return (
      <LoginScreen 
        onLogin={handleLogin}
        onBack={handleBackToLanding}
      />
    );
  }

  if (currentScreen === 'email-signup') {
    return (
      <EmailSignupScreen 
        onSignupComplete={handleEmailSignupComplete}
        onBack={handleBackToLanding}
      />
    );
  }

  if (currentScreen === 'onboarding') {
    return (
      <OnboardingScreen 
        onComplete={handleOnboardingComplete}
        isReturningUser={isReturningUser}
        isEditingProfile={isEditingProfile}
        currentProfile={userProfile}
        skipAppleId={fromEmailSignup}
        userId={user?.id}
        authToken={authToken}
      />
    );
  }

  if (currentScreen === 'sync-success') {
    return <SyncSuccessScreen onComplete={handleSyncComplete} />;
  }

  if (currentScreen === 'notifications') {
    return <NotificationScreen onComplete={handleNotificationsComplete} />;
  }

  const renderScreen = () => {
    switch (currentScreen) {
      case 'home':
        return (
          <SwipeInterface 
            userPreferences={userPreferences} 
            userProfile={userProfile}
            onUpdatePreferences={handleUpdatePreferences}
            onMenuItemLiked={handleMenuItemLiked}
            chatHistory={chatHistory}
            onChatHistoryUpdate={handleChatHistoryUpdate}
            hasInitialPrompt={hasInitialPrompt}
            initialPrompt={initialPrompt}
            onInitialPromptSubmit={handleInitialPromptSubmit}
            onStartNewChat={handleStartNewChat}
          />
        );
      case 'liked':
        return (
          <LikedScreen 
            likedMenuItems={likedMenuItems}
            onRemoveLiked={handleRemoveLiked}
          />
        );
      case 'profile':
        return (
          <UserProfile 
            profile={userProfile}
            preferences={userPreferences}
            onEditProfile={handleEditProfile}
            learnedInsights={learnedInsights}
          />
        );
      default:
        return null;
    }
  };

  return (
    <ErrorBoundary>
      <div className="size-full flex flex-col bg-background">
        {/* Main Content */}
        <div className="flex-1 overflow-hidden">
          {renderScreen()}
        </div>

        {/* Bottom Navigation */}
        <div className="border-t bg-card p-2">
          <div className="flex justify-around items-center max-w-md mx-auto">
            <Button
              variant={currentScreen === 'home' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrentScreen('home')}
              className="flex flex-col items-center gap-1 h-auto py-2 px-4"
            >
              <Home className="w-5 h-5" />
              <span className="text-xs">Discover</span>
            </Button>
            
            <Button
              variant={currentScreen === 'liked' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrentScreen('liked')}
              className="flex flex-col items-center gap-1 h-auto py-2 px-4 relative"
            >
              <Heart className="w-5 h-5" />
              <span className="text-xs">Liked</span>
              {likedMenuItems.length > 0 && (
                <div className="absolute -top-1 -right-1 w-5 h-5 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs">
                  {likedMenuItems.length > 9 ? '9+' : likedMenuItems.length}
                </div>
              )}
            </Button>
            
            <Button
              variant={currentScreen === 'profile' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrentScreen('profile')}
              className="flex flex-col items-center gap-1 h-auto py-2 px-4"
            >
              <User className="w-5 h-5" />
              <span className="text-xs">Profile</span>
            </Button>
          </div>
        </div>

        <Toaster />
      </div>
    </ErrorBoundary>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppContent />
        <Toaster />
      </AuthProvider>
    </ErrorBoundary>
  );
}