/**
 * Analyst Dashboard for WatchTower
 * Displays incident list with filtering and severity indicators
 */

import { useState, useMemo, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search, Filter, AlertTriangle, Link2, MessageSquare, FileText,
  ChevronRight, Calendar, Clock, Shield, TrendingUp, X
} from "lucide-react";
import { Layout } from "@/components/Layout";
import { useAuth } from "@/hooks/useAuth";
import { LiveThreatMap } from "@/components/LiveThreatMap";
import axios from "axios";
import { API_BASE_URL } from "@/utils/constants";

interface Incident {
  id: string;
  type: "url" | "message" | "file" | "sms" | "email" | "social_media";
  riskScore: number;
  risk_score?: number;
  severity: "critical" | "high" | "medium" | "low";
  summary?: string;
  description?: string;
  content?: string;
  reportedBy?: string;
  createdAt: string;
  created_at?: string;
  status: "pending" | "reviewed" | "escalated" | "investigating" | "resolved";
  geo_region?: string;
  frequency_count?: number;
  military_relevant?: number;
  escalated_flag?: number;
}

const Dashboard = () => {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch real incidents from backend
  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await axios.get(`${API_BASE_URL}/incidents`);
        
        // Transform backend data to match frontend interface
        const transformedIncidents = response.data.incidents.map((inc: any) => ({
          id: inc.id,
          type: inc.type,
          riskScore: inc.risk_score || 0,
          severity: inc.severity || "low",
          summary: inc.description || inc.content?.substring(0, 100) + "..." || "No description",
          reportedBy: inc.unit_name || inc.geo_region || "Citizen Report",
          createdAt: inc.created_at,
          status: inc.status || "pending",
          geo_region: inc.geo_region,
          frequency_count: inc.frequency_count,
          military_relevant: inc.military_relevant,
          escalated_flag: inc.escalated_flag,
          content: inc.content,
          description: inc.description
        }));
        
        setIncidents(transformedIncidents);
      } catch (err: any) {
        console.error("Error fetching incidents:", err);
        setError(err.response?.data?.detail || "Failed to load incidents. Please ensure backend is running.");
        // Fallback to empty array
        setIncidents([]);
      } finally {
        setLoading(false);
      }
    };

    fetchIncidents();
    // Refresh every 30 seconds
    const interval = setInterval(fetchIncidents, 30000);
    return () => clearInterval(interval);
  }, []);

  const filteredIncidents = useMemo(() => {
    return incidents.filter((incident) => {
      const matchesSearch =
        incident.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (incident.summary?.toLowerCase().includes(searchQuery.toLowerCase()) || false) ||
        (incident.content?.toLowerCase().includes(searchQuery.toLowerCase()) || false);
      const matchesType = typeFilter === "all" || incident.type === typeFilter;
      const matchesSeverity = severityFilter === "all" || incident.severity === severityFilter;
      return matchesSearch && matchesType && matchesSeverity;
    });
  }, [incidents, searchQuery, typeFilter, severityFilter]);

  const stats = {
    total: incidents.length,
    critical: incidents.filter((i) => i.severity === "critical").length,
    pending: incidents.filter((i) => i.status === "pending").length,
    escalated: incidents.filter((i) => i.escalated_flag === 1).length,
    military: incidents.filter((i) => i.military_relevant === 1).length,
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "url": return Link2;
      case "message": return MessageSquare;
      case "file": return FileText;
      default: return AlertTriangle;
    }
  };

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-destructive/10 text-destructive border-destructive/30";
      case "high": return "bg-orange-500/10 text-orange-500 border-orange-500/30";
      case "medium": return "bg-yellow-500/10 text-yellow-500 border-yellow-500/30";
      case "low": return "bg-emerald-500/10 text-emerald-500 border-emerald-500/30";
      default: return "bg-muted text-muted-foreground";
    }
  };

  const getStatusStyles = (status: string) => {
    switch (status) {
      case "pending": return "bg-yellow-500/10 text-yellow-500";
      case "reviewed": return "bg-primary/10 text-primary";
      case "escalated": return "bg-destructive/10 text-destructive";
      default: return "bg-muted text-muted-foreground";
    }
  };

  return (
    <Layout>
      <div className="gov-container py-8 min-h-screen">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
            {error && (
              <div className="w-full mb-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-destructive mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-destructive mb-1">Backend Connection Error</h3>
                    <p className="text-sm text-muted-foreground">{error}</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      Make sure backend is running: <code className="bg-muted px-2 py-1 rounded">python backend/server.py</code>
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
            <div>
              <h1 className="text-3xl font-bold text-foreground font-heading">
                Incident Triage Dashboard
              </h1>
              <p className="text-muted-foreground mt-1 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Live Monitoring Active
              </p>
            </div>
            <Link to="/report" className="cyber-button-accent flex items-center gap-2 self-start">
              <AlertTriangle className="h-4 w-4" />
              Report New Incident
            </Link>
          </div>

          {/* Impact Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass-card p-6 flex flex-col justify-between group relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <Shield className="h-16 w-16 text-primary" />
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-primary/10 rounded-lg border border-primary/20">
                  <Shield className="h-5 w-5 text-primary" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">Total Incidents</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground font-heading mb-1">
                  {stats.total}
                </div>
                <div className="text-xs text-emerald-500 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" />
                  +12% from last week
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass-card p-6 flex flex-col justify-between group relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <AlertTriangle className="h-16 w-16 text-destructive" />
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-destructive/10 rounded-lg border border-destructive/20">
                  <AlertTriangle className="h-5 w-5 text-destructive" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">Critical Threats</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground font-heading mb-1">
                  {stats.critical}
                </div>
                <div className="text-xs text-destructive flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  Immediate action required
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass-card p-6 flex flex-col justify-between group relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <div className="text-6xl font-bold text-emerald-500">₹</div>
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                  <TrendingUp className="h-5 w-5 text-emerald-500" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">Fraud Prevented</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground font-heading mb-1">
                  ₹50.2 Cr
                </div>
                <div className="text-xs text-emerald-500 flex items-center gap-1">
                  <Shield className="h-3 w-3" />
                  Est. savings this year
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="glass-card p-6 flex flex-col justify-between group relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <div className="text-6xl font-bold text-blue-500">👨‍👩‍👧‍👦</div>
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                  <Shield className="h-5 w-5 text-blue-500" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">Families Protected</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground font-heading mb-1">
                  10,450+
                </div>
                <div className="text-xs text-blue-500 flex items-center gap-1">
                  <Shield className="h-3 w-3" />
                  Across 5 commands
                </div>
              </div>
            </motion.div>
          </div>

          {/* Live Threat Map */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-foreground font-heading mb-4 flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              Live Threat Visualization
            </h2>
            <LiveThreatMap />
          </div>

          {/* Filters */}
          <div className="glass-panel rounded-xl p-4 mb-6">
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by ID or summary..."
                  className="cyber-input pl-10"
                />
              </div>

              {/* Type Filter */}
              <div className="flex items-center gap-2">
                <Filter className="h-5 w-5 text-muted-foreground" />
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="cyber-input py-2"
                >
                  <option value="all">All Types</option>
                  <option value="url">URL</option>
                  <option value="message">Message</option>
                  <option value="file">File</option>
                </select>
              </div>

              {/* Severity Filter */}
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="cyber-input py-2"
              >
                <option value="all">All Severity</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>

          {/* Incidents Table */}
          <div className="glass-card overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10 bg-white/5">
                    <th className="text-left py-4 px-6 text-sm font-medium text-muted-foreground">
                      Incident ID
                    </th>
                    <th className="text-left py-4 px-6 text-sm font-medium text-muted-foreground">
                      Type
                    </th>
                    <th className="text-left py-4 px-6 text-sm font-medium text-muted-foreground">
                      Risk Score
                    </th>
                    <th className="text-left py-4 px-6 text-sm font-medium text-muted-foreground">
                      Severity
                    </th>
                    <th className="text-left py-4 px-6 text-sm font-medium text-muted-foreground">
                      Status
                    </th>
                    <th className="text-left py-4 px-6 text-sm font-medium text-muted-foreground">
                      Date
                    </th>
                    <th className="text-left py-4 px-6 text-sm font-medium text-muted-foreground"></th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan={7} className="py-12 px-6 text-center">
                        <div className="flex flex-col items-center gap-3">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                          <p className="text-muted-foreground">Loading incidents from backend...</p>
                        </div>
                      </td>
                    </tr>
                  ) : filteredIncidents.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-12 px-6 text-center">
                        <div className="flex flex-col items-center gap-3">
                          <AlertTriangle className="h-12 w-12 text-muted-foreground/50" />
                          <p className="text-muted-foreground">No incidents found. Submit your first report!</p>
                          <Link to="/report" className="cyber-button-primary mt-2">
                            Report Incident
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    <AnimatePresence>
                      {filteredIncidents.map((incident, index) => {
                      const TypeIcon = getTypeIcon(incident.type);
                      return (
                        <motion.tr
                          key={incident.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="border-b border-white/5 hover:bg-white/5 transition-all duration-300 cursor-pointer group"
                          onClick={() => setSelectedIncident(incident)}
                        >
                          <td className="py-4 px-6">
                            <span className="font-mono text-sm text-primary/80 group-hover:text-primary transition-colors">
                              {incident.id}
                            </span>
                          </td>
                          <td className="py-4 px-6">
                            <div className="flex items-center gap-2">
                              <TypeIcon className="h-4 w-4 text-muted-foreground" />
                              <span className="capitalize text-sm text-foreground">{incident.type}</span>
                            </div>
                          </td>
                          <td className="py-4 px-6">
                            <div className="flex items-center gap-2">
                              <div className="w-16 h-2 bg-secondary rounded-full overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${incident.riskScore > 80 ? "bg-destructive" :
                                    incident.riskScore > 50 ? "bg-orange-500" : "bg-emerald-500"
                                    }`}
                                  style={{ width: `${incident.riskScore}%` }}
                                />
                              </div>
                              <span className="font-semibold text-foreground text-sm">
                                {incident.riskScore}
                              </span>
                            </div>
                          </td>
                          <td className="py-4 px-6">
                            <span
                              className={`px-2 py-1 text-xs font-medium rounded border capitalize ${getSeverityStyles(
                                incident.severity
                              )}`}
                            >
                              {incident.severity}
                            </span>
                          </td>
                          <td className="py-4 px-6">
                            <span
                              className={`px-2 py-1 text-xs font-medium rounded capitalize ${getStatusStyles(
                                incident.status
                              )}`}
                            >
                              {incident.status}
                            </span>
                          </td>
                          <td className="py-4 px-6">
                            <div className="flex items-center gap-1 text-sm text-muted-foreground">
                              <Calendar className="h-3 w-3" />
                              {new Date(incident.createdAt).toLocaleDateString()}
                            </div>
                          </td>
                          <td className="py-4 px-6">
                            <div
                              className="p-2 hover:bg-white/10 rounded-lg inline-flex transition-all duration-300 hover:scale-110"
                            >
                              <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                            </div>
                          </td>
                        </motion.tr>
                      );
                      })}
                    </AnimatePresence>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Quick View Modal */}
          <AnimatePresence>
            {selectedIncident && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
                onClick={() => setSelectedIncident(null)}
              >
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="glass-panel rounded-xl shadow-2xl max-w-lg w-full p-6 border border-white/10"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h3 className="text-xl font-bold text-foreground font-heading">
                        {selectedIncident.id}
                      </h3>
                      <span
                        className={`inline-block mt-2 px-2 py-1 text-xs font-medium rounded border capitalize ${getSeverityStyles(
                          selectedIncident.severity
                        )}`}
                      >
                        {selectedIncident.severity} Risk
                      </span>
                    </div>
                    <button
                      onClick={() => setSelectedIncident(null)}
                      className="text-muted-foreground hover:text-foreground hover:bg-white/10 rounded-lg p-1 transition-colors"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>

                  <div className="bg-white/5 rounded-lg p-4 mb-6 border border-white/5">
                    <p className="text-sm text-foreground leading-relaxed">
                      {selectedIncident.summary}
                    </p>
                  </div>

                  <div className="space-y-4 text-sm mb-8">
                    <div className="flex justify-between items-center py-2 border-b border-white/5">
                      <span className="text-muted-foreground">Reported by</span>
                      <span className="text-foreground font-medium">{selectedIncident.reportedBy}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/5">
                      <span className="text-muted-foreground">Risk Score</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-secondary rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${selectedIncident.riskScore > 80 ? "bg-destructive" :
                              selectedIncident.riskScore > 50 ? "bg-orange-500" : "bg-emerald-500"
                              }`}
                            style={{ width: `${selectedIncident.riskScore}%` }}
                          />
                        </div>
                        <span className="font-bold text-foreground">
                          {selectedIncident.riskScore}/100
                        </span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/5">
                      <span className="text-muted-foreground">Timestamp</span>
                      <span className="text-foreground font-medium">
                        {new Date(selectedIncident.createdAt).toLocaleString()}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <Link
                      to={`/incident/${selectedIncident.id}`}
                      className="flex-1 cyber-button-primary text-center text-sm"
                    >
                      View Full Details
                    </Link>
                    <button className="flex-1 px-4 py-3 rounded-lg border border-white/10 text-foreground font-medium hover:bg-white/5 transition-all duration-300 text-sm">
                      Escalate to CERT
                    </button>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </Layout>
  );
};

export default Dashboard;
