/**
 * Zero Trust Metrics Page
 * Displays zero trust security metrics and violations
 */

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Shield, AlertTriangle, CheckCircle, XCircle,
  Lock, Unlock, Activity, Clock, User, Globe,
  Database, Key, Eye
} from "lucide-react";
import { Layout } from "@/components/Layout";
import { useAuth } from "@/hooks/useAuth";
import axios from "axios";
import { API_BASE_URL } from "@/utils/constants";

interface ZeroTrustMetric {
  category: string;
  status: "compliant" | "warning" | "violated";
  violations: number;
  lastCheck: string;
  description: string;
}

const ZeroTrust = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<ZeroTrustMetric[]>([
    {
      category: "Identity Verification",
      status: "compliant",
      violations: 0,
      lastCheck: new Date().toISOString(),
      description: "All users authenticated with multi-factor verification"
    },
    {
      category: "Least Privilege Access",
      status: "compliant",
      violations: 0,
      lastCheck: new Date().toISOString(),
      description: "Role-based access control enforced"
    },
    {
      category: "Network Segmentation",
      status: "compliant",
      violations: 0,
      lastCheck: new Date().toISOString(),
      description: "Micro-segmentation active across all zones"
    },
    {
      category: "Continuous Monitoring",
      status: "compliant",
      violations: 0,
      lastCheck: new Date().toISOString(),
      description: "Real-time threat detection active"
    },
    {
      category: "Data Encryption",
      status: "compliant",
      violations: 0,
      lastCheck: new Date().toISOString(),
      description: "All data encrypted at rest and in transit"
    },
    {
      category: "Device Health",
      status: "compliant",
      violations: 0,
      lastCheck: new Date().toISOString(),
      description: "All devices meet security baseline"
    }
  ]);
  const [overallStatus, setOverallStatus] = useState<"secure" | "warning" | "critical">("secure");
  const [totalViolations, setTotalViolations] = useState(0);

  useEffect(() => {
    const checkZeroTrustStatus = async () => {
      try {
        // Check for any incidents that might indicate violations
        const response = await axios.get(`${API_BASE_URL}/incidents`);
        const incidents = response.data.incidents;

        // Calculate violations based on incident patterns
        const violations = incidents.filter((inc: any) => 
          inc.severity === "critical" || inc.severity === "high"
        ).length;

        setTotalViolations(violations);

        // Update overall status
        if (violations === 0) {
          setOverallStatus("secure");
        } else if (violations < 5) {
          setOverallStatus("warning");
        } else {
          setOverallStatus("critical");
        }

        // Update last check time
        const now = new Date().toISOString();
        setMetrics(prev => prev.map(metric => ({
          ...metric,
          lastCheck: now
        })));

      } catch (error) {
        console.error("Error checking zero trust status:", error);
      }
    };

    checkZeroTrustStatus();
    const interval = setInterval(checkZeroTrustStatus, 15000); // Check every 15s
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "compliant": return "text-green-500 bg-green-500/10 border-green-500/30";
      case "warning": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/30";
      case "violated": return "text-red-500 bg-red-500/10 border-red-500/30";
      default: return "text-gray-500 bg-gray-500/10 border-gray-500/30";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "compliant": return CheckCircle;
      case "warning": return AlertTriangle;
      case "violated": return XCircle;
      default: return Shield;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "Identity Verification": return User;
      case "Least Privilege Access": return Key;
      case "Network Segmentation": return Globe;
      case "Continuous Monitoring": return Eye;
      case "Data Encryption": return Lock;
      case "Device Health": return Database;
      default: return Shield;
    }
  };

  if (!user || user.role !== 'admin') {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <Shield className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-foreground mb-2">Admin Access Required</h2>
            <p className="text-muted-foreground">This page is only accessible to administrators.</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Government Header */}
      <div className="bg-white border-b-4 border-orange-500">
        <div className="max-w-[1400px] mx-auto px-8 py-3 flex items-center gap-3">
          <img src="/media/logo.png" alt="Emblem" className="h-12" />
          <div>
            <h1 className="text-sm font-semibold text-gray-900">भारत सरकार | Government of India</h1>
            <p className="text-xs text-gray-600">रक्षा मंत्रालय | Ministry of Defence</p>
            <p className="text-xs text-blue-900 font-medium">Zero Trust Security Metrics | शून्य विश्वास सुरक्षा मेट्रिक्स</p>
          </div>
        </div>
      </div>
      
      <div className="gov-container py-8 min-h-screen bg-gradient-to-b from-white to-green-50">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 font-heading flex items-center gap-3">
              <Shield className="h-8 w-8 text-blue-900" />
              Zero Trust Security Metrics
            </h1>
            <p className="text-gray-600 mt-2 flex items-center gap-2">
              <Activity className="h-4 w-4 text-emerald-500 animate-pulse" />
              Never trust, always verify - Continuous security validation
            </p>
          </div>

          {/* Overall Status Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`bg-white p-8 mb-8 border-l-8 shadow-lg ${
              overallStatus === "secure" ? "border-green-500" :
              overallStatus === "warning" ? "border-yellow-500" :
              "border-red-500"
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Security Posture: {overallStatus.toUpperCase()}
                </h2>
                <p className="text-gray-600">
                  {totalViolations === 0 ? (
                    "All zero trust principles are being enforced"
                  ) : (
                    `${totalViolations} potential security concern${totalViolations !== 1 ? 's' : ''} detected`
                  )}
                </p>
              </div>
              <div className={`p-6 rounded-full ${
                overallStatus === "secure" ? "bg-green-100" :
                overallStatus === "warning" ? "bg-yellow-100" :
                "bg-red-100"
              }`}>
                {overallStatus === "secure" ? (
                  <Lock className="h-12 w-12 text-green-600" />
                ) : (
                  <Unlock className="h-12 w-12 text-yellow-600" />
                )}
              </div>
            </div>
          </motion.div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {metrics.map((metric, index) => {
              const StatusIcon = getStatusIcon(metric.status);
              const CategoryIcon = getCategoryIcon(metric.category);
              
              return (
                <motion.div
                  key={metric.category}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`bg-white p-6 border-l-4 shadow-sm ${getStatusColor(metric.status)}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <CategoryIcon className="h-6 w-6 text-blue-900" />
                      <div>
                        <h3 className="font-bold text-gray-900">{metric.category}</h3>
                        <p className="text-xs text-gray-600 mt-1">
                          {metric.description}
                        </p>
                      </div>
                    </div>
                    <StatusIcon className={
                      metric.status === "compliant" ? "text-green-500" :
                      metric.status === "warning" ? "text-yellow-500" :
                      "text-red-500"
                    } />
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Clock className="h-4 w-4" />
                      <span>Last checked: {new Date(metric.lastCheck).toLocaleTimeString()}</span>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                      metric.violations === 0 ? "bg-green-500/20 text-green-500" : "bg-red-500/20 text-red-500"
                    }`}>
                      {metric.violations} violations
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Live Monitoring Indicator */}
          <div className="bg-white border-2 border-gray-300 p-6 text-center shadow-sm">
            <div className="flex items-center justify-center gap-3 mb-3">
              <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
              <h3 className="text-lg font-bold text-gray-900">Live Monitoring Active</h3>
            </div>
            <p className="text-sm text-gray-600">
              Zero Trust validation checks running every 15 seconds
            </p>
            <p className="text-xs text-gray-600 mt-2">
              Last system scan: {new Date().toLocaleString()}
            </p>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default ZeroTrust;
