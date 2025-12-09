import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Search, AlertTriangle, Shield, TrendingUp, Clock, Eye } from "lucide-react";
import { Layout } from "@/components/Layout";
import { useAuth } from "@/hooks/useAuth";
import axios from "axios";
import { useTranslation } from "react-i18next";

const API_BASE_URL = "http://localhost:8000";

interface Incident {
  id: string;
  type: string;
  risk_score: number;
  severity: string;
  summary?: string;
  description?: string;
  content?: string;
  created_at: string;
  status: string;
  geo_region?: string;
}

const Dashboard = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterSeverity, setFilterSeverity] = useState("all");

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchIncidents = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/incidents`);
      setIncidents(response.data.incidents || []);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch incidents:", err);
      setError("Failed to load incidents");
    } finally {
      setLoading(false);
    }
  };

  const filteredIncidents = incidents.filter((incident) => {
    const matchesSearch = 
      (incident.summary?.toLowerCase().includes(searchQuery.toLowerCase()) ||
       incident.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
       incident.content?.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesSeverity = filterSeverity === "all" || incident.severity === filterSeverity;
    
    return matchesSearch && matchesSeverity;
  });

  const stats = {
    total: incidents.length,
    critical: incidents.filter(i => i.severity === "critical").length,
    high: incidents.filter(i => i.severity === "high").length,
    pending: incidents.filter(i => i.status === "pending").length,
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-red-100 text-red-800 border-red-300";
      case "high": return "bg-orange-100 text-orange-800 border-orange-300";
      case "medium": return "bg-yellow-100 text-yellow-800 border-yellow-300";
      default: return "bg-blue-100 text-blue-800 border-blue-300";
    }
  };

  const getTypeIcon = (type: string) => {
    return "🔔";
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b-2 border-orange-500">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-blue-900">
                  {t('dashboard.title', 'Incident Dashboard')}
                </h1>
                <p className="text-gray-600 mt-1">
                  {user?.role === "admin" ? "Administrator View" : "Reporter View"}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-8 h-8 text-orange-500" />
                <span className="text-sm text-gray-600">RakshaNetra</span>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white border-2 border-gray-300 rounded-lg p-6 border-l-4 border-l-blue-900">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Incidents</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
                </div>
                <Shield className="w-10 h-10 text-blue-900" />
              </div>
            </div>

            <div className="bg-white border-2 border-gray-300 rounded-lg p-6 border-l-4 border-l-red-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Critical</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.critical}</p>
                </div>
                <AlertTriangle className="w-10 h-10 text-red-600" />
              </div>
            </div>

            <div className="bg-white border-2 border-gray-300 rounded-lg p-6 border-l-4 border-l-orange-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">High Risk</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.high}</p>
                </div>
                <TrendingUp className="w-10 h-10 text-orange-500" />
              </div>
            </div>

            <div className="bg-white border-2 border-gray-300 rounded-lg p-6 border-l-4 border-l-blue-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Pending</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.pending}</p>
                </div>
                <Clock className="w-10 h-10 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white border-2 border-gray-300 rounded-lg p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Search Incidents
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by description, content..."
                    className="w-full pl-10 pr-4 py-2 border-2 border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-blue-600 text-gray-900"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Filter by Severity
                </label>
                <select
                  value={filterSeverity}
                  onChange={(e) => setFilterSeverity(e.target.value)}
                  className="w-full px-4 py-2 border-2 border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-blue-600 text-gray-900"
                >
                  <option value="all">All Severities</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Incidents Table */}
          <div className="bg-white border-2 border-gray-300 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-300">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">ID</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Type</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Description</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Severity</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Risk Score</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Date</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-12 text-center text-gray-600">
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-6 h-6 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                          Loading incidents...
                        </div>
                      </td>
                    </tr>
                  ) : filteredIncidents.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-12 text-center text-gray-600">
                        No incidents found
                      </td>
                    </tr>
                  ) : (
                    filteredIncidents.map((incident) => (
                      <tr key={incident.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 text-sm text-gray-900 font-mono">
                          #{incident.id.slice(0, 8)}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span className="inline-flex items-center gap-1 text-gray-700">
                            {getTypeIcon(incident.type)} {incident.type}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                          {incident.summary || incident.description || incident.content || "No description"}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(incident.severity)}`}>
                            {incident.severity?.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span className="font-bold text-gray-900">{incident.risk_score}/100</span>
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                            {incident.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {new Date(incident.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <Link
                            to={`/incident/${incident.id}`}
                            className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium"
                          >
                            <Eye className="w-4 h-4" />
                            View
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Summary Footer */}
          <div className="mt-6 bg-white border-2 border-gray-300 rounded-lg p-4">
            <p className="text-sm text-gray-600 text-center">
              Showing {filteredIncidents.length} of {incidents.length} total incidents
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
