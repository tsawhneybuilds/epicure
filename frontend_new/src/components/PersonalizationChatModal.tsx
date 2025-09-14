import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Send, Bot, User, X } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';
import { motion, AnimatePresence } from 'motion/react';

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
}

export function PersonalizationChatModal({ 
  isOpen, 
  onClose, 
  onUpdateProfile, 
  onComplete 
}: PersonalizationChatModalProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hi! I'm here to learn about your food and fitness goals. What are you hoping to achieve with Epicure?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);

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
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');

    // Generate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(input);
      
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
    
    // Extract goals from user input
    if (input.includes('macro') || input.includes('protein') || input.includes('carb')) {
      goals.push('Track macros');
    }
    if (input.includes('lose weight') || input.includes('deficit') || input.includes('cut')) {
      goals.push('Calorie deficit');
    }
    if (input.includes('muscle') || input.includes('gain') || input.includes('bulk')) {
      goals.push('Muscle gain');
    }
    if (input.includes('vegetarian') || input.includes('vegan') || input.includes('plant')) {
      goals.push('Vegetarian/Vegan');
    }
    if (input.includes('budget') || input.includes('cheap') || input.includes('money')) {
      goals.push('Budget-friendly');
    }
    if (input.includes('quick') || input.includes('fast') || input.includes('busy')) {
      goals.push('Quick meals');
    }

    // Check if conversation should end
    const conversationLength = messages.length;
    if (conversationLength >= 4 || (goals.length > 0 && conversationLength >= 2)) {
      return {
        content: "Perfect! I have everything I need to personalize your Epicure experience. You're all set to start discovering amazing food options that match your goals!",
        profileUpdates: { goals },
        isComplete: true
      };
    }
    
    if (goals.length > 0) {
      return {
        content: `Got it! I've noted your interest in ${goals.join(', ').toLowerCase()}. Is there anything else about your dietary preferences or lifestyle that would help me recommend better food options for you?`,
        profileUpdates: { goals }
      };
    }
    
    const followUpQuestions = [
      "That's great! Are you looking to track specific nutrition goals like protein intake or calorie management?",
      "Interesting! Do you have any dietary restrictions or preferences I should know about?",
      "Perfect! What's your typical schedule like - do you need quick meal options or do you enjoy longer dining experiences?"
    ];
    
    const questionIndex = Math.min(conversationLength / 2, followUpQuestions.length - 1);
    return {
      content: followUpQuestions[Math.floor(questionIndex)]
    };
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
              disabled={isTyping}
            />
            <Button 
              onClick={handleSendMessage} 
              disabled={!input.trim() || isTyping}
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