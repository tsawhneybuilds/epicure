import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Send, Bot, User, Mic, MicOff, X } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Badge } from './ui/badge';
import { VoiceModal } from './VoiceModal';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface ChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdatePreferences: (preferences: any) => void;
}

export function ChatModal({ isOpen, onClose, onUpdatePreferences }: ChatModalProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hi! I'm here to help personalize your feed. Tell me about your current goals, cravings, or dietary needs!",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState(false);

  useEffect(() => {
    // Check if speech recognition is supported
    setIsVoiceSupported('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);
  }, []);

  const startVoiceRecognition = () => {
    if (!isVoiceSupported) return;

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setIsListening(false);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    // Simulate AI response based on user input
    setTimeout(() => {
      const aiResponse = generateAIResponse(input);
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: aiResponse.content,
        sender: 'ai',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Update preferences based on the conversation
      if (aiResponse.preferences) {
        onUpdatePreferences(aiResponse.preferences);
      }
    }, 1000);

    setInput('');
  };

  const generateAIResponse = (userInput: string): { content: string; preferences?: any } => {
    const input = userInput.toLowerCase();
    
    // Meal-specific responses
    if (input.includes('pizza') || input.includes('italian')) {
      return {
        content: "Craving pizza? I'll show you the best Italian spots nearby with calorie info so you can find the perfect slice!",
        preferences: { cuisinePreference: 'italian', showCalories: true, priorityInfo: ['cuisine'] }
      };
    }
    
    if (input.includes('sushi') || input.includes('asian') || input.includes('japanese')) {
      return {
        content: "Great choice! I'll prioritize Asian restaurants and sushi spots, focusing on fresh, high-quality options.",
        preferences: { cuisinePreference: 'asian', showQuality: true, priorityInfo: ['cuisine'] }
      };
    }
    
    if (input.includes('breakfast') || input.includes('brunch')) {
      return {
        content: "Looking for breakfast? I'll show you morning spots with quick service and healthy options to start your day right!",
        preferences: { mealTime: 'breakfast', quickService: true, showWaitTime: true, priorityInfo: ['waitTime'] }
      };
    }
    
    if (input.includes('lunch') || input.includes('midday')) {
      return {
        content: "Perfect for lunch! I'll focus on quick, satisfying options that won't slow down your day.",
        preferences: { mealTime: 'lunch', quickService: true, showWaitTime: true, priorityInfo: ['waitTime'] }
      };
    }
    
    if (input.includes('dinner') || input.includes('evening')) {
      return {
        content: "Dinner plans! I'll show you quality restaurants with great ambiance and full nutrition info.",
        preferences: { mealTime: 'dinner', showMacros: true, priorityInfo: ['quality'] }
      };
    }
    
    if (input.includes('healthy') || input.includes('clean') || input.includes('nutritious')) {
      return {
        content: "Focusing on healthy options! I'll prioritize restaurants with fresh ingredients and detailed nutrition information.",
        preferences: { healthFocus: true, showMacros: true, showCalories: true, priorityInfo: ['nutrition'] }
      };
    }
    
    // Existing goal-based responses
    if (input.includes('macro') || input.includes('protein') || input.includes('carb') || input.includes('fat')) {
      return {
        content: "Perfect! I'll prioritize showing macro information on your cards. Your feed will now highlight protein, carbs, and fat content.",
        preferences: { trackMacros: true, showMacros: true, priorityInfo: ['macros'] }
      };
    }
    
    if (input.includes('budget') || input.includes('cheap') || input.includes('affordable') || input.includes('money')) {
      return {
        content: "I'll prioritize budget-friendly options and make sure price is prominently displayed!",
        preferences: { budgetFriendly: true, showPrice: true, priorityInfo: ['price'] }
      };
    }
    
    if (input.includes('vegetarian') || input.includes('vegan') || input.includes('plant')) {
      return {
        content: "Great! I'll filter for plant-based options and highlight dietary information.",
        preferences: { dietary: 'vegetarian', showDietary: true, priorityInfo: ['dietary'] }
      };
    }
    
    if (input.includes('quick') || input.includes('fast') || input.includes('time') || input.includes('busy')) {
      return {
        content: "I understand you need quick options! I'll prioritize places with fast service and show wait times.",
        preferences: { quickService: true, showWaitTime: true, priorityInfo: ['waitTime'] }
      };
    }

    // Default response
    return {
      content: "Thanks for sharing! I'm personalizing your feed based on your cravings. Feel free to tell me more about what you're in the mood for!",
      preferences: { conversationCount: (messages.length + 1) / 2 }
    };
  };

  const suggestedQuestions = [
    "I'm craving pizza tonight",
    "Show me healthy lunch options",
    "I want sushi or Asian food",
    "Find me a good breakfast spot",
    "Something quick for dinner"
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md h-[80vh] flex flex-col p-0">
        <DialogHeader className="p-4 border-b">
          <div className="flex items-center justify-between">
            <DialogTitle>Personalize Your Feed</DialogTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <DialogDescription className="text-sm text-muted-foreground">
            Tell me what you're looking for and I'll customize your recommendations
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
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
                    : 'bg-muted'
                }`}>
                  <p className="text-sm">{message.content}</p>
                </Card>
                {message.sender === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {messages.length <= 2 && (
              <div className="mt-6">
                <p className="text-sm text-muted-foreground mb-3">Quick suggestions:</p>
                <div className="space-y-2">
                  {suggestedQuestions.map((question, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      className="text-xs justify-start w-full h-auto p-2"
                      onClick={() => setInput(question)}
                    >
                      {question}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="p-4 border-t">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Tell me what you're looking for..."
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                className="pr-10"
              />
              {isVoiceSupported && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-1 top-1/2 transform -translate-y-1/2 h-7 w-7 p-0 text-muted-foreground"
                  onClick={() => setIsVoiceModalOpen(true)}
                >
                  <Mic className="w-3 h-3" />
                </Button>
              )}
            </div>
            <Button onClick={handleSend} size="icon" className="flex-shrink-0">
              <Send className="w-4 h-4" />
            </Button>
          </div>
          {isListening && (
            <div className="mt-2 flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-muted-foreground">Listening...</span>
            </div>
          )}
        </div>
      </DialogContent>

      {/* Voice Modal */}
      <VoiceModal
        isOpen={isVoiceModalOpen}
        onClose={() => {
          setIsVoiceModalOpen(false);
          onClose(); // Also close the chat modal
        }}
        onUpdatePreferences={onUpdatePreferences}
      />
    </Dialog>
  );
}