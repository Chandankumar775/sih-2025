/**
 * WatchTower - AI-Powered Cyber Incident Portal for Defence
 * Smart India Hackathon 2025 | Team Urban Dons
 */

import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { lazy, Suspense } from "react";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { ProtectedRoute } from "@/components/ProtectedRoute";

// Pages
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import NotFound from "./pages/NotFound";
import Unauthorized from "./pages/Unauthorized";

// Lazy loaded pages
const Dashboard = lazy(() => import("./pages/Dashboard"));
const ReportIncident = lazy(() => import("./pages/ReportIncident"));
const IncidentDetails = lazy(() => import("./pages/IncidentDetails"));
const Trends = lazy(() => import("./pages/Trends"));

const queryClient = new QueryClient();

const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-background">
    <LoadingSpinner text="Loading..." />
  </div>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Index />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/unauthorized" element={<Unauthorized />} />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute allowedRoles={["analyst", "admin"]}>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/report"
              element={
                <ProtectedRoute allowedRoles={["reporter", "analyst", "admin"]}>
                  <ReportIncident />
                </ProtectedRoute>
              }
            />
            <Route
              path="/incident/:id"
              element={
                <ProtectedRoute allowedRoles={["analyst", "admin"]}>
                  <IncidentDetails />
                </ProtectedRoute>
              }
            />
            <Route
              path="/trends"
              element={
                <ProtectedRoute allowedRoles={["analyst", "admin"]}>
                  <Trends />
                </ProtectedRoute>
              }
            />

            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
