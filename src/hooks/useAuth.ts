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

    try {
      // Call REAL backend API
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      
      // Extract user and token from backend response
      const user: User = {
        id: data.user.user_id,
        name: data.user.username,
        email: data.user.email,
        role: data.user.role
      };
      
      const token = data.access_token || data.token;
      
      setAuth(token, user);
      setAuthState({ user, token, isAuthenticated: true });
      setLoading(false);
      return { success: true };
      
    } catch (err: any) {
      console.error('Login error:', err);
      setLoading(false);
      setError(err.message || "Login failed. Please try again.");
      return { success: false, error: err.message };
    }
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
