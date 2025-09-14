import React from 'react';
import { Button } from './ui/button';
import { Bell, BellOff } from 'lucide-react';
import { motion } from 'motion/react';

interface NotificationScreenProps {
  onComplete: () => void;
}

export function NotificationScreen({ onComplete }: NotificationScreenProps) {
  const handleAllowNotifications = async () => {
    try {
      const permission = await Notification.requestPermission();
      console.log('Notification permission:', permission);
    } catch (error) {
      console.log('Notification not supported');
    }
    onComplete();
  };

  const handleSkipNotifications = () => {
    onComplete();
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center px-8">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center max-w-sm"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2, type: "spring" }}
          className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-8"
        >
          <Bell className="w-12 h-12 text-primary" />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-8"
        >
          <h2 className="text-2xl font-medium text-foreground mb-4">
            Stay Updated
          </h2>
          <p className="text-muted-foreground leading-relaxed">
            Get notified about new restaurant recommendations, meal reminders, and exclusive offers tailored to your goals.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="space-y-4"
        >
          <Button
            onClick={handleAllowNotifications}
            className="w-full h-12 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl"
            size="lg"
          >
            <Bell className="w-5 h-5 mr-2" />
            Allow Notifications
          </Button>

          <Button
            onClick={handleSkipNotifications}
            variant="ghost"
            className="w-full h-12 text-muted-foreground hover:text-foreground rounded-xl"
            size="lg"
          >
            <BellOff className="w-5 h-5 mr-2" />
            Not Now
          </Button>
        </motion.div>
      </motion.div>
    </div>
  );
}