import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { PersonalizationChatModal } from './PersonalizationChatModal';
import { PersonalizationVoiceModal } from './PersonalizationVoiceModal';

import { 
  Apple, 
  Heart, 
  CheckCircle, 
  Loader2, 
  Mic, 
  MessageCircle,
  Shield,
  Activity,
  User,
  SkipForward
} from 'lucide-react';
import { motion } from 'motion/react';
import { toast } from 'sonner@2.0.3';

interface UserProfile {
  age: string;
  height: string;
  weight: string;
  gender: string;
  activityLevel: string;
  goals: string[];
  appleId?: string;
  healthData?: any;
}

interface OnboardingScreenProps {
  onComplete: (profile: UserProfile) => void;
  isReturningUser?: boolean;
  isEditingProfile?: boolean;
  currentProfile?: any;
  skipAppleId?: boolean; // New prop to skip Apple ID step
  userId?: string; // User ID for storing personalization data
  authToken?: string; // Auth token for API calls
}

type OnboardingStep = 
  | 'apple-id' 
  | 'health-connect' 
  | 'health-sync' 
  | 'personalization'
  | 'completion';

export function OnboardingScreen({ onComplete, isReturningUser = false, isEditingProfile = false, currentProfile, skipAppleId = false, userId, authToken }: OnboardingScreenProps) {
  const [step, setStep] = useState<OnboardingStep>('apple-id');
  const [profile, setProfile] = useState<UserProfile>(
    isEditingProfile && currentProfile ? {
      age: currentProfile.age || '',
      height: currentProfile.height || '',
      weight: currentProfile.weight || '',
      gender: currentProfile.gender || '',
      activityLevel: currentProfile.activityLevel || '',
      goals: currentProfile.goals || []
    } : {
      age: '',
      height: '',
      weight: '',
      gender: '',
      activityLevel: '',
      goals: []
    }
  );
  
  const [isLoading, setIsLoading] = useState(false);
  const [healthDataSynced, setHealthDataSynced] = useState(false);
  const [chatModalOpen, setChatModalOpen] = useState(false);
  const [voiceModalOpen, setVoiceModalOpen] = useState(false);
  const [lastUsedMode, setLastUsedMode] = useState<'chat' | 'voice'>('voice');

  // Skip directly to personalization if returning user or editing profile
  // Skip Apple ID step if coming from email signup
  useEffect(() => {
    if ((isReturningUser || isEditingProfile) && step === 'apple-id') {
      setStep('personalization');
    } else if (skipAppleId && step === 'apple-id') {
      setStep('health-connect');
    }
  }, [isReturningUser, isEditingProfile, skipAppleId, step]);

  // Simulate Apple ID connection
  const handleAppleIdConnect = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      setProfile(prev => ({ 
        ...prev, 
        appleId: 'user@icloud.com' 
      }));
      toast.success('Successfully connected to Apple ID');
      setStep('health-connect');
    } catch (error) {
      console.error('Apple ID connection error:', error);
      toast.error('Failed to connect to Apple ID');
    } finally {
      setIsLoading(false);
    }
  };

  // Simulate Apple Health connection
  const handleHealthConnect = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      toast.success('Apple Health access granted');
      setStep('health-sync');
      
      setTimeout(() => {
        simulateHealthDataSync();
      }, 500);
    } catch (error) {
      console.error('Apple Health connection error:', error);
      toast.error('Failed to connect to Apple Health');
      setIsLoading(false);
    }
  };

  const handleSkipHealthConnect = () => {
    setStep('personalization');
  };

  // Simulate health data synchronization
  const simulateHealthDataSync = async () => {
    try {
      const healthDataPoints = [
        'Personal Information',
        'Body Measurements',
        'Activity Data',
        'Heart Rate',
        'Sleep Data',
        'Nutrition Preferences'
      ];

      for (let i = 0; i < healthDataPoints.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 800));
        toast.success(`Synced ${healthDataPoints[i]}`);
      }

      const mockHealthData = {
        age: '28',
        height: '5\'9"',
        weight: '159',
        gender: 'male',
        activityLevel: 'moderate',
        avgDailySteps: 8500,
        avgHeartRate: 68,
        sleepHours: 7.5,
        dietaryRestrictions: []
      };

      setProfile(prev => ({
        ...prev,
        ...mockHealthData,
        healthData: mockHealthData
      }));

      setHealthDataSynced(true);
      setIsLoading(false);
      
      toast.success('Health data sync complete!');
      
      setTimeout(() => {
        setStep('personalization');
      }, 2000);
    } catch (error) {
      console.error('Error syncing health data:', error);
      setIsLoading(false);
      toast.error('Failed to sync health data. Please try again.');
    }
  };

  const handleUpdateProfile = (updates: any) => {
    setProfile(prev => ({ ...prev, ...updates }));
  };

  const handlePersonalizationComplete = () => {
    setStep('completion');
  };

  const handleSkipPersonalization = () => {
    setStep('completion');
  };

  const handleComplete = () => {
    onComplete(profile);
  };

  const handleOpenChat = () => {
    setLastUsedMode('chat');
    setChatModalOpen(true);
  };

  const handleOpenVoice = () => {
    setLastUsedMode('voice');
    setVoiceModalOpen(true);
  };

  const renderStep = () => {
    switch (step) {
      case 'apple-id':
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-center space-y-6"
          >
            <div className="w-16 h-16 bg-black rounded-2xl flex items-center justify-center mx-auto">
              <Apple className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2>Connect with Apple ID</h2>
              <p className="text-muted-foreground mt-2">
                Sign in securely with your Apple ID to enable health data sync and personalized recommendations.
              </p>
            </div>

            <div className="bg-muted/50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium">Your privacy is protected</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Your health data stays on your device. We only access anonymized insights to improve your recommendations.
              </p>
            </div>

            <Button 
              onClick={handleAppleIdConnect} 
              className="w-full bg-black hover:bg-gray-800" 
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Connecting...
                </>
              ) : (
                <>
                  <Apple className="w-4 h-4 mr-2" />
                  Continue with Apple
                </>
              )}
            </Button>
          </motion.div>
        );

      case 'health-connect':
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-center space-y-6"
          >
            <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto">
              <Heart className="w-8 h-8 text-red-500" />
            </div>
            <div>
              <h2>Connect Apple Health</h2>
              <p className="text-muted-foreground mt-2">
                Allow Epicure to access your health data to provide personalized nutrition recommendations.
              </p>
            </div>

            <div className="text-left space-y-3">
              <h4>We'll access:</h4>
              <div className="space-y-2">
                {[
                  'Basic profile (age, height, weight)',
                  'Activity levels and exercise data',
                  'Heart rate and sleep patterns',
                  'Dietary preferences (if available)'
                ].map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-sm">{item}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <Button 
                onClick={handleHealthConnect} 
                className="w-full" 
                size="lg"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Authorizing...
                  </>
                ) : (
                  <>
                    <Heart className="w-4 h-4 mr-2" />
                    Connect Apple Health
                  </>
                )}
              </Button>
              
              <Button 
                onClick={handleSkipHealthConnect}
                variant="ghost"
                className="w-full"
                size="lg"
              >
                <SkipForward className="w-4 h-4 mr-2" />
                Skip for Now
              </Button>
            </div>
          </motion.div>
        );

      case 'health-sync':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-6"
          >
            <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto">
              <Activity className="w-8 h-8 text-blue-500" />
            </div>
            <div>
              <h2>Syncing Your Health Data</h2>
              <p className="text-muted-foreground mt-2">
                Please wait while we securely import your health information...
              </p>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
              
              {healthDataSynced && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-green-50 border border-green-200 rounded-lg p-4"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-800">Sync Complete!</span>
                  </div>
                  <p className="text-sm text-green-700">
                    Successfully imported your health profile. Moving to personalization...
                  </p>
                </motion.div>
              )}
            </div>
          </motion.div>
        );

      case 'personalization':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <User className="w-8 h-8 text-primary" />
              </div>
              <h2>{isEditingProfile ? 'Edit Your Profile' : 'Personalize Your Goals'}</h2>
              <p className="text-muted-foreground mt-2">
                {isEditingProfile 
                  ? 'Update your food and fitness goals to get better recommendations.'
                  : 'Tell me about your food and fitness goals to get personalized recommendations.'
                }
              </p>
            </div>

            {/* Goals Display */}
            {profile.goals.length > 0 && (
              <Card>
                <CardContent className="p-4">
                  <h4 className="font-medium mb-2">Your Goals:</h4>
                  <div className="flex flex-wrap gap-1">
                    {profile.goals.map((goal, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {goal}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Action Buttons */}
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <Button
                  onClick={handleOpenVoice}
                  variant={lastUsedMode === 'voice' ? 'default' : 'outline'}
                  className="h-16 flex-col gap-2"
                >
                  <Mic className="w-5 h-5" />
                  <span className="text-sm">Voice Chat</span>
                </Button>
                <Button
                  onClick={handleOpenChat}
                  variant={lastUsedMode === 'chat' ? 'default' : 'outline'}
                  className="h-16 flex-col gap-2"
                >
                  <MessageCircle className="w-5 h-5" />
                  <span className="text-sm">Text Chat</span>
                </Button>
              </div>

              <Button
                onClick={handleSkipPersonalization}
                variant="ghost"
                className="w-full"
              >
                <SkipForward className="w-4 h-4 mr-2" />
                Skip Personalization
              </Button>
            </div>

            {/* Chat Modal */}
        <PersonalizationChatModal
          isOpen={chatModalOpen}
          onClose={() => setChatModalOpen(false)}
          onUpdateProfile={handleUpdateProfile}
          onComplete={handlePersonalizationComplete}
          healthDataAvailable={healthDataSynced}
          userId={userId}
          authToken={authToken}
        />

            {/* Voice Modal */}
            <PersonalizationVoiceModal
              isOpen={voiceModalOpen}
              onClose={() => setVoiceModalOpen(false)}
              onUpdateProfile={handleUpdateProfile}
              onComplete={handlePersonalizationComplete}
            />
          </motion.div>
        );

      case 'completion':
        return (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center space-y-6"
          >
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle className="w-10 h-10 text-green-500" />
            </div>
            <div>
              <h2>Profile Complete!</h2>
              <p className="text-muted-foreground mt-2">
                Your Epicure profile is ready. Let's start discovering amazing food options tailored just for you!
              </p>
            </div>

            {/* Profile Summary */}
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Profile:</span>
                    <span>{profile.age} years, {profile.gender}, {profile.activityLevel}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Health Data:</span>
                    <span>{profile.healthData ? '✓ Synced from Apple Health' : '✓ Manual setup'}</span>
                  </div>
                  {profile.goals.length > 0 && (
                    <div>
                      <span className="text-sm text-muted-foreground">Goals:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {profile.goals.map((goal, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {goal}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Button onClick={handleComplete} className="w-full" size="lg">
              Start Discovering Food
            </Button>
          </motion.div>
        );

      default:
        return null;
    }
  };

  const getProgress = () => {
    const steps = ['apple-id', 'health-connect', 'health-sync', 'personalization', 'completion'];
    const currentIndex = steps.indexOf(step);
    return ((currentIndex + 1) / steps.length) * 100;
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Progress Bar */}
      <div className="p-4 border-b">
        <Progress value={getProgress()} className="max-w-md mx-auto" />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Card>
            <CardContent className="p-6">
              {renderStep()}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}