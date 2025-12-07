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
  "analyst@cert.army.mil": {
    password: "demo123",
    user: { id: "2", name: "CERT Analyst", email: "analyst@cert.army.mil", role: "analyst" },
  },
  "admin@rakshanetra.mil": {
    password: "demo123",
    user: { id: "3", name: "System Admin", email: "admin@rakshanetra.mil", role: "admin" },
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

    const demoUser = DEMO_USERS[email.toLowerCase()];

    if (demoUser && demoUser.password === password) {
      const token = btoa(`${email}:${Date.now()}`);
      setAuth(token, demoUser.user);
      setAuthState({ user: demoUser.user, token, isAuthenticated: true });
      setLoading(false);
      return { success: true };
    }

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
