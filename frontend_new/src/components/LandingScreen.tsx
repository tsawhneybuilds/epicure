import React from 'react';
import { Button } from './ui/button';
import { Apple, Mail } from 'lucide-react';
import { motion } from 'motion/react';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface LandingScreenProps {
  onCreateProfile: () => void;
  onEmailSignup: () => void;
  onLogin: () => void;
}

export function LandingScreen({ onCreateProfile, onEmailSignup, onLogin }: LandingScreenProps) {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Status Bar Placeholder */}
      <div className="flex justify-between items-center p-4 text-sm font-medium">
        <span>5:18</span>
        <div className="flex items-center gap-1">
          <div className="flex gap-1">
            <div className="w-1 h-3 bg-foreground rounded-sm"></div>
            <div className="w-1 h-3 bg-foreground rounded-sm"></div>
            <div className="w-1 h-3 bg-foreground rounded-sm"></div>
            <div className="w-1 h-3 bg-muted rounded-sm"></div>
          </div>
          <svg className="w-6 h-4 ml-2" viewBox="0 0 24 16" fill="none">
            <path d="M1 5C1 3.34315 2.34315 2 4 2H20C21.6569 2 23 3.34315 23 5V11C23 12.6569 21.6569 14 20 14H4C2.34315 14 1 12.6569 1 11V5Z" stroke="currentColor" strokeWidth="1"/>
            <path d="M23 6L23 10" stroke="currentColor" strokeWidth="1" strokeLinecap="round"/>
          </svg>
          <div className="w-6 h-3 bg-foreground rounded-sm ml-1"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col justify-center items-center px-8 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center mb-12"
        >
          <h1 className="text-3xl font-medium text-primary mb-4 leading-tight">
            LET'S GET STARTED<br />
            WITH EPICURE
          </h1>
        </motion.div>

        {/* Illustration */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-16 relative"
        >
          <div className="w-80 h-64 relative">
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=400&h=300&fit=crop"
              alt="Healthy food illustration"
              className="w-full h-full object-cover rounded-2xl"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-primary/20 to-transparent rounded-2xl"></div>
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="w-full max-w-sm space-y-4"
        >
          <Button
            onClick={onCreateProfile}
            className="w-full h-14 bg-primary hover:bg-primary/90 text-primary-foreground rounded-2xl text-base font-medium"
            size="lg"
          >
            <Apple className="w-5 h-5 mr-3" />
            Continue with Apple
          </Button>

          <Button
            onClick={onEmailSignup}
            variant="outline"
            className="w-full h-14 border-2 border-primary text-primary hover:bg-primary/5 rounded-2xl text-base font-medium"
            size="lg"
          >
            <Mail className="w-5 h-5 mr-3" />
            Continue with email
          </Button>

          <div className="text-center pt-4">
            <button
              onClick={onLogin}
              className="text-muted-foreground text-base hover:text-foreground transition-colors"
            >
              Already have an account?
            </button>
          </div>
        </motion.div>
      </div>

      {/* Bottom indicator */}
      <div className="flex justify-center pb-6">
        <div className="w-32 h-1 bg-foreground rounded-full"></div>
      </div>
    </div>
  );
}