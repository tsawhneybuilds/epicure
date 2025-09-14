import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { User, Settings, Target, Activity, Heart, Brain, Bell } from 'lucide-react';
import { Separator } from './ui/separator';
import { ScrollArea } from './ui/scroll-area';
import { toast } from 'sonner@2.0.3';

interface UserProfileProps {
  profile: any;
  preferences: any;
  onEditProfile: () => void;
}

export function UserProfile({ profile, preferences, onEditProfile }: UserProfileProps) {
  const [notificationSettings, setNotificationSettings] = useState({
    recommendations: true,
    mealReminders: false,
    healthTracking: true,
    promotions: false
  });
  const calculateBMI = () => {
    if (profile.height && profile.weight) {
      // Parse height in feet'inches" format (e.g., "5'9"")
      const heightMatch = profile.height.match(/(\d+)'(\d+)"/);
      if (heightMatch) {
        const feet = parseInt(heightMatch[1]);
        const inches = parseInt(heightMatch[2]);
        const totalInches = feet * 12 + inches;
        const heightInM = totalInches * 0.0254; // Convert inches to meters
        
        const weightInLbs = parseInt(profile.weight);
        const weightInKg = weightInLbs * 0.453592; // Convert pounds to kg
        
        const bmi = weightInKg / (heightInM * heightInM);
        return bmi.toFixed(1);
      }
    }
    return null;
  };

  const getBMICategory = (bmi: number) => {
    if (bmi < 18.5) return { category: 'Underweight', color: 'text-blue-600' };
    if (bmi < 25) return { category: 'Normal', color: 'text-green-600' };
    if (bmi < 30) return { category: 'Overweight', color: 'text-yellow-600' };
    return { category: 'Obese', color: 'text-red-600' };
  };

  const bmi = calculateBMI();
  const bmiInfo = bmi ? getBMICategory(parseFloat(bmi)) : null;

  // Mock personal insights based on profile data
  const getPersonalInsights = () => {
    const insights = [];
    
    if (profile.goals?.includes('Muscle gain')) {
      insights.push("I'm focused on building muscle and strength");
    }
    if (profile.goals?.includes('Track macros')) {
      insights.push("I carefully track my nutrition and macros");
    }
    if (profile.activityLevel === 'high') {
      insights.push("I'm very active and exercise regularly");
    } else if (profile.activityLevel === 'moderate') {
      insights.push("I maintain a moderately active lifestyle");
    }
    if (preferences.budgetFriendly) {
      insights.push("I prefer budget-friendly dining options");
    }
    if (preferences.dietary === 'vegetarian') {
      insights.push("I follow a vegetarian lifestyle");
    }
    if (preferences.quickService) {
      insights.push("I value quick service when dining out");
    }
    
    // Add some example personal insights
    if (profile.age && parseInt(profile.age) < 30) {
      insights.push("I'm always looking to try new restaurants and cuisines");
    }
    
    return insights;
  };

  const personalInsights = getPersonalInsights();

  const handleNotificationToggle = (key: keyof typeof notificationSettings) => {
    setNotificationSettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
    
    const settingLabels = {
      recommendations: 'Restaurant recommendations',
      mealReminders: 'Meal reminders',
      healthTracking: 'Health tracking',
      promotions: 'Promotions and offers'
    };
    
    toast.success(`${settingLabels[key]} ${!notificationSettings[key] ? 'enabled' : 'disabled'}`);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b flex items-center justify-between flex-shrink-0">
        <h1>Your Profile</h1>
        <Button variant="outline" onClick={onEditProfile}>
          <Settings className="w-4 h-4 mr-2" />
          Edit
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="max-w-2xl mx-auto p-4 space-y-6">

        {/* Here's What We Know About You */}
        {personalInsights.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Here's what we know about you
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {personalInsights.map((insight, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-sm">{insight}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Basic Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Age</p>
                <p>{profile.age} years old</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Gender</p>
                <p className="capitalize">{profile.gender}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Height</p>
                <p>{profile.height}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Weight</p>
                <p>{profile.weight} lbs</p>
              </div>
            </div>
            
            {bmi && bmiInfo && (
              <div className="mt-4 p-3 bg-muted rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">BMI</span>
                  <div className="text-right">
                    <span className="font-medium">{bmi}</span>
                    <span className={`ml-2 text-sm ${bmiInfo.color}`}>
                      {bmiInfo.category}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

      {/* Activity Level */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Activity Level
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="capitalize">{profile.activityLevel?.replace('-', ' ')}</div>
        </CardContent>
      </Card>

      {/* Goals */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Goals & Preferences
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-2">Your Goals</p>
              <div className="flex flex-wrap gap-2">
                {profile.goals?.map((goal: string, index: number) => (
                  <Badge key={index} variant="secondary">
                    {goal}
                  </Badge>
                ))}
              </div>
            </div>
            
            {Object.keys(preferences).length > 0 && (
              <>
                <Separator />
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Current Preferences</p>
                  <div className="space-y-2 text-sm">
                    {preferences.trackMacros && (
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        Tracking macros
                      </div>
                    )}
                    {preferences.calorieGoal === 'deficit' && (
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                        Calorie deficit goal
                      </div>
                    )}
                    {preferences.budgetFriendly && (
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                        Budget-friendly options
                      </div>
                    )}
                    {preferences.dietary && (
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                        {preferences.dietary} diet
                      </div>
                    )}
                    {preferences.quickService && (
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Quick service preferred
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Health Integration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="w-5 h-5" />
            Health Integration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center">
                  <Heart className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className="font-medium">Apple Health</p>
                  <p className="text-sm text-muted-foreground">Connected</p>
                </div>
              </div>
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                Active
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              Syncing health data to personalize your food recommendations
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notifications
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Restaurant recommendations</p>
                <p className="text-sm text-muted-foreground">Get notified about new places to try</p>
              </div>
              <Switch
                checked={notificationSettings.recommendations}
                onCheckedChange={() => handleNotificationToggle('recommendations')}
              />
            </div>
            
            <Separator />
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Meal reminders</p>
                <p className="text-sm text-muted-foreground">Reminders to log your meals</p>
              </div>
              <Switch
                checked={notificationSettings.mealReminders}
                onCheckedChange={() => handleNotificationToggle('mealReminders')}
              />
            </div>
            
            <Separator />
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Health tracking</p>
                <p className="text-sm text-muted-foreground">Updates on your health goals</p>
              </div>
              <Switch
                checked={notificationSettings.healthTracking}
                onCheckedChange={() => handleNotificationToggle('healthTracking')}
              />
            </div>
            
            <Separator />
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Promotions and offers</p>
                <p className="text-sm text-muted-foreground">Special deals and discounts</p>
              </div>
              <Switch
                checked={notificationSettings.promotions}
                onCheckedChange={() => handleNotificationToggle('promotions')}
              />
            </div>
          </div>
        </CardContent>
      </Card>
        </div>
      </ScrollArea>
    </div>
  );
}