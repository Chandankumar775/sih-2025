/**
 * Analysis Admin Page - Attack Type Analytics
 * Shows comprehensive analytics about attack types and patterns
 */

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Shield, TrendingUp, AlertTriangle, Activity,
  PieChart, BarChart3, Globe, FileWarning,
  MessageSquare, Link2
} from "lucide-react";
import { Layout } from "@/components/Layout";
import { useAuth } from "@/hooks/useAuth";
import axios from "axios";
import { API_BASE_URL } from "@/utils/constants";

interface AttackStats {
  type: string;
  count: number;
  percentage: number;
  severity: { critical: number; high: number; medium: number; low: number };
}

const AnalysisAdmin = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<AttackStats[]>([]);
  const [totalIncidents, setTotalIncidents] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/incidents`);
        const incidents = response.data.incidents;

        // Calculate attack type statistics
        const typeMap: Record<string, any> = {};
        
        incidents.forEach((inc: any) => {
          const type = inc.type || "unknown";
          if (!typeMap[type]) {
            typeMap[type] = {
              type,
              count: 0,
              severity: { critical: 0, high: 0, medium: 0, low: 0 }
            };
          }
          typeMap[type].count++;
          
          const sev = (inc.severity || "low").toLowerCase();
          if (sev in typeMap[type].severity) {
            typeMap[type].severity[sev]++;
          }
        });

        const total = incidents.length;
        const statsArray = Object.values(typeMap).map((item: any) => ({
          ...item,
          percentage: total > 0 ? (item.count / total) * 100 : 0
        }));

        statsArray.sort((a, b) => b.count - a.count);

        setStats(statsArray);
        setTotalIncidents(total);
      } catch (error) {
        console.error("Error fetching analytics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "url": return Link2;
      case "message": return MessageSquare;
      case "file": return FileWarning;
      default: return AlertTriangle;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "url": return "text-blue-500";
      case "message": return "text-purple-500";
      case "file": return "text-orange-500";
      default: return "text-gray-500";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-red-500";
      case "high": return "bg-orange-500";
      case "medium": return "bg-yellow-500";
      case "low": return "bg-green-500";
      default: return "bg-gray-500";
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
            <p className="text-xs text-blue-900 font-medium">Attack Type Analytics | हमला प्रकार विश्लेषण</p>
          </div>
        </div>
      </div>
      
      <div className="gov-container py-8 min-h-screen bg-gradient-to-b from-white to-blue-50">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 font-heading flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-blue-900" />
              Attack Type Analytics
            </h1>
            <p className="text-gray-600 mt-2 flex items-center gap-2">
              <Activity className="h-4 w-4 text-emerald-500" />
              Real-time threat intelligence and pattern analysis
            </p>
          </div>

          {/* Overview Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white border-l-4 border-blue-900 p-6 shadow-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Total Incidents</span>
                <Shield className="h-5 w-5 text-blue-900" />
              </div>
              <div className="text-3xl font-bold text-gray-900">{totalIncidents}</div>
              <div className="text-xs text-emerald-500 mt-1 flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                Live tracking
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white border-l-4 border-purple-600 p-6 shadow-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Attack Types</span>
                <PieChart className="h-5 w-5 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">{stats.length}</div>
              <div className="text-xs text-gray-600 mt-1">Categories detected</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white border-l-4 border-blue-600 p-6 shadow-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Most Common</span>
                <Globe className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-xl font-bold text-gray-900">
                {stats[0]?.type.toUpperCase() || "N/A"}
              </div>
              <div className="text-xs text-gray-600 mt-1">
                {stats[0]?.count || 0} incidents
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white border-l-4 border-emerald-500 p-6 shadow-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Update Interval</span>
                <Activity className="h-5 w-5 text-emerald-500 animate-pulse" />
              </div>
              <div className="text-2xl font-bold text-gray-900">10s</div>
              <div className="text-xs text-gray-600 mt-1">Auto-refresh</div>
            </motion.div>
          </div>

          {/* Attack Type Breakdown */}
          <div className="bg-white border-2 border-gray-300 p-6 mb-8 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-900" />
              Attack Type Distribution
            </h2>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="text-muted-foreground mt-3">Loading analytics...</p>
              </div>
            ) : stats.length === 0 ? (
              <div className="text-center py-12">
                <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">No incidents to analyze yet</p>
              </div>
            ) : (
              <div className="space-y-6">
                {stats.map((stat, index) => {
                  const Icon = getTypeIcon(stat.type);
                  const colorClass = getTypeColor(stat.type);
                  
                  return (
                    <motion.div
                      key={stat.type}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="border-2 border-gray-300 p-4 hover:bg-gray-50 transition-all"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <Icon className={`h-6 w-6 ${colorClass}`} />
                          <div>
                            <h3 className="font-bold text-gray-900 text-lg uppercase">
                              {stat.type}
                            </h3>
                            <p className="text-sm text-gray-600">
                              {stat.count} incidents ({stat.percentage.toFixed(1)}%)
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-gray-900">{stat.count}</div>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="w-full bg-gray-200 h-3 mb-3">
                        <div
                          className={`h-3 ${getSeverityColor("high")}`}
                          style={{ width: `${stat.percentage}%` }}
                        />
                      </div>

                      {/* Severity Breakdown */}
                      <div className="grid grid-cols-4 gap-2">
                        {Object.entries(stat.severity).map(([sev, count]) => (
                          <div key={sev} className="text-center">
                            <div className={`text-xs font-medium mb-1 ${
                              count > 0 ? 'text-gray-900' : 'text-gray-500'
                            }`}>
                              {sev}
                            </div>
                            <div className={`text-sm font-bold px-2 py-1 ${
                              count > 0 ? getSeverityColor(sev) + ' text-white' : 'bg-gray-200 text-gray-500'
                            }`}>
                              {count}
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default AnalysisAdmin;
