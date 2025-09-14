import React, { useEffect } from 'react';
import { motion } from 'motion/react';

interface SyncSuccessScreenProps {
  onComplete: () => void;
}

export function SyncSuccessScreen({ onComplete }: SyncSuccessScreenProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete();
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen bg-primary flex items-center justify-center text-center px-8"
    >
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.6, delay: 0.3, type: "spring" }}
          className="w-20 h-20 bg-primary-foreground/20 rounded-full flex items-center justify-center mx-auto mb-8"
        >
          <svg
            className="w-10 h-10 text-primary-foreground"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </motion.div>
        
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-4xl font-light text-primary-foreground leading-tight"
        >
          Sync<br />
          Successful
        </motion.h1>
      </motion.div>
    </motion.div>
  );
}