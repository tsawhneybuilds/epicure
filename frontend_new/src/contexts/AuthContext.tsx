import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { EpicureAPI } from '../utils/api';

interface User {
  id: string;
  email?: string;
  apple_id?: string;
}

interface AuthContextType {
  user: User | null;
  authToken: string | null;
  isLoading: boolean;
  login: (email?: string, appleId?: string) => Promise<void>;
  signup: (email?: string, appleId?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing auth on mount
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');
    
    if (token && userId) {
      setAuthToken(token);
      setUser({ id: userId });
    }
    
    setIsLoading(false);
  }, []);

  const login = async (email?: string, appleId?: string) => {
    try {
      setIsLoading(true);
      const response = await EpicureAPI.loginUser(email, appleId);
      
      setUser({ id: response.user_id, email, apple_id: appleId });
      setAuthToken(response.auth_token);
      
      // Store in localStorage
      localStorage.setItem('auth_token', response.auth_token);
      localStorage.setItem('user_id', response.user_id);
      if (email) localStorage.setItem('user_email', email);
      if (appleId) localStorage.setItem('user_apple_id', appleId);
      
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email?: string, appleId?: string) => {
    try {
      setIsLoading(true);
      const response = await EpicureAPI.createUser(email, appleId);
      
      setUser({ id: response.user_id, email, apple_id: appleId });
      setAuthToken(response.auth_token);
      
      // Store in localStorage
      localStorage.setItem('auth_token', response.auth_token);
      localStorage.setItem('user_id', response.user_id);
      if (email) localStorage.setItem('user_email', email);
      if (appleId) localStorage.setItem('user_apple_id', appleId);
      
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setAuthToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_apple_id');
  };

  const value: AuthContextType = {
    user,
    authToken,
    isLoading,
    login,
    signup,
    logout,
    isAuthenticated: !!user && !!authToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
