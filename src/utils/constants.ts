/**
 * Application-wide constants for WatchTower
 * Government-grade cyber incident reporting system
 */

export const APP_NAME = "Raksha Netra";
export const APP_TAGLINE = "AI-Powered Cyber Incident Portal for Defence";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export const INCIDENT_TYPES = {
  URL: "url",
  MESSAGE: "message",
  FILE: "file",
} as const;

export const RISK_LEVELS = {
  CRITICAL: { label: "Critical", score: 90, color: "destructive" },
  HIGH: { label: "High", score: 70, color: "orange" },
  MEDIUM: { label: "Medium", score: 40, color: "warning" },
  LOW: { label: "Low", score: 20, color: "success" },
} as const;

export const SEVERITY_BADGES = {
  critical: { label: "Critical", className: "risk-critical" },
  high: { label: "High", className: "risk-high" },
  medium: { label: "Medium", className: "risk-medium" },
  low: { label: "Low", className: "risk-low" },
} as const;

export const NAV_ITEMS = [
  { label: "Dashboard", path: "/dashboard", roles: ["analyst", "admin"] },
  { label: "Report Incident", path: "/report", roles: ["reporter", "analyst", "admin"] },
  { label: "Trends", path: "/trends", roles: ["analyst", "admin"] },
] as const;

export const FILE_TYPES_ALLOWED = [
  "application/pdf",
  "image/jpeg",
  "image/png",
  "image/gif",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
