import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Send, Bot, User } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface ChatInterfaceProps {
  onUpdatePreferences: (preferences: any) => void;
}

export function ChatInterface({ onUpdatePreferences }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hi! I'm here to help you find the perfect food options. Tell me about your current goals, dietary preferences, or what you're craving!",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');

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
    
    if (input.includes('macro') || input.includes('protein') || input.includes('carb') || input.includes('fat')) {
      return {
        content: "I can help you track macros! I've noted that you're interested in macro tracking. Are you looking for high protein options, or do you have specific macro targets in mind?",
        preferences: { trackMacros: true, showMacros: true }
      };
    }
    
    if (input.includes('calorie') || input.includes('deficit') || input.includes('lose weight')) {
      return {
        content: "Got it! I'll prioritize lower-calorie options for you. What's your target calorie range per meal?",
        preferences: { calorieGoal: 'deficit', showCalories: true }
      };
    }
    
    if (input.includes('budget') || input.includes('cheap') || input.includes('affordable')) {
      return {
        content: "I'll focus on budget-friendly options! I'll make sure to highlight prices and value for money.",
        preferences: { budgetFriendly: true, showPrice: true }
      };
    }
    
    if (input.includes('vegetarian') || input.includes('vegan') || input.includes('plant')) {
      return {
        content: "Perfect! I'll filter for vegetarian/vegan options. Do you have any specific plant-based preferences?",
        preferences: { dietary: 'vegetarian', showDietary: true }
      };
    }
    
    if (input.includes('quick') || input.includes('fast') || input.includes('time')) {
      return {
        content: "I understand you need quick options! I'll prioritize places with fast service and delivery options.",
        preferences: { quickService: true, showWaitTime: true }
      };
    }

    // Default response
    return {
      content: "Thanks for sharing! I'm learning about your preferences. Feel free to tell me more about your dietary goals, favorite cuisines, or what you're in the mood for today!",
      preferences: null
    };
  };

  const suggestedQuestions = [
    "I want to track my macros",
    "I'm looking for high protein meals",
    "I need budget-friendly options",
    "Show me vegetarian restaurants nearby",
    "I want something quick for lunch"
  ];

  return (
    <div className="flex flex-col h-full max-w-2xl mx-auto">
      <div className="p-4 border-b">
        <h2>Chat with FoodFit AI</h2>
        <p className="text-sm text-muted-foreground">
          Tell me about your goals and preferences
        </p>
      </div>

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
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
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
                <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}
        </div>

        {messages.length === 1 && (
          <div className="mt-6">
            <p className="text-sm text-muted-foreground mb-3">Try asking:</p>
            <div className="space-y-2">
              {suggestedQuestions.map((question, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="text-xs justify-start w-full"
                  onClick={() => setInput(question)}
                >
                  {question}
                </Button>
              ))}
            </div>
          </div>
        )}
      </ScrollArea>

      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tell me about your food goals..."
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          />
          <Button onClick={handleSend} size="icon">
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}