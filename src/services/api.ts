/**
 * API service wrapper for WatchTower
 * Handles authentication headers and error management
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { API_BASE_URL } from "@/utils/constants";

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor - adds auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("watchtower_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handles 401 errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("watchtower_token");
      localStorage.removeItem("watchtower_user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (credentials: { email: string; password: string }) =>
    api.post("/api/auth/login", credentials),
  register: (data: { name: string; email: string; password: string; role: string }) =>
    api.post("/api/auth/register", data),
  logout: () => api.post("/api/auth/logout"),
  refreshToken: () => api.post("/api/auth/refresh"),
};

export const incidentAPI = {
  submit: (data: FormData) =>
    api.post("/api/incidents", data, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  getAll: (params?: { page?: number; type?: string; severity?: string }) =>
    api.get("/api/incidents", { params }),
  getById: (id: string) => api.get(`/api/incidents/${id}`),
  escalate: (id: string) => api.post(`/api/incidents/${id}/escalate`),
  getAnalysis: (id: string) => api.get(`/api/incidents/${id}/analysis`),
};

export const analyticsAPI = {
  getTrends: (period?: string) => api.get("/api/analytics/trends", { params: { period } }),
  getRiskDistribution: () => api.get("/api/analytics/risk-distribution"),
  getIncidentStats: () => api.get("/api/analytics/stats"),
};

export default api;
