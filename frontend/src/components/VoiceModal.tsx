import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { X, Mic, MicOff } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { toast } from 'sonner';

interface VoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdatePreferences: (preferences: any) => void;
}

export function VoiceModal({ isOpen, onClose, onUpdatePreferences }: VoiceModalProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [displayedWords, setDisplayedWords] = useState<string[]>([]);
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsVoiceSupported('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);
  }, []);

  // Auto-start voice recognition when modal opens
  useEffect(() => {
    if (isOpen && isVoiceSupported) {
      // Reset state when opening
      setTranscript('');
      setDisplayedWords([]);
      setIsListening(false);
      
      // Start listening automatically after a brief delay
      const timer = setTimeout(() => {
        if (isOpen) { // Double-check modal is still open
          startVoiceRecognition();
        }
      }, 300);
      return () => clearTimeout(timer);
    } else if (!isOpen) {
      // Reset state when closing
      setIsListening(false);
      setTranscript('');
      setDisplayedWords([]);
    }
  }, [isOpen, isVoiceSupported]);

  // Animate words as they appear in transcript
  useEffect(() => {
    if (transcript) {
      const words = transcript.split(' ');
      const currentWordsLength = displayedWords.length;
      
      // Only add new words, don't reset the entire array
      if (words.length > currentWordsLength) {
        const newWords = words.slice(currentWordsLength);
        
        newWords.forEach((word, index) => {
          setTimeout(() => {
            setDisplayedWords(prev => [...prev, word]);
            // Auto-scroll to bottom
            if (scrollRef.current) {
              scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
            }
          }, index * 100); // 100ms delay between words for faster response
        });
      }
    }
  }, [transcript]);

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
        setTranscript('');
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

          // Update transcript with both final and interim results for real-time display
          const currentTranscript = finalTranscript || interimTranscript;
          if (currentTranscript) {
            setTranscript(currentTranscript);
          }

          // Only process when we have final results
          if (finalTranscript) {
            clearTimeout(recognitionTimeout);
            processVoiceInput(finalTranscript);
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

  const processVoiceInput = (input: string) => {
    const preferences: any = {};
    const lowerInput = input.toLowerCase();

    // Process voice input for preferences
    if (lowerInput.includes('protein') || lowerInput.includes('macro')) {
      preferences.showMacros = true;
    }
    if (lowerInput.includes('calorie') || lowerInput.includes('calories')) {
      preferences.showCalories = true;
    }
    if (lowerInput.includes('vegetarian') || lowerInput.includes('vegan')) {
      preferences.dietary = ['vegetarian'];
    }
    if (lowerInput.includes('quick') || lowerInput.includes('fast')) {
      preferences.showWaitTime = true;
    }

    if (Object.keys(preferences).length > 0) {
      onUpdatePreferences(preferences);
      toast.success('Updated your preferences based on your request!');
    }

    setTimeout(() => {
      onClose();
    }, 2000);
  };

  const stopListening = () => {
    setIsListening(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-x-0 top-0 z-50 h-1/2 bg-primary shadow-lg flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-primary-foreground/20 flex-shrink-0">
        <div>
          <h2 className="text-lg font-medium text-primary-foreground">Voice Search</h2>
          <p className="text-sm text-primary-foreground/80">Tell me what you're craving</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} className="text-primary-foreground hover:bg-primary-foreground/10">
          <X className="w-5 h-5" />
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col p-6">
        {/* Microphone Icon */}
        <div className="flex justify-center mb-6">
          <motion.div
            className="w-16 h-16 bg-primary-foreground/20 rounded-full flex items-center justify-center"
            animate={{ scale: isListening ? [1, 1.1, 1] : 1 }}
            transition={{ duration: 2, repeat: isListening ? Infinity : 0 }}
          >
            <Mic className="w-8 h-8 text-primary-foreground" />
          </motion.div>
        </div>

        {/* Transcript Area */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto px-4 py-2"
        >
          <div className="min-h-full flex flex-col justify-end">
            <div className="space-y-1">
              <AnimatePresence>
                {displayedWords.map((word, index) => (
                  <motion.span
                    key={`${word}-${index}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className="inline-block text-primary-foreground text-xl mr-2 leading-relaxed font-medium"
                  >
                    {word}
                  </motion.span>
                ))}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex justify-center pt-4 flex-shrink-0">
          {isListening && (
            <Button
              onClick={stopListening}
              variant="outline"
              size="sm"
              className="border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/10"
            >
              <MicOff className="w-4 h-4 mr-2" />
              Stop
            </Button>
          )}
          
          {!isListening && !isVoiceSupported && (
            <p className="text-primary-foreground/60 text-sm text-center">
              Voice recognition is not supported on this device
            </p>
          )}
        </div>
      </div>
    </div>
  );
}