/**
 * Authentication service for WatchTower
 */

export interface User {
  id: string;
  name: string;
  email: string;
  role: "reporter" | "analyst" | "admin";
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

const AUTH_TOKEN_KEY = "watchtower_token";
const AUTH_USER_KEY = "watchtower_user";

export const getStoredAuth = (): AuthState => {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  const userStr = localStorage.getItem(AUTH_USER_KEY);
  
  if (token && userStr) {
    try {
      const user = JSON.parse(userStr) as User;
      return { user, token, isAuthenticated: true };
    } catch {
      clearAuth();
    }
  }
  
  return { user: null, token: null, isAuthenticated: false };
};

export const setAuth = (token: string, user: User): void => {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
};

export const clearAuth = (): void => {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
};

export const hasRole = (user: User | null, allowedRoles: string[]): boolean => {
  if (!user) return false;
  return allowedRoles.includes(user.role);
};
