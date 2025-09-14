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

type Screen = 'landing' | 'login' | 'email-signup' | 'onboarding' | 'sync-success' | 'notifications' | 'home' | 'liked' | 'profile';

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

interface UserProfileType {
  age: string;
  height: string;
  weight: string;
  gender: string;
  activityLevel: string;
  goals: string[];
}

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('landing');
  const [userProfile, setUserProfile] = useState<UserProfileType | null>(null);
  const [userPreferences, setUserPreferences] = useState<any>({});
  const [likedRestaurants, setLikedRestaurants] = useState<Restaurant[]>([]);
  const [isReturningUser, setIsReturningUser] = useState(false);

  const handleCreateProfile = () => {
    setIsReturningUser(false);
    setCurrentScreen('onboarding');
  };

  const handleEmailSignup = () => {
    setCurrentScreen('email-signup');
  };

  const handleShowLogin = () => {
    setCurrentScreen('login');
  };

  const handleLogin = () => {
    // Simulate login - in a real app this would authenticate
    setIsReturningUser(true);
    // Mock returning user profile
    setUserProfile({
      age: '28',
      height: '5\'9"',
      weight: '159',
      gender: 'male',
      activityLevel: 'moderate',
      goals: ['Track macros', 'Muscle gain']
    });
    setCurrentScreen('home');
  };

  const handleBackToLanding = () => {
    setCurrentScreen('landing');
  };

  const handleEmailSignupComplete = () => {
    setIsReturningUser(false);
    setCurrentScreen('onboarding');
  };

  const handleOnboardingComplete = (profile: UserProfileType) => {
    setUserProfile(profile);
    setCurrentScreen('sync-success');
  };

  const handleSyncComplete = () => {
    setCurrentScreen('notifications');
  };

  const handleNotificationsComplete = () => {
    setCurrentScreen('home');
  };

  const handleUpdatePreferences = (preferences: any) => {
    setUserPreferences(prev => ({ ...prev, ...preferences }));
  };

  const handleEditProfile = () => {
    setCurrentScreen('onboarding');
  };

  const handleRestaurantLiked = (restaurant: Restaurant) => {
    setLikedRestaurants(prev => [...prev, restaurant]);
    toast.success(`Added ${restaurant.name} to your liked list!`);
  };

  const handleRemoveLiked = (restaurantId: string) => {
    setLikedRestaurants(prev => prev.filter(r => r.id !== restaurantId));
    toast.success('Removed from liked list');
  };

  // Listen for health tracking events and global error handling
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

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      try {
        console.error('Unhandled promise rejection:', event.reason);
        event.preventDefault(); // Prevent default browser behavior
        
        // Only show toast if it's not a network/timeout error to avoid spam
        if (event.reason && !String(event.reason).includes('timeout')) {
          toast.error('Something went wrong. Please try again.');
        }
      } catch (error) {
        console.warn('Error handling rejection:', error);
      }
    };

    const handleGlobalError = (event: ErrorEvent) => {
      try {
        console.error('Global error:', event.error);
        
        // Only show toast for serious errors, not timeouts
        if (event.error && !String(event.error).includes('timeout')) {
          toast.error('An unexpected error occurred. Please refresh the page.');
        }
      } catch (error) {
        console.warn('Error handling global error:', error);
      }
    };

    // Add event listeners with proper typing
    window.addEventListener('show-toast', handleHealthTrack as EventListener);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleGlobalError);
    
    return () => {
      try {
        window.removeEventListener('show-toast', handleHealthTrack as EventListener);
        window.removeEventListener('unhandledrejection', handleUnhandledRejection);
        window.removeEventListener('error', handleGlobalError);
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
            onRestaurantLiked={handleRestaurantLiked}
          />
        );
      case 'liked':
        return (
          <LikedScreen 
            likedRestaurants={likedRestaurants}
            onRemoveLiked={handleRemoveLiked}
          />
        );
      case 'profile':
        return (
          <UserProfile 
            profile={userProfile}
            preferences={userPreferences}
            onEditProfile={handleEditProfile}
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
              {likedRestaurants.length > 0 && (
                <div className="absolute -top-1 -right-1 w-5 h-5 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs">
                  {likedRestaurants.length > 9 ? '9+' : likedRestaurants.length}
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