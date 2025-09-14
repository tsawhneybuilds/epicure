import React, { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Mic, Paperclip, Send } from 'lucide-react';
import { motion } from 'motion/react';

interface InitialPromptInterfaceProps {
  onPromptSubmit: (prompt: string) => void;
  onVoiceActivate: () => void;
}

export function InitialPromptInterface({ onPromptSubmit, onVoiceActivate }: InitialPromptInterfaceProps) {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = () => {
    if (prompt.trim()) {
      onPromptSubmit(prompt.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-2xl mx-auto space-y-8"
      >
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-medium text-foreground mb-2">
            What's on the agenda today?
          </h1>
          <p className="text-muted-foreground">
            Tell us what you're looking for and we'll find the perfect meal options for you
          </p>
        </div>

        {/* Input Area */}
        <div className="relative">
          <div className="bg-card border border-border rounded-2xl p-4 shadow-sm">
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="I'm looking for healthy lunch options under $15..."
              className="min-h-[80px] border-0 resize-none focus-visible:ring-0 bg-transparent p-0 text-base placeholder:text-muted-foreground"
            />
            
            {/* Bottom toolbar */}
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  disabled
                >
                  <Paperclip className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  onClick={onVoiceActivate}
                >
                  <Mic className="w-4 h-4" />
                </Button>
              </div>
              
              <Button
                onClick={handleSubmit}
                disabled={!prompt.trim()}
                size="sm"
                className="h-8 w-8 p-0"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Sample prompts */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="space-y-3"
        >
          <p className="text-sm text-muted-foreground text-center">Try asking for:</p>
          <div className="grid grid-cols-1 gap-2">
            {[
              "High protein meals for post-workout recovery",
              "Vegan lunch options under $12 nearby",
              "Quick healthy breakfast before my meeting",
              "Low carb dinner that's ready in 15 minutes"
            ].map((suggestion, index) => (
              <Button
                key={index}
                variant="outline"
                className="h-auto p-3 text-left justify-start bg-muted/30 hover:bg-muted/50 border-border/50"
                onClick={() => setPrompt(suggestion)}
              >
                <span className="text-sm text-muted-foreground">{suggestion}</span>
              </Button>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}