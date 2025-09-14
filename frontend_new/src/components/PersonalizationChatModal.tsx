import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Send, Bot, User, X } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';
import { motion, AnimatePresence } from 'motion/react';
import { EpicureAPI } from '../utils/api';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface PersonalizationChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdateProfile: (updates: any) => void;
  onComplete: () => void;
  healthDataAvailable?: boolean; // New prop to indicate if health data is available
  userId?: string; // User ID for storing personalization data
  authToken?: string; // Auth token for API calls
}

export function PersonalizationChatModal({ 
  isOpen, 
  onClose, 
  onUpdateProfile, 
  onComplete,
  healthDataAvailable = true,
  userId,
  authToken
}: PersonalizationChatModalProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [fallbackQuestionsAsked, setFallbackQuestionsAsked] = useState<string[]>([]);
  const [collectedData, setCollectedData] = useState<any>({});
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Initialize conversation based on health data availability
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const initialMessage = healthDataAvailable 
        ? "Hi! I'm here to learn about your food and fitness goals. What are you hoping to achieve with Epicure?"
        : "Hi! Since we don't have access to your health data, I'd love to learn about you through a quick conversation. What are your main food and fitness goals?";
      
      setMessages([{
        id: '1',
        content: initialMessage,
        sender: 'ai',
        timestamp: new Date()
      }]);
    }
  }, [isOpen, healthDataAvailable, messages.length]);

  const streamText = (text: string, callback: () => void) => {
    setIsTyping(true);
    setStreamingText('');
    
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        setStreamingText(prev => prev + text[currentIndex]);
        currentIndex++;
        
        // Auto scroll during streaming
        if (scrollAreaRef.current) {
          try {
            const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
            if (viewport) {
              viewport.scrollTop = viewport.scrollHeight;
            }
          } catch (error) {
            console.warn('Scroll error:', error);
          }
        }
      } else {
        clearInterval(interval);
        setIsTyping(false);
        setStreamingText('');
        callback();
      }
    }, 30);
    
    // Safety timeout to prevent infinite streaming
    setTimeout(() => {
      clearInterval(interval);
      setIsTyping(false);
      setStreamingText('');
      callback();
    }, 10000);
  };

  const handleSendMessage = () => {
    if (!input.trim() || isProcessing) return;

    setIsProcessing(true);
    const userInput = input.trim();

    const userMessage: Message = {
      id: Date.now().toString(),
      content: userInput,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');

    // Generate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(userInput);
      
      streamText(aiResponse.content, () => {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: aiResponse.content,
          sender: 'ai',
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, aiMessage]);
        
        if (aiResponse.profileUpdates) {
          onUpdateProfile(aiResponse.profileUpdates);
        }
        
        if (aiResponse.isComplete) {
          setTimeout(onComplete, 2000);
        }
        
        setIsProcessing(false);
      });
    }, 1000);
  };

  const generateAIResponse = (userInput: string): { 
    content: string; 
    profileUpdates?: any; 
    isComplete?: boolean 
  } => {
    const input = userInput.toLowerCase();
    let goals: string[] = [];
    let collectedInfo = { ...collectedData };
    
    // Extract goals and information from user input
    if (input.includes('macro') || input.includes('protein') || input.includes('carb')) {
      goals.push('Track macros');
      collectedInfo.trackMacros = true;
    }
    if (input.includes('lose weight') || input.includes('deficit') || input.includes('cut')) {
      goals.push('Calorie deficit');
      collectedInfo.calorieGoal = 'deficit';
    }
    if (input.includes('muscle') || input.includes('gain') || input.includes('bulk')) {
      goals.push('Muscle gain');
      collectedInfo.muscleGain = true;
    }
    if (input.includes('vegetarian') || input.includes('vegan') || input.includes('plant')) {
      goals.push('Vegetarian/Vegan');
      collectedInfo.dietary = 'vegetarian';
    }
    if (input.includes('budget') || input.includes('cheap') || input.includes('money')) {
      goals.push('Budget-friendly');
      collectedInfo.budgetFriendly = true;
    }
    if (input.includes('quick') || input.includes('fast') || input.includes('busy')) {
      goals.push('Quick meals');
      collectedInfo.quickService = true;
    }

    // Extract age, height, weight if mentioned
    const ageMatch = input.match(/(\d+)\s*(?:years?|yrs?)/);
    if (ageMatch) {
      collectedInfo.age = ageMatch[1];
    }
    
    const heightMatch = input.match(/(\d+)'(\d+)"/);
    if (heightMatch) {
      collectedInfo.height = `${heightMatch[1]}'${heightMatch[2]}"`;
    }
    
    const weightMatch = input.match(/(\d+)\s*(?:lbs?|pounds?)/);
    if (weightMatch) {
      collectedInfo.weight = weightMatch[1];
    }

    // Update collected data
    setCollectedData(collectedInfo);

    // Check if conversation should end
    const conversationLength = messages.length;
    const hasBasicInfo = collectedInfo.age || collectedInfo.height || collectedInfo.weight;
    const hasGoals = goals.length > 0;
    
    // If health data is not available, we need more information
    const needsMoreInfo = !healthDataAvailable && (!hasBasicInfo || !hasGoals);
    
    if (conversationLength >= 6 || (!needsMoreInfo && conversationLength >= 3)) {
      const learnedInsights = generateLearnedInsights(collectedInfo, goals);
      
      // Store personalization data in backend if we have user credentials
      if (userId && authToken) {
        storePersonalizationData(collectedInfo, goals, learnedInsights, messages);
      }
      
      return {
        content: "Perfect! I have everything I need to personalize your Epicure experience. You're all set to start discovering amazing food options that match your goals!",
        profileUpdates: { 
          goals, 
          ...collectedInfo,
          learnedInsights 
        },
        isComplete: true
      };
    }
    
    if (goals.length > 0) {
      return {
        content: `Got it! I've noted your interest in ${goals.join(', ').toLowerCase()}. Is there anything else about your dietary preferences or lifestyle that would help me recommend better food options for you?`,
        profileUpdates: { goals, ...collectedInfo }
      };
    }
    
    // Generate fallback questions if health data is not available
    const fallbackQuestions = generateFallbackQuestions(collectedInfo, fallbackQuestionsAsked);
    const questionIndex = Math.min(fallbackQuestionsAsked.length, fallbackQuestions.length - 1);
    
    if (questionIndex < fallbackQuestions.length) {
      const question = fallbackQuestions[questionIndex];
      setFallbackQuestionsAsked(prev => [...prev, question]);
      return {
        content: question
      };
    }
    
    // Default follow-up questions
    const followUpQuestions = [
      "That's great! Are you looking to track specific nutrition goals like protein intake or calorie management?",
      "Interesting! Do you have any dietary restrictions or preferences I should know about?",
      "Perfect! What's your typical schedule like - do you need quick meal options or do you enjoy longer dining experiences?"
    ];
    
    const defaultQuestionIndex = Math.min(Math.floor((conversationLength - 1) / 2), followUpQuestions.length - 1);
    return {
      content: followUpQuestions[defaultQuestionIndex]
    };
  };

  const generateFallbackQuestions = (collectedInfo: any, askedQuestions: string[]): string[] => {
    const questions: string[] = [];
    
    if (!collectedInfo.age && !askedQuestions.some(q => q.includes('age'))) {
      questions.push("To better personalize your experience, could you tell me your age?");
    }
    
    if (!collectedInfo.height && !askedQuestions.some(q => q.includes('height'))) {
      questions.push("What's your height? This helps me understand your nutritional needs better.");
    }
    
    if (!collectedInfo.weight && !askedQuestions.some(q => q.includes('weight'))) {
      questions.push("Could you share your current weight? This helps me calculate appropriate portion sizes.");
    }
    
    if (!collectedInfo.activityLevel && !askedQuestions.some(q => q.includes('active'))) {
      questions.push("How would you describe your activity level - sedentary, moderate, or very active?");
    }
    
    if (!collectedInfo.dietary && !askedQuestions.some(q => q.includes('diet'))) {
      questions.push("Do you follow any specific dietary preferences like vegetarian, vegan, or have any food allergies?");
    }
    
    return questions;
  };

  const generateLearnedInsights = (collectedInfo: any, goals: string[]): string[] => {
    const insights: string[] = [];
    
    if (collectedInfo.trackMacros) {
      insights.push("I carefully track my nutrition and macros");
    }
    
    if (collectedInfo.calorieGoal === 'deficit') {
      insights.push("I'm focused on maintaining a calorie deficit for weight management");
    }
    
    if (collectedInfo.muscleGain) {
      insights.push("I'm focused on building muscle and strength");
    }
    
    if (collectedInfo.budgetFriendly) {
      insights.push("I prefer budget-friendly dining options");
    }
    
    if (collectedInfo.quickService) {
      insights.push("I value quick service when dining out");
    }
    
    if (collectedInfo.dietary === 'vegetarian') {
      insights.push("I follow a vegetarian lifestyle");
    }
    
    if (collectedInfo.age && parseInt(collectedInfo.age) < 30) {
      insights.push("I'm always looking to try new restaurants and cuisines");
    }
    
    if (collectedInfo.activityLevel === 'moderate') {
      insights.push("I maintain a moderately active lifestyle");
    }
    
    return insights;
  };

  const storePersonalizationData = async (collectedInfo: any, goals: string[], learnedInsights: string[], conversationMessages: Message[]) => {
    try {
      
      // Convert conversation messages to backend format
      const conversationPoints = conversationMessages.map(msg => ({
        role: msg.sender,
        content: msg.content,
        timestamp: msg.timestamp.toISOString()
      }));
      
      // Create learned insights object
      const learnedInsightsData = {
        lifestyle_patterns: {
          active_lifestyle: collectedInfo.activityLevel === 'high',
          moderate_activity: collectedInfo.activityLevel === 'moderate'
        },
        food_preferences: {
          track_macros: collectedInfo.trackMacros || false,
          calorie_deficit: collectedInfo.calorieGoal === 'deficit',
          muscle_gain: collectedInfo.muscleGain || false,
          vegetarian: collectedInfo.dietary === 'vegetarian'
        },
        dining_habits: {
          quick_meals: collectedInfo.quickService || false,
          budget_conscious: collectedInfo.budgetFriendly || false
        },
        health_goals: {
          weight_loss: collectedInfo.calorieGoal === 'deficit',
          muscle_gain: collectedInfo.muscleGain || false,
          macro_tracking: collectedInfo.trackMacros || false
        },
        confidence_scores: {
          lifestyle_patterns: 0.8,
          food_preferences: 0.9,
          dining_habits: 0.7,
          health_goals: 0.9
        },
        source: "conversation"
      };
      
      const personalizationData = {
        learned_insights: learnedInsightsData,
        conversation_points: conversationPoints,
        interaction_patterns: {
          goals_mentioned: goals,
          data_collected: collectedInfo
        },
        fallback_questions_asked: fallbackQuestionsAsked
      };
      
      await EpicureAPI.updatePersonalizationData(userId!, personalizationData, authToken!);
      console.log('✅ Personalization data stored successfully');
    } catch (error) {
      console.error('❌ Failed to store personalization data:', error);
    }
  };

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current && !isTyping) {
      setTimeout(() => {
        const viewport = scrollAreaRef.current?.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
        if (viewport) {
          viewport.scrollTop = viewport.scrollHeight;
        }
      }, 100);
    }
  }, [messages.length, isTyping]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-background">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div>
          <h2 className="text-lg font-medium">Chat with AI</h2>
          <p className="text-sm text-muted-foreground">Tell me about your goals</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="w-5 h-5" />
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea ref={scrollAreaRef} className="h-[calc(100vh-140px)] p-4">
          <div className="space-y-4 max-w-2xl mx-auto">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${
                  message.sender === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.sender === 'ai' && (
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-primary-foreground" />
                  </div>
                )}
                <Card className={`max-w-[80%] p-3 ${
                  message.sender === 'user' 
                    ? 'bg-primary text-primary-foreground' 
                    : 'bg-card'
                }`}>
                  <p className="text-sm leading-relaxed">{message.content}</p>
                </Card>
                {message.sender === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-muted-foreground" />
                  </div>
                )}
              </motion.div>
            ))}
            
            {/* Streaming message */}
            {isTyping && streamingText && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3 justify-start"
              >
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-primary-foreground" />
                </div>
                <Card className="max-w-[80%] p-3 bg-card">
                  <p className="text-sm leading-relaxed">
                    {streamingText}
                    <span className="animate-pulse">|</span>
                  </p>
                </Card>
              </motion.div>
            )}
            
            {/* Typing indicator */}
            {isTyping && !streamingText && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3 justify-start"
              >
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-primary-foreground" />
                </div>
                <Card className="p-3 bg-card">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </Card>
              </motion.div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-border">
        <div className="max-w-2xl mx-auto">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your response..."
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              className="flex-1 rounded-xl"
              disabled={isTyping || isProcessing}
            />
            <Button 
              onClick={handleSendMessage} 
              disabled={!input.trim() || isTyping || isProcessing}
              className="rounded-xl"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}