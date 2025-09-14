import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { X, Mic, MicOff } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ScrollArea } from './ui/scroll-area';
import { toast } from 'sonner';

interface TranscriptEntry {
  id: string;
  text: string;
  speaker: 'user' | 'ai';
  timestamp: Date;
}

interface PersonalizationVoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdateProfile: (updates: any) => void;
  onComplete: () => void;
}

export function PersonalizationVoiceModal({ 
  isOpen, 
  onClose, 
  onUpdateProfile, 
  onComplete 
}: PersonalizationVoiceModalProps) {
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([
    {
      id: '1',
      text: "Hi! I'm here to learn about your food and fitness goals. What are you hoping to achieve with Epicure?",
      speaker: 'ai',
      timestamp: new Date()
    }
  ]);
  const [isListening, setIsListening] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsVoiceSupported('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);
  }, []);

  useEffect(() => {
    if (isOpen && !isListening && transcript.length === 1 && isVoiceSupported) {
      // Auto-start listening when modal opens
      const timer = setTimeout(() => {
        if (isOpen && !isListening) { // Double-check conditions
          startVoiceRecognition();
        }
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [isOpen, isListening, transcript.length, isVoiceSupported]);

  const streamText = (text: string, callback: () => void) => {
    setIsAISpeaking(true);
    setStreamingText('');
    
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        setStreamingText(prev => prev + text[currentIndex]);
        currentIndex++;
        
        // Auto scroll during streaming
        if (scrollAreaRef.current) {
          try {
            scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
          } catch (error) {
            console.warn('Scroll error:', error);
          }
        }
      } else {
        clearInterval(interval);
        setIsAISpeaking(false);
        setStreamingText('');
        callback();
      }
    }, 30);
    
    // Safety timeout to prevent infinite streaming
    setTimeout(() => {
      clearInterval(interval);
      setIsAISpeaking(false);
      setStreamingText('');
      callback();
    }, 10000);
  };

  const startVoiceRecognition = () => {
    if (!isVoiceSupported) {
      toast.error('Voice recognition is not supported on this device');
      return;
    }

    try {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      // Set timeout for voice recognition
      const recognitionTimeout = setTimeout(() => {
        try {
          recognition.stop();
          setIsListening(false);
          toast.error('Voice recognition timed out. Please try again.');
        } catch (error) {
          console.warn('Recognition timeout cleanup error:', error);
        }
      }, 30000); // 30 second timeout

      recognition.onstart = () => {
        setIsListening(true);
        setCurrentTranscript('');
      };

      recognition.onresult = (event: any) => {
        try {
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }

          setCurrentTranscript(finalTranscript || interimTranscript);

          if (finalTranscript) {
            clearTimeout(recognitionTimeout);
            handleUserResponse(finalTranscript);
          }
        } catch (error) {
          console.error('Speech result processing error:', error);
          setIsListening(false);
        }
      };

      recognition.onerror = (event: any) => {
        clearTimeout(recognitionTimeout);
        setIsListening(false);
        console.error('Speech recognition error:', event.error);
        if (event.error !== 'aborted') {
          toast.error('Voice recognition error. Please try again.');
        }
      };

      recognition.onend = () => {
        clearTimeout(recognitionTimeout);
        setIsListening(false);
      };

      recognition.start();
    } catch (error) {
      console.error('Failed to start voice recognition:', error);
      setIsListening(false);
      toast.error('Failed to start voice recognition. Please try again.');
    }
  };

  const handleUserResponse = (message: string) => {
    const userEntry: TranscriptEntry = {
      id: Date.now().toString(),
      text: message,
      speaker: 'user',
      timestamp: new Date()
    };

    setTranscript(prev => [...prev, userEntry]);
    setCurrentTranscript('');

    // Generate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(message);
      
      streamText(aiResponse.content, () => {
        const aiEntry: TranscriptEntry = {
          id: (Date.now() + 1).toString(),
          text: aiResponse.content,
          speaker: 'ai',
          timestamp: new Date()
        };

        setTranscript(prev => [...prev, aiEntry]);
        
        if (aiResponse.profileUpdates) {
          onUpdateProfile(aiResponse.profileUpdates);
        }

        if (aiResponse.isComplete) {
          setTimeout(onComplete, 3000);
        } else {
          // Continue listening after AI response
          setTimeout(() => {
            if (isOpen) {
              startVoiceRecognition();
            }
          }, 2000);
        }
      });
    }, 1500);
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
    const conversationLength = transcript.length;
    if (conversationLength >= 6 || (goals.length > 0 && conversationLength >= 3)) {
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
    
    const questionIndex = Math.min((conversationLength - 1) / 2, followUpQuestions.length - 1);
    return {
      content: followUpQuestions[Math.floor(questionIndex)]
    };
  };

  const stopListening = () => {
    setIsListening(false);
  };

  // Auto scroll to bottom when new entries arrive
  useEffect(() => {
    if (scrollAreaRef.current && !isAISpeaking) {
      const scrollArea = scrollAreaRef.current;
      setTimeout(() => {
        scrollArea.scrollTop = scrollArea.scrollHeight;
      }, 100);
    }
  }, [transcript.length, isAISpeaking]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-primary">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-primary-foreground/20">
        <div>
          <h2 className="text-lg font-medium text-primary-foreground">Voice Interview</h2>
          <p className="text-sm text-primary-foreground/80">Tell me about your goals</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} className="text-primary-foreground hover:bg-primary-foreground/10">
          <X className="w-5 h-5" />
        </Button>
      </div>

      {/* Transcript */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea ref={scrollAreaRef} className="h-[calc(100vh-200px)] p-6">
          <div className="space-y-4 max-w-2xl mx-auto">
            {transcript.map((entry) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`${entry.speaker === 'user' ? 'text-right' : 'text-left'}`}
              >
                <div className={`inline-block max-w-[80%] p-3 rounded-2xl ${
                  entry.speaker === 'user' 
                    ? 'bg-primary-foreground/20 text-primary-foreground' 
                    : 'bg-primary-foreground/10 text-primary-foreground'
                }`}>
                  <p className="text-sm leading-relaxed">{entry.text}</p>
                  <p className="text-xs opacity-60 mt-1">
                    {entry.speaker === 'user' ? 'You' : 'AI'} • {entry.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </motion.div>
            ))}
            
            {/* Current user transcript */}
            {currentTranscript && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-right"
              >
                <div className="inline-block max-w-[80%] p-3 rounded-2xl bg-primary-foreground/30 text-primary-foreground">
                  <p className="text-sm leading-relaxed">
                    {currentTranscript}
                    <span className="animate-pulse">|</span>
                  </p>
                  <p className="text-xs opacity-60 mt-1">You • Speaking...</p>
                </div>
              </motion.div>
            )}
            
            {/* Streaming AI response */}
            {isAISpeaking && streamingText && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-left"
              >
                <div className="inline-block max-w-[80%] p-3 rounded-2xl bg-primary-foreground/10 text-primary-foreground">
                  <p className="text-sm leading-relaxed">
                    {streamingText}
                    <span className="animate-pulse">|</span>
                  </p>
                  <p className="text-xs opacity-60 mt-1">AI • Responding...</p>
                </div>
              </motion.div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Controls */}
      <div className="p-6 text-center border-t border-primary-foreground/20">
        <div className="max-w-sm mx-auto space-y-4">
          {isListening ? (
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="space-y-4"
            >
              <motion.div
                className="w-20 h-20 bg-primary-foreground/20 rounded-full flex items-center justify-center mx-auto"
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Mic className="w-10 h-10 text-primary-foreground" />
              </motion.div>
              <p className="text-primary-foreground/80 text-sm">Listening...</p>
              <Button
                onClick={stopListening}
                variant="outline"
                className="border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/10"
              >
                <MicOff className="w-4 h-4 mr-2" />
                Stop
              </Button>
            </motion.div>
          ) : (
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="space-y-4"
            >
              <div className="w-20 h-20 bg-primary-foreground/10 rounded-full flex items-center justify-center mx-auto">
                <Mic className="w-10 h-10 text-primary-foreground/60" />
              </div>
              <Button
                onClick={startVoiceRecognition}
                disabled={!isVoiceSupported || isAISpeaking}
                className="bg-primary-foreground text-primary hover:bg-primary-foreground/90"
              >
                <Mic className="w-4 h-4 mr-2" />
                {isVoiceSupported ? 'Continue Speaking' : 'Voice not supported'}
              </Button>
              {isAISpeaking && (
                <p className="text-primary-foreground/60 text-sm">AI is responding...</p>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}