/**
 * Incident Details page for WatchTower
 * Full incident analysis and forensic report
 */

import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft, Shield, AlertTriangle, Download, Send, Clock,
  User, MapPin, Link2, FileText, CheckCircle, ExternalLink, Activity
} from "lucide-react";
import { Layout } from "@/components/Layout";
import { RiskMeter } from "@/components/RiskMeter";

const IncidentDetails = () => {
  const { id } = useParams();

  // Mock data for demonstration
  const incident = {
    id: id || "INC-M4K7X2-A1B2C3",
    type: "url",
    content: "https://army-welfare-portal.suspicious.com/login",
    riskScore: 95,
    severity: "critical",
    status: "pending",
    reportedBy: "Capt. Sharma, Field Officer",
    location: "Northern Command, Udhampur",
    createdAt: "2025-11-30T10:30:00",
    description: "Received this link via WhatsApp claiming to be from Army Welfare. Requesting urgent login to verify pension details.",
    analysis: {
      summary: "This URL has been identified as a sophisticated phishing attempt targeting defence personnel. The domain mimics the legitimate Army Welfare portal but is designed to harvest credentials. The site was registered 5 days ago and uses SSL certificates to appear legitimate.",
      indicators: [
        { label: "Domain Age", value: "5 days", risk: "high" },
        { label: "SSL Certificate", value: "Valid but recently issued", risk: "medium" },
        { label: "Hosting Location", value: "Overseas server", risk: "high" },
        { label: "Content Match", value: "92% match to official portal", risk: "critical" },
        { label: "Form Action", value: "External credential capture", risk: "critical" },
      ],
      recommendations: [
        "Immediately block this domain at all firewall levels",
        "Issue advisory to all personnel in Northern Command",
        "Scan systems that may have accessed this URL",
        "Report to CERT-In for domain takedown",
        "Monitor for similar domains targeting Army Welfare",
      ],
      iocs: [
        "army-welfare-portal.suspicious.com",
        "185.234.xxx.xxx",
        "SHA256: 8f7d3a2b1c4e5f6g...",
      ],
    },
    timeline: [
      { time: "10:30", event: "Incident reported", status: "complete" },
      { time: "10:31", event: "AI analysis initiated", status: "complete" },
      { time: "10:32", event: "Risk assessment: Critical", status: "complete" },
      { time: "10:35", event: "Pending analyst review", status: "current" },
    ],
  };

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-destructive/10 text-destructive border-destructive/30";
      case "high": return "bg-orange-500/10 text-orange-500 border-orange-500/30";
      default: return "bg-yellow-500/10 text-yellow-500 border-yellow-500/30";
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "critical": return "text-destructive";
      case "high": return "text-orange-500";
      case "medium": return "text-yellow-500";
      default: return "text-emerald-500";
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
          {/* Back Button */}
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary mb-6 transition-colors group"
          >
            <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
            Back to Dashboard
          </Link>

          {/* Header */}
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4 mb-8">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-foreground font-heading">
                  {incident.id}
                </h1>
                <span
                  className={`px-3 py-1 text-sm font-medium rounded border capitalize ${getSeverityStyles(
                    incident.severity
                  )}`}
                >
                  {incident.severity}
                </span>
              </div>
              <p className="text-muted-foreground text-lg">
                Incident Analysis and Forensic Report
              </p>
            </div>
            <div className="flex gap-3">
              <button className="cyber-button-outline flex items-center gap-2">
                <Download className="h-4 w-4" />
                Download Report
              </button>
              <button className="cyber-button-accent flex items-center gap-2">
                <Send className="h-4 w-4" />
                Escalate to CERT
              </button>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Reported Content */}
              <div className="glass-card p-6">
                <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2 font-heading">
                  <Link2 className="h-5 w-5 text-primary" />
                  Reported Content
                </h3>
                <div className="p-4 bg-black/40 rounded-lg font-mono text-sm break-all border border-white/10 text-primary/90">
                  {incident.content}
                </div>
                {incident.description && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-muted-foreground mb-2 uppercase tracking-wider">
                      Reporter's Description
                    </p>
                    <p className="text-sm text-foreground leading-relaxed">{incident.description}</p>
                  </div>
                )}
              </div>

              {/* AI Analysis */}
              <div className="glass-card p-6">
                <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2 font-heading">
                  <Shield className="h-5 w-5 text-primary" />
                  Sentinel AI Analysis
                </h3>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5 mb-6">
                  <p className="text-sm text-foreground leading-relaxed">
                    {incident.analysis.summary}
                  </p>
                </div>

                {/* Threat Indicators */}
                <div className="mb-6">
                  <h4 className="text-sm font-bold text-foreground mb-3 uppercase tracking-wider">
                    Threat Indicators
                  </h4>
                  <div className="space-y-3">
                    {incident.analysis.indicators.map((indicator, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 transition-colors"
                      >
                        <span className="text-sm text-foreground">{indicator.label}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-sm text-muted-foreground font-mono">
                            {indicator.value}
                          </span>
                          <span
                            className={`text-xs font-bold px-2 py-1 rounded capitalize ${indicator.risk === 'critical' ? 'bg-destructive/20 text-destructive' :
                                indicator.risk === 'high' ? 'bg-orange-500/20 text-orange-500' :
                                  indicator.risk === 'medium' ? 'bg-yellow-500/20 text-yellow-500' :
                                    'bg-emerald-500/20 text-emerald-500'
                              }`}
                          >
                            {indicator.risk}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                <div className="mb-6">
                  <h4 className="text-sm font-bold text-foreground mb-3 uppercase tracking-wider">
                    Recommended Actions
                  </h4>
                  <ul className="space-y-2">
                    {incident.analysis.recommendations.map((rec, index) => (
                      <li
                        key={index}
                        className="flex items-start gap-2 text-sm text-muted-foreground bg-white/5 p-3 rounded-lg border border-white/5"
                      >
                        <AlertTriangle className="h-4 w-4 text-orange-500 flex-shrink-0 mt-0.5" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* IOCs */}
                <div>
                  <h4 className="text-sm font-bold text-foreground mb-3 uppercase tracking-wider">
                    Indicators of Compromise (IOCs)
                  </h4>
                  <div className="space-y-2">
                    {incident.analysis.iocs.map((ioc, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-2 p-3 bg-destructive/10 rounded-lg font-mono text-xs text-destructive border border-destructive/20"
                      >
                        <Activity className="h-4 w-4" />
                        {ioc}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Risk Score */}
              <div className="glass-card p-6">
                <h3 className="text-sm font-bold text-muted-foreground mb-6 text-center uppercase tracking-wider">
                  Risk Assessment
                </h3>
                <div className="flex justify-center">
                  <RiskMeter score={incident.riskScore} size="lg" />
                </div>
              </div>

              {/* Incident Details */}
              <div className="glass-card p-6">
                <h3 className="text-sm font-bold text-foreground mb-4 uppercase tracking-wider">
                  Incident Details
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3 p-3 bg-white/5 rounded-lg border border-white/5">
                    <User className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Reported By</p>
                      <p className="text-sm text-foreground font-medium">{incident.reportedBy}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-white/5 rounded-lg border border-white/5">
                    <MapPin className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Location</p>
                      <p className="text-sm text-foreground font-medium">{incident.location}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-white/5 rounded-lg border border-white/5">
                    <Clock className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Reported At</p>
                      <p className="text-sm text-foreground font-medium">
                        {new Date(incident.createdAt).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div className="glass-card p-6">
                <h3 className="text-sm font-bold text-foreground mb-4 uppercase tracking-wider">
                  Activity Timeline
                </h3>
                <div className="space-y-0 relative">
                  <div className="absolute left-[5px] top-2 bottom-2 w-px bg-white/10" />
                  {incident.timeline.map((item, index) => (
                    <div key={index} className="flex gap-4 relative pb-6 last:pb-0">
                      <div className="flex flex-col items-center z-10">
                        <div
                          className={`w-3 h-3 rounded-full border-2 border-background ${item.status === "complete"
                              ? "bg-emerald-500"
                              : item.status === "current"
                                ? "bg-primary animate-pulse"
                                : "bg-muted"
                            }`}
                        />
                      </div>
                      <div>
                        <p className="text-xs text-primary font-mono mb-1">{item.time}</p>
                        <p className="text-sm text-foreground font-medium">{item.event}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default IncidentDetails;
