import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { MapPin, Search, X, Navigation, Clock } from 'lucide-react';

interface LocationModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentLocation: string;
  onLocationUpdate: (newLocation: string) => void;
}

export function LocationModal({ isOpen, onClose, currentLocation, onLocationUpdate }: LocationModalProps) {
  const [inputValue, setInputValue] = useState(currentLocation);
  const [isUpdating, setIsUpdating] = useState(false);
  const [addressSuggestions, setAddressSuggestions] = useState<string[]>([]);
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [recentAddresses, setRecentAddresses] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Load recent addresses from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('epicure_recent_addresses');
    if (saved) {
      try {
        setRecentAddresses(JSON.parse(saved));
      } catch (error) {
        console.warn('Error loading recent addresses:', error);
      }
    }
  }, []);

  // Mock address suggestions based on input
  useEffect(() => {
    if (inputValue.length > 2) {
      const mockSuggestions = generateAddressSuggestions(inputValue);
      setAddressSuggestions(mockSuggestions);
      setShowSuggestions(mockSuggestions.length > 0);
    } else {
      setAddressSuggestions([]);
      setShowSuggestions(false);
    }
  }, [inputValue]);

  const generateAddressSuggestions = (input: string): string[] => {
    const suggestions: string[] = [];
    const inputLower = input.toLowerCase();
    
    // Common address patterns
    if (/^\d/.test(input)) {
      // If starts with number, suggest street addresses
      suggestions.push(
        `${input} Main Street, New York, NY`,
        `${input} Broadway, New York, NY`,
        `${input} 5th Avenue, New York, NY`,
        `${input} Market Street, San Francisco, CA`,
        `${input} State Street, Chicago, IL`
      );
    } else if (inputLower.includes('main')) {
      suggestions.push(
        '123 Main Street, New York, NY',
        '456 Main Avenue, Brooklyn, NY',
        '789 Main Boulevard, Manhattan, NY'
      );
    } else if (inputLower.includes('broadway')) {
      suggestions.push(
        '1234 Broadway, New York, NY',
        '567 Broadway, New York, NY',
        '890 Broadway, New York, NY'
      );
    } else {
      // General suggestions based on common locations
      suggestions.push(
        `${input} Street, New York, NY`,
        `${input} Avenue, Brooklyn, NY`,
        `${input} Boulevard, Manhattan, NY`,
        `${input} Drive, San Francisco, CA`,
        `${input} Plaza, Los Angeles, CA`
      );
    }
    
    return suggestions.slice(0, 5);
  };

  const saveRecentAddress = (address: string) => {
    const updated = [address, ...recentAddresses.filter(a => a !== address)].slice(0, 5);
    setRecentAddresses(updated);
    localStorage.setItem('epicure_recent_addresses', JSON.stringify(updated));
  };

  const handleSubmit = async () => {
    if (inputValue.trim() && inputValue.trim() !== currentLocation) {
      setIsUpdating(true);
      
      // Simulate location validation/geocoding
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Save to recent addresses
      saveRecentAddress(inputValue.trim());
      
      onLocationUpdate(inputValue.trim());
      setIsUpdating(false);
      onClose();
    } else {
      onClose();
    }
  };

  const handleUseCurrentLocation = async () => {
    setIsGettingLocation(true);
    
    try {
      if (!('geolocation' in navigator)) {
        throw new Error('Geolocation is not supported by this browser');
      }

      // Check if geolocation permission is available
      if ('permissions' in navigator) {
        try {
          const permission = await navigator.permissions.query({ name: 'geolocation' });
          if (permission.state === 'denied') {
            throw new Error('Geolocation permission denied');
          }
        } catch (permissionError) {
          console.warn('Permission API not available:', permissionError);
        }
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const { latitude, longitude } = position.coords;
            
            // Simulate reverse geocoding with more realistic mock data
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Generate a more realistic mock address based on general location patterns
            const streetNumber = Math.floor(Math.random() * 9999) + 1;
            const streets = ['Main Street', 'Broadway', 'Oak Avenue', 'Park Place', 'First Street', 'Market Street'];
            const cities = [
              { name: 'New York', state: 'NY', zip: '10001' },
              { name: 'Los Angeles', state: 'CA', zip: '90210' },
              { name: 'Chicago', state: 'IL', zip: '60601' },
              { name: 'San Francisco', state: 'CA', zip: '94102' }
            ];
            
            const randomStreet = streets[Math.floor(Math.random() * streets.length)];
            const randomCity = cities[Math.floor(Math.random() * cities.length)];
            
            const mockAddress = `${streetNumber} ${randomStreet}, ${randomCity.name}, ${randomCity.state} ${randomCity.zip}`;
            setInputValue(mockAddress);
            setIsGettingLocation(false);
          } catch (geocodingError) {
            console.error('Error processing location:', geocodingError);
            setInputValue('123 Current Location Street, New York, NY 10001');
            setIsGettingLocation(false);
          }
        },
        (error) => {
          let errorMessage = 'Unable to get your location';
          let fallbackAddress = '123 Main Street, New York, NY 10001';
          
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Location access denied by user';
              console.warn('Geolocation permission denied');
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location information unavailable';
              console.warn('Geolocation position unavailable');
              break;
            case error.TIMEOUT:
              errorMessage = 'Location request timed out';
              console.warn('Geolocation request timeout');
              break;
            default:
              errorMessage = `Geolocation error: ${error.message || 'Unknown error'}`;
              console.error('Geolocation error:', {
                code: error.code,
                message: error.message,
                error: error
              });
              break;
          }
          
          setInputValue(fallbackAddress);
          setIsGettingLocation(false);
          
          // You could also show a toast notification here if needed
          console.info(`${errorMessage}. Using fallback address: ${fallbackAddress}`);
        },
        { 
          timeout: 15000, // Increased timeout
          enableHighAccuracy: false, // Faster response
          maximumAge: 300000 // Accept cached position up to 5 minutes old
        }
      );
    } catch (error) {
      console.error('Error initializing geolocation:', error);
      setIsGettingLocation(false);
      setInputValue('123 Main Street, New York, NY 10001');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    setShowSuggestions(false);
  };

  const popularLocations = [
    '123 Times Square, New York, NY 10036',
    '456 Union Square, San Francisco, CA 94108',
    '789 Michigan Avenue, Chicago, IL 60611',
    '321 Harvard Square, Cambridge, MA 02138',
    '654 Pike Place, Seattle, WA 98101',
    '987 South Beach, Miami, FL 33139'
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-primary" />
              Update Location
            </DialogTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <DialogDescription>
            Enter your specific address to find the most accurate nearby restaurants and delivery options.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Current Location Button */}
          <Button
            variant="outline"
            onClick={handleUseCurrentLocation}
            disabled={isGettingLocation}
            className="w-full justify-start"
          >
            {isGettingLocation ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
                Getting your location...
              </div>
            ) : (
              <>
                <Navigation className="w-4 h-4 mr-2" />
                Use Current Location
              </>
            )}
          </Button>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              onFocus={() => setShowSuggestions(addressSuggestions.length > 0)}
              placeholder="Enter specific address (e.g., 123 Main St, New York, NY)"
              className="pl-10"
              autoFocus
            />
            
            {/* Address Suggestions Dropdown */}
            {showSuggestions && addressSuggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-popover border rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto">
                {addressSuggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start h-auto p-3 text-sm rounded-none border-none"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    <MapPin className="w-3 h-3 mr-2 flex-shrink-0 text-muted-foreground" />
                    <span className="text-left">{suggestion}</span>
                  </Button>
                ))}
              </div>
            )}
          </div>

          {/* Recent Addresses */}
          {recentAddresses.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Clock className="w-3 h-3" />
                Recent addresses:
              </p>
              <div className="grid grid-cols-1 gap-1 max-h-32 overflow-y-auto">
                {recentAddresses.map((address, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    size="sm"
                    className="justify-start h-auto p-2 text-sm text-muted-foreground hover:text-foreground"
                    onClick={() => setInputValue(address)}
                  >
                    <Clock className="w-3 h-3 mr-2 flex-shrink-0" />
                    <span className="truncate">{address}</span>
                  </Button>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Popular areas:</p>
            <div className="grid grid-cols-1 gap-1 max-h-40 overflow-y-auto">
              {popularLocations.map((location) => (
                <Button
                  key={location}
                  variant="ghost"
                  size="sm"
                  className="justify-start h-auto p-2 text-sm text-muted-foreground hover:text-foreground"
                  onClick={() => setInputValue(location)}
                >
                  <MapPin className="w-3 h-3 mr-2 flex-shrink-0" />
                  <span className="truncate">{location}</span>
                </Button>
              ))}
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button 
              onClick={handleSubmit} 
              disabled={!inputValue.trim() || isUpdating}
              className="flex-1"
            >
              {isUpdating ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-primary-foreground/20 border-t-primary-foreground rounded-full animate-spin" />
                  Updating...
                </div>
              ) : (
                'Update Location'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}