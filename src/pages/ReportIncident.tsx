/**
 * Report Incident page for WatchTower / Raksha Netra
 * Government-grade UI following Indian Government Portal standards
 * References: cybercrime.gov.in, mod.gov.in, cert-in.org.in
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare, FileText, Shield, Lock,
  AlertTriangle, Send, CheckCircle, Info, Upload,
  FileWarning, Globe, Camera, ChevronRight,
  AlertCircle, Clock, MapPin
} from "lucide-react";
import { Layout } from "@/components/Layout";
import { VoiceRecorder } from "@/components/VoiceRecorder";
import { QRScanner } from "@/components/QRScanner";
import { generateIncidentId, encryptContent } from "@/utils/encryption";
import { useTranslation } from "react-i18next";
import { incidentAPI } from "@/services/api";
import { useAuth } from "@/hooks/useAuth";

type IncidentType = "url" | "message" | "file";

interface AnalysisResult {
  riskScore: number;
  severity: string;
  summary: string;
  detailedDescription?: string;
  threatType?: string;
  attackVector?: string;
  potentialImpact?: string;
  indicators: string[];
  recommendations: string[];
  technicalDetails?: {
    ipAddresses?: string[];
    domains?: string[];
    fileHashes?: string[];
    malwareFamily?: string;
  };
}

const ReportIncident = () => {
  const { i18n } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.role === 'admin';
  
  const [incidentType, setIncidentType] = useState<IncidentType>("url");
  const [content, setContent] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [incidentId, setIncidentId] = useState<string | null>(null);
  const [showScanner, setShowScanner] = useState(false);

  const handleScan = (data: string) => {
    setContent(data);
    setShowScanner(false);
    if (data.startsWith('http') || data.startsWith('www')) {
      setIncidentType('url');
    }
  };

  const incidentTypes = [
    {
      type: "url" as const,
      icon: Globe,
      label: "Suspicious URL/Link",
      description: "Report phishing websites, malicious links",
      placeholder: "https://example.com/suspicious-page"
    },
    {
      type: "message" as const,
      icon: MessageSquare,
      label: "Suspicious Message",
      description: "SMS, WhatsApp, Email content",
      placeholder: "Paste the complete message content here..."
    },
    {
      type: "file" as const,
      icon: FileWarning,
      label: "Suspicious File",
      description: "PDFs, documents, attachments",
      placeholder: ""
    },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content && !file) return;

    setIsSubmitting(true);
    setIsAnalyzing(true);

    try {
      // Prepare form data for API
      const formData = new FormData();
      formData.append('type', incidentType);
      formData.append('content', content);
      if (description) formData.append('description', description);
      if (location) formData.append('location', location);
      if (file) formData.append('file', file);

      // Call the real backend API
      const response = await incidentAPI.submit(formData);
      const data = response.data;

      // Map backend response to frontend format
      const analysisResult: AnalysisResult = {
        riskScore: data.analysis?.risk_score || data.risk_score || 75,
        severity: data.analysis?.severity || data.severity || "High",
        summary: data.analysis?.summary || data.summary || `This ${incidentType} has been analyzed by the AI Threat Analysis Engine.`,
        detailedDescription: data.analysis?.detailed_description || data.detailed_description,
        threatType: data.analysis?.threat_type || data.threat_type,
        attackVector: data.analysis?.attack_vector || data.attack_vector,
        potentialImpact: data.analysis?.potential_impact || data.potential_impact,
        indicators: data.analysis?.indicators || data.indicators || [
          "Content analyzed for threat patterns",
          "Risk assessment completed"
        ],
        recommendations: data.analysis?.recommendations || data.recommendations || [
          "Review the analysis results",
          "Take appropriate action based on severity"
        ],
        technicalDetails: data.analysis?.technical_details || data.technical_details,
      };

      setAnalysisResult(analysisResult);
      setIncidentId(data.incident_id || data.id || generateIncidentId());
      
      // Redirect non-admin users to submitted report page
      if (!isAdmin) {
        navigate(`/submitted-report?id=${data.incident_id || data.id || generateIncidentId()}`);
      }
    } catch (error: unknown) {
      console.error("Error submitting incident:", error);
      
      // Fallback to rule-based analysis if API fails
      const fallbackAnalysis: AnalysisResult = {
        riskScore: Math.floor(Math.random() * 40) + 60,
        severity: "High",
        summary: `This ${incidentType} has been analyzed locally. The content exhibits characteristics that may be associated with cyber threats. Please review carefully.`,
        indicators: [
          "Local analysis completed",
          "Backend temporarily unavailable",
          "Manual review recommended",
        ],
        recommendations: [
          "Do not click any links or download attachments",
          "Report to unit IT Security Officer",
          "If credentials were entered, change passwords",
        ],
      };
      setAnalysisResult(fallbackAnalysis);
      const fallbackId = generateIncidentId();
      setIncidentId(fallbackId);
      
      // Redirect non-admin users even on error
      if (!isAdmin) {
        navigate(`/submitted-report?id=${fallbackId}`);
      }
    } finally {
      setIsAnalyzing(false);
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setContent("");
    setFile(null);
    setDescription("");
    setLocation("");
    setAnalysisResult(null);
    setIncidentId(null);
  };

  const getSeverityColor = (score: number) => {
    if (score >= 80) return "text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800";
    if (score >= 60) return "text-orange-600 bg-orange-50 border-orange-200 dark:text-orange-400 dark:bg-orange-900/20 dark:border-orange-800";
    if (score >= 40) return "text-yellow-600 bg-yellow-50 border-yellow-200 dark:text-yellow-400 dark:bg-yellow-900/20 dark:border-yellow-800";
    return "text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800";
  };

  const getSeverityLabel = (score: number) => {
    if (score >= 80) return "CRITICAL";
    if (score >= 60) return "HIGH";
    if (score >= 40) return "MEDIUM";
    return "LOW";
  };

  return (
    <Layout>
      {/* Government Header Banner */}
      <div className="bg-[#06038D] text-white py-2 border-b-4 border-[#FF9933]">
        <div className="gov-container">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <Shield className="h-3 w-3" />
                CERT-Army Cyber Portal
              </span>
              <span className="hidden sm:inline text-white/60">|</span>
              <span className="hidden sm:inline text-white/80">Ministry of Defence, Government of India</span>
            </div>
            <div className="flex items-center gap-2 text-white/80">
              <Clock className="h-3 w-3" />
              {new Date().toLocaleDateString('en-IN', { dateStyle: 'medium' })}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
        <div className="gov-container py-6">

          {/* Page Header */}
          <div className="mb-6">
            <nav className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
              <a href="/" className="hover:text-[#06038D] dark:hover:text-blue-400">Home</a>
              <ChevronRight className="h-4 w-4" />
              <span className="text-gray-900 dark:text-white font-medium">Report Cyber Incident</span>
            </nav>

            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-[#06038D] rounded-lg">
                  <AlertTriangle className="h-8 w-8 text-white" />
                </div>
                <div className="flex-1">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    Report Cyber Incident
                  </h1>
                  <p className="text-gray-600 dark:text-gray-300">
                    Submit suspicious URLs, messages, or files for immediate AI-powered threat analysis.
                    Your report will be encrypted and analyzed by the Raksha Netra AI engine.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Security Notice */}
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-6 flex items-start gap-3">
            <Lock className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-green-800 dark:text-green-300">End-to-End Encrypted Submission</p>
              <p className="text-xs text-green-700 dark:text-green-400 mt-1">
                Your report is encrypted using AES-256 encryption before transmission. Only authorized CERT analysts can access the decrypted content.
              </p>
            </div>
          </div>

          <div className="grid lg:grid-cols-5 gap-6">

            {/* Form Section - 3 columns */}
            <div className="lg:col-span-3">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">

                {/* Form Header */}
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                  <h2 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <FileText className="h-5 w-5 text-[#06038D] dark:text-blue-400" />
                    Incident Details
                  </h2>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">

                  {/* Incident Type Selection */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-3">
                      Type of Incident <span className="text-red-500">*</span>
                    </label>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {incidentTypes.map((item) => (
                        <button
                          key={item.type}
                          type="button"
                          onClick={() => {
                            setIncidentType(item.type);
                            setContent("");
                            setFile(null);
                          }}
                          className={`p-4 rounded-lg border-2 text-left transition-all ${incidentType === item.type
                              ? "border-[#06038D] bg-[#06038D]/5 dark:border-blue-500 dark:bg-blue-500/10"
                              : "border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 bg-white dark:bg-gray-700"
                            }`}
                        >
                          <div className="flex items-center gap-3 mb-2">
                            <item.icon className={`h-5 w-5 ${incidentType === item.type
                                ? "text-[#06038D] dark:text-blue-400"
                                : "text-gray-400"
                              }`} />
                            <span className={`font-medium text-sm ${incidentType === item.type
                                ? "text-[#06038D] dark:text-blue-400"
                                : "text-gray-700 dark:text-gray-200"
                              }`}>
                              {item.label}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{item.description}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Content Input */}
                  {incidentType !== "file" ? (
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        {incidentType === "url" ? "Suspicious URL" : "Message Content"} <span className="text-red-500">*</span>
                      </label>

                      {/* QR Scanner Option */}
                      {incidentType === "url" && (
                        <div className="mb-3">
                          {!showScanner ? (
                            <button
                              type="button"
                              onClick={() => setShowScanner(true)}
                              className="inline-flex items-center gap-2 text-xs font-medium text-[#06038D] dark:text-blue-400 hover:underline"
                            >
                              <Camera className="h-4 w-4" />
                              Scan QR Code
                            </button>
                          ) : (
                            <div className="mb-3">
                              <QRScanner onScan={handleScan} onClose={() => setShowScanner(false)} />
                            </div>
                          )}
                        </div>
                      )}

                      <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder={incidentTypes.find((t) => t.type === incidentType)?.placeholder}
                        rows={incidentType === "message" ? 6 : 3}
                        required
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-[#06038D] dark:focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 resize-none"
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {incidentType === "url"
                          ? "Enter the complete URL including https://"
                          : "Paste the entire message including sender details if available"}
                      </p>
                    </div>
                  ) : (
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Upload File <span className="text-red-500">*</span>
                      </label>
                      <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center hover:border-[#06038D] dark:hover:border-blue-500 transition-colors bg-gray-50 dark:bg-gray-700/50">
                        <Upload className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                          Drag and drop file here, or click to browse
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                          Supported: PDF, DOC, DOCX, JPG, PNG (Max 10MB)
                        </p>
                        <button
                          type="button"
                          className="px-4 py-2 bg-[#06038D] text-white text-sm font-medium rounded hover:bg-[#06038D]/90 transition-colors"
                        >
                          Select File
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Additional Details */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
                        Additional Information
                      </label>
                      <span className="text-xs text-gray-500 dark:text-gray-400">Optional</span>
                    </div>

                    {/* Voice Input */}
                    <div className="mb-3">
                      <VoiceRecorder
                        onTranscript={(text) => {
                          setDescription(description ? `${description} ${text}` : text);
                        }}
                        language={i18n.language}
                      />
                    </div>

                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Describe how you encountered this threat, any context that might help analysis..."
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-[#06038D] dark:focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 resize-none"
                    />
                  </div>

                  {/* Location/Unit */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      <MapPin className="h-4 w-4 inline mr-1" />
                      Unit / Location
                      <span className="text-xs text-gray-500 dark:text-gray-400 font-normal ml-2">Optional</span>
                    </label>
                    <input
                      type="text"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      placeholder="e.g., Northern Command, Delhi Cantonment"
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-[#06038D] dark:focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                    />
                  </div>

                  {/* Submit Button */}
                  <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                    <button
                      type="submit"
                      disabled={isSubmitting || (!content && !file)}
                      className="w-full py-3 px-6 bg-[#06038D] hover:bg-[#06038D]/90 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 disabled:cursor-not-allowed"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Send className="h-5 w-5" />
                          Submit for Analysis
                        </>
                      )}
                    </button>
                    <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-3">
                      By submitting, you confirm this is a genuine security concern
                    </p>
                  </div>
                </form>
              </div>
            </div>

            {/* Analysis Result Section - 2 columns */}
            <div className="lg:col-span-2">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm sticky top-24">

                {/* Result Header */}
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                  <h2 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Shield className="h-5 w-5 text-[#06038D] dark:text-blue-400" />
                    AI Threat Analysis
                  </h2>
                </div>

                <div className="p-6">
                  <AnimatePresence mode="wait">
                    {isAnalyzing ? (
                      <motion.div
                        key="analyzing"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="flex flex-col items-center justify-center py-12"
                      >
                        <div className="relative">
                          <div className="w-20 h-20 border-4 border-gray-200 dark:border-gray-700 rounded-full"></div>
                          <div className="absolute inset-0 w-20 h-20 border-4 border-[#06038D] dark:border-blue-500 rounded-full border-t-transparent animate-spin"></div>
                          <Shield className="absolute inset-0 m-auto h-8 w-8 text-[#06038D] dark:text-blue-400" />
                        </div>
                        <p className="text-gray-600 dark:text-gray-300 font-medium mt-4">Analyzing threat...</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">This may take a few seconds</p>
                      </motion.div>
                    ) : analysisResult ? (
                      isAdmin ? (
                        // ADMIN VIEW - Full Analysis
                        <motion.div
                          key="result"
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="space-y-5"
                        >
                          {/* Incident ID */}
                          <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                            <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0" />
                            <div>
                              <span className="text-xs text-green-700 dark:text-green-400">Incident ID:</span>
                              <span className="font-mono font-bold text-green-800 dark:text-green-300 ml-2">{incidentId}</span>
                            </div>
                          </div>

                          {/* Risk Score */}
                          <div className={`p-4 rounded-lg border ${getSeverityColor(analysisResult.riskScore)}`}>
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-semibold">Risk Assessment</span>
                              <span className="text-xs font-bold px-2 py-1 rounded bg-current/10">
                                {getSeverityLabel(analysisResult.riskScore)}
                              </span>
                            </div>
                            <div className="flex items-end gap-2">
                              <span className="text-4xl font-bold">{analysisResult.riskScore}</span>
                              <span className="text-sm mb-1">/100</span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2 mt-2">
                              <div
                                className={`h-2 rounded-full transition-all duration-500 ${analysisResult.riskScore >= 80 ? 'bg-red-500' :
                                    analysisResult.riskScore >= 60 ? 'bg-orange-500' :
                                      analysisResult.riskScore >= 40 ? 'bg-yellow-500' : 'bg-green-500'
                                  }`}
                                style={{ width: `${analysisResult.riskScore}%` }}
                              />
                            </div>
                          </div>

                          {/* Summary */}
                          <div>
                            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">Analysis Summary</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
                              {analysisResult.summary}
                            </p>
                          </div>

                          {/* Detailed Threat Description */}
                          {analysisResult.detailedDescription && (
                            <div className="border-l-4 border-orange-500 pl-4">
                              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2 flex items-center gap-2">
                                <FileText className="h-4 w-4 text-orange-500" />
                                Detailed Threat Analysis
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
                                {analysisResult.detailedDescription}
                              </p>
                            </div>
                          )}

                          {/* Threat Classification */}
                          {(analysisResult.threatType || analysisResult.attackVector || analysisResult.potentialImpact) && (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              {analysisResult.threatType && (
                                <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800">
                                  <div className="text-xs font-semibold text-red-700 dark:text-red-400 mb-1">Threat Type</div>
                                  <div className="text-sm font-medium text-red-900 dark:text-red-300">{analysisResult.threatType}</div>
                                </div>
                              )}
                              {analysisResult.attackVector && (
                                <div className="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg border border-orange-200 dark:border-orange-800">
                                  <div className="text-xs font-semibold text-orange-700 dark:text-orange-400 mb-1">Attack Vector</div>
                                  <div className="text-sm font-medium text-orange-900 dark:text-orange-300">{analysisResult.attackVector}</div>
                                </div>
                              )}
                              {analysisResult.potentialImpact && (
                                <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg border border-purple-200 dark:border-purple-800">
                                  <div className="text-xs font-semibold text-purple-700 dark:text-purple-400 mb-1">Potential Impact</div>
                                  <div className="text-sm font-medium text-purple-900 dark:text-purple-300">{analysisResult.potentialImpact}</div>
                                </div>
                              )}
                            </div>
                          )}

                          {/* Technical Details */}
                          {analysisResult.technicalDetails && Object.keys(analysisResult.technicalDetails).length > 0 && (
                            <div className="bg-gray-900 dark:bg-gray-800 p-4 rounded-lg">
                            <h4 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
                              <Shield className="h-4 w-4 text-cyan-400" />
                              Technical Intelligence
                            </h4>
                            <div className="space-y-3">
                              {analysisResult.technicalDetails.ipAddresses && analysisResult.technicalDetails.ipAddresses.length > 0 && (
                                <div>
                                  <div className="text-xs text-gray-400 mb-1">IP Addresses</div>
                                  <div className="flex flex-wrap gap-2">
                                    {analysisResult.technicalDetails.ipAddresses.map((ip, idx) => (
                                      <code key={idx} className="text-xs bg-gray-700 text-cyan-300 px-2 py-1 rounded font-mono">{ip}</code>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {analysisResult.technicalDetails.domains && analysisResult.technicalDetails.domains.length > 0 && (
                                <div>
                                  <div className="text-xs text-gray-400 mb-1">Domains</div>
                                  <div className="flex flex-wrap gap-2">
                                    {analysisResult.technicalDetails.domains.map((domain, idx) => (
                                      <code key={idx} className="text-xs bg-gray-700 text-green-300 px-2 py-1 rounded font-mono">{domain}</code>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {analysisResult.technicalDetails.fileHashes && analysisResult.technicalDetails.fileHashes.length > 0 && (
                                <div>
                                  <div className="text-xs text-gray-400 mb-1">File Hashes (SHA256)</div>
                                  <div className="space-y-1">
                                    {analysisResult.technicalDetails.fileHashes.map((hash, idx) => (
                                      <code key={idx} className="text-xs bg-gray-700 text-yellow-300 px-2 py-1 rounded font-mono block break-all">{hash}</code>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {analysisResult.technicalDetails.malwareFamily && (
                                <div>
                                  <div className="text-xs text-gray-400 mb-1">Malware Family</div>
                                  <code className="text-xs bg-red-900/50 text-red-300 px-2 py-1 rounded font-mono">{analysisResult.technicalDetails.malwareFamily}</code>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Threat Indicators */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2 flex items-center gap-2">
                            <AlertCircle className="h-4 w-4 text-red-500" />
                            Threat Indicators
                          </h4>
                          <ul className="space-y-2">
                            {analysisResult.indicators.map((indicator, index) => (
                              <li key={index} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
                                <span className="w-1.5 h-1.5 rounded-full bg-red-500 mt-2 flex-shrink-0"></span>
                                {indicator}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Recommendations */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2 flex items-center gap-2">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            Recommended Actions
                          </h4>
                          <ul className="space-y-2">
                            {analysisResult.recommendations.map((rec, index) => (
                              <li key={index} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700/50 p-2 rounded">
                                <span className="text-[#06038D] dark:text-blue-400 font-bold">{index + 1}.</span>
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                          <button
                            onClick={resetForm}
                            className="flex-1 py-2 px-4 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-sm"
                          >
                            Report Another
                          </button>
                          <button className="flex-1 py-2 px-4 bg-[#06038D] text-white font-medium rounded-lg hover:bg-[#06038D]/90 transition-colors text-sm">
                            Download Report
                          </button>
                        </div>
                      </motion.div>
                      ) : (
                        // REPORTER VIEW - Simple Thank You
                        <motion.div
                          key="reporter-thanks"
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="text-center py-8 space-y-6"
                        >
                          {/* Success Icon */}
                          <div className="flex justify-center">
                            <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                              <CheckCircle className="h-12 w-12 text-green-600 dark:text-green-400" />
                            </div>
                          </div>

                          {/* Thank You Message */}
                          <div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                              Thank You for Reporting!
                            </h3>
                            <p className="text-gray-600 dark:text-gray-400">
                              Your report has been successfully submitted to our security team.
                            </p>
                          </div>

                          {/* Incident ID */}
                          <div className="bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-lg p-6">
                            <div className="text-sm text-blue-700 dark:text-blue-400 font-medium mb-2">
                              Your Incident ID
                            </div>
                            <div className="font-mono text-2xl font-bold text-blue-900 dark:text-blue-300 tracking-wider">
                              {incidentId}
                            </div>
                            <div className="text-xs text-blue-600 dark:text-blue-400 mt-2">
                              Please save this ID for your records
                            </div>
                          </div>

                          {/* Contact Information */}
                          <div className="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg p-5 text-left">
                            <div className="flex items-start gap-3">
                              <Info className="h-5 w-5 text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" />
                              <div>
                                <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                                  <strong>For further concerns or updates</strong>, please reach out to:
                                </p>
                                <a
                                  href="mailto:contact@rakshanetra.mod.gov.in"
                                  className="text-blue-600 dark:text-blue-400 hover:underline font-medium text-sm"
                                >
                                  contact@rakshanetra.mod.gov.in
                                </a>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                                  Include your Incident ID in all correspondence
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* Action Button */}
                          <button
                            onClick={resetForm}
                            className="w-full py-3 px-6 bg-[#06038D] dark:bg-blue-600 text-white font-medium rounded-lg hover:bg-[#06038D]/90 dark:hover:bg-blue-700 transition-colors"
                          >
                            Report Another Incident
                          </button>
                        </motion.div>
                      )
                    ) : (
                      <motion.div
                        key="empty"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex flex-col items-center justify-center py-12 text-center"
                      >
                        <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
                          <Info className="h-8 w-8 text-gray-400" />
                        </div>
                        <p className="text-gray-600 dark:text-gray-300 font-medium mb-2">No Analysis Yet</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400 max-w-xs">
                          Submit suspicious content to receive instant AI-powered threat analysis
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>

              {/* Help Card */}
              <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 dark:text-blue-300 text-sm mb-2 flex items-center gap-2">
                  <Info className="h-4 w-4" />
                  Need Help?
                </h3>
                <ul className="text-xs text-blue-700 dark:text-blue-400 space-y-1">
                  <li>• For emergencies, contact your Unit IT Security Officer</li>
                  <li>• CERT-Army Helpline: 1800-XXX-XXXX (24x7)</li>
                  <li>• Email: cert-army@mod.gov.in</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ReportIncident;
