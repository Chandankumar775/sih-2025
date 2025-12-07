/**
 * Landing page for WatchTower
 * Cyber-defence style hero and feature showcase
 */

import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Shield, Lock, AlertTriangle, BarChart3, Users, CheckCircle,
  ArrowRight, FileSearch, Zap, Globe, Activity, Radar
} from "lucide-react";
import { Layout } from "@/components/Layout";
import { APP_NAME, APP_TAGLINE } from "@/utils/constants";
import { RakshaNetraLogo } from "@/components/RakshaNetraLogo";

const Index = () => {
  const features = [
    {
      icon: AlertTriangle,
      title: "Threat Reporting",
      description: "Submit suspicious URLs, messages, and files for immediate AI-powered analysis",
      color: "text-neon-orange"
    },
    {
      icon: Zap,
      title: "AI Triage Core",
      description: "Sentinel AI provides real-time threat assessment with risk scores and recommendations",
      color: "text-neon-blue"
    },
    {
      icon: Lock,
      title: "Quantum Encryption",
      description: "All submissions are encrypted before transmission for maximum security",
      color: "text-neon-purple"
    },
    {
      icon: Radar,
      title: "Live Surveillance",
      description: "Monitor threat trends and patterns across the defence network in real-time",
      color: "text-emerald-400"
    },
  ];

  const stats = [
    { value: "10K+", label: "Threats Neutralized" },
    { value: "99.9%", label: "AI Accuracy" },
    { value: "<30ms", label: "Response Time" },
    { value: "24/7", label: "Active Watch" },
  ];

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-20 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/10 via-background to-background" />
          <div className="absolute inset-0 animate-grid opacity-20" />
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: "2s" }} />
        </div>

        <div className="relative z-10 w-full max-w-[1400px] mx-auto px-8">
          <div className="grid grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="col-span-1 text-left"
            >
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6 animate-fade-in">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                </span>
                System Operational
              </div>

              <h1 className="text-6xl font-bold mb-6 leading-tight font-heading">
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-white/50">
                  Advanced
                </span>
                <span className="block text-glow">
                  Cyber Defence
                </span>
              </h1>

              <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
                {APP_TAGLINE}. Deploying next-generation AI sentinels to protect national digital infrastructure.
              </p>

              <div className="flex flex-row gap-4 justify-start">
                <Link
                  to="/report"
                  className="px-8 py-3 bg-gradient-to-br from-white/10 to-white/5 hover:from-white/20 hover:to-white/10 rounded-lg border border-white/20 font-semibold tracking-wider uppercase text-sm transition-all duration-300 shadow-lg hover:shadow-primary/20 inline-flex items-center justify-center gap-2 group"
                >
                  Initiate Report
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
                <Link
                  to="/login"
                  className="px-8 py-3 rounded-lg border border-white/10 text-foreground font-medium hover:bg-white/5 transition-all duration-300 hover:border-primary/50"
                >
                  Analyst Access
                </Link>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="col-span-1 relative flex items-center justify-center"
            >
              <div className="relative w-full flex items-center justify-center" style={{ minHeight: '500px' }}>
                {/* Background glow */}
                <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-accent/20 rounded-full blur-3xl" />

                {/* 3D Glowing Circle Logo */}
                <div className="relative z-10 flex flex-col items-center">
                  <div className="mb-6">
                    <RakshaNetraLogo />
                  </div>
                  <div className="text-2xl font-bold text-foreground font-heading mb-2">RAKSHA NETRA</div>
                  <div className="text-sm text-primary/80 tracking-[0.2em] uppercase">Sentinel Active</div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="border-y border-white/5 bg-black/20 backdrop-blur-sm">
        <div className="max-w-[1400px] mx-auto px-8">
          <div className="grid grid-cols-4 divide-x divide-white/5">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="py-8 text-center group hover:bg-white/5 transition-colors"
              >
                <p className="text-3xl lg:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-accent mb-1 font-heading">
                  {stat.value}
                </p>
                <p className="text-sm text-muted-foreground uppercase tracking-wider">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 relative overflow-hidden">
        <div className="gov-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-foreground mb-4 font-heading">
              Tactical Capabilities
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
              Equipped with state-of-the-art tools for comprehensive threat detection and neutralization.
            </p>
          </motion.div>

          <div className="grid grid-cols-4 gap-6 max-w-[1400px] mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="glass-card p-6 group hover:-translate-y-2 transition-all duration-300"
              >
                <div className={`w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 ${feature.color}`}>
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold text-foreground mb-3 font-heading">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 bg-secondary/20 relative">
        <div className="gov-container">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-foreground mb-4 font-heading">
              Protocol Sequence
            </h2>
            <p className="text-muted-foreground">
              Standard operating procedure for threat neutralization
            </p>
          </motion.div>

          <div className="relative">
            {/* Connecting Line */}
            <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-primary/30 to-transparent hidden lg:block" />

            <div className="grid md:grid-cols-4 gap-8">
              {[
                { step: "01", title: "Detection", desc: "Identify suspicious vector" },
                { step: "02", title: "Analysis", desc: "AI-driven threat scanning" },
                { step: "03", title: "Verdict", desc: "Risk assessment & scoring" },
                { step: "04", title: "Response", desc: "Neutralization protocols" },
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="relative text-center group"
                >
                  <div className="w-16 h-16 mx-auto bg-background border border-primary/30 rounded-2xl flex items-center justify-center text-xl font-bold text-primary mb-6 relative z-10 group-hover:border-primary group-hover:shadow-[0_0_20px_hsl(var(--primary)/0.3)] transition-all duration-300">
                    {item.step}
                  </div>
                  <h3 className="text-lg font-bold text-foreground mb-2 font-heading">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-primary/5" />
        <div className="gov-container relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass-panel rounded-3xl p-12 text-center border-primary/20"
          >
            <Shield className="h-16 w-16 text-primary mx-auto mb-6 animate-pulse-slow" />
            <h2 className="text-3xl lg:text-5xl font-bold mb-6 font-heading">
              Secure The Network
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
              Join the elite digital defence force. Report threats and contribute to national security.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register" className="cyber-button-accent inline-flex items-center justify-center gap-2">
                Initialize Account
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/login"
                className="px-8 py-3 rounded-lg border border-white/10 text-foreground font-medium hover:bg-white/5 transition-all duration-300"
              >
                Secure Login
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-white/5 bg-black/40">
        <div className="gov-container">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary/50" />
              <span className="text-sm text-muted-foreground">
                Smart India Hackathon 2025
              </span>
            </div>
            <div className="text-sm text-muted-foreground">
              <span className="text-primary/50 mr-2">ID:</span>
              SIH25183
              <span className="mx-3 text-white/10">|</span>
              <span className="text-primary/50 mr-2">UNIT:</span>
              Team Urban Dons
            </div>
          </div>
        </div>
      </footer>
    </Layout>
  );
};

export default Index;
