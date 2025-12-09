/**
 * Authentication hook for WatchTower
 */

import { useState, useEffect, useCallback } from "react";
import { User, AuthState, getStoredAuth, setAuth, clearAuth } from "@/services/auth";

// Demo users for hackathon demonstration
const DEMO_USERS: Record<string, { password: string; user: User }> = {
  "reporter@army.mil": {
    password: "demo123",
    user: { id: "1", name: "Field Officer", email: "reporter@army.mil", role: "reporter" },
  },
  "admin@rakshanetra.mil": {
    password: "demo123",
    user: { id: "2", name: "System Admin", email: "admin@rakshanetra.mil", role: "admin" },
  },
};

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>(() => getStoredAuth());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const stored = getStoredAuth();
    setAuthState(stored);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Hardcoded login logic: check if username is "admin"
    const username = email.split('@')[0].toLowerCase();
    
    if (username === 'admin') {
      // Admin login
      const user: User = {
        id: '3',
        name: 'System Admin',
        email: email,
        role: 'admin'
      };
      const token = btoa(`${email}:${Date.now()}`);
      setAuth(token, user);
      setAuthState({ user, token, isAuthenticated: true });
      setLoading(false);
      return { success: true };
    } else {
      // Regular user login (reporter)
      const user: User = {
        id: Date.now().toString(),
        name: email.split('@')[0] || 'User',
        email: email,
        role: 'reporter'
      };
      const token = btoa(`${email}:${Date.now()}`);
      setAuth(token, user);
      setAuthState({ user, token, isAuthenticated: true });
      setLoading(false);
      return { success: true };
    }

    // This code is unreachable now but kept for safety
    setLoading(false);
    setError("Invalid credentials. Use demo accounts.");
    return { success: false, error: "Invalid credentials" };
  }, []);

  const register = useCallback(async (name: string, email: string, password: string) => {
    setLoading(true);
    setError(null);

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 800));

    const token = btoa(`${email}:${Date.now()}`);
    const user: User = { id: Date.now().toString(), name, email, role: "reporter" };

    setAuth(token, user);
    setAuthState({ user, token, isAuthenticated: true });
    setLoading(false);

    return { success: true };
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setAuthState({ user: null, token: null, isAuthenticated: false });
  }, []);

  return {
    ...authState,
    loading,
    error,
    login,
    register,
    logout,
  };
};
