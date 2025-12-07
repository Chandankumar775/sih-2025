/**
 * Login page for Raksha Netra
 */

import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Shield, Mail, Lock, AlertCircle, Eye, EyeOff, ArrowRight } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { APP_NAME } from "@/utils/constants";
import { GetStartedButton } from "@/components/GetStartedButton";
import { CyberCheckbox } from "@/components/CyberCheckbox";
import { RakshaNetraLogo } from "@/components/RakshaNetraLogo";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/dashboard";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await login(email, password);
    if (result.success) {
      navigate(from, { replace: true });
    }
  };

  const demoAccounts = [
    { email: "reporter@army.mil", role: "Reporter" },
    { email: "analyst@cert.army.mil", role: "Analyst" },
    { email: "admin@rakshanetra.mil", role: "Admin" },
  ];

  return (
    <div className="min-h-screen bg-background flex overflow-hidden relative">
      {/* Background Elements */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/5 via-background to-background" />
        <div className="absolute top-0 left-0 w-full h-full bg-[url('/grid.svg')] opacity-10" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: "2s" }} />
      </div>

      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative z-10 flex-col justify-center items-center p-12 border-r border-white/5 bg-black/20 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-lg"
        >
          <div className="relative inline-block mb-8">
            <RakshaNetraLogo />
          </div>
          <p className="text-xl text-muted-foreground mb-12 leading-relaxed">
            Next-Generation Cyber Incident Reporting & Intelligence Platform
          </p>

          <div className="grid grid-cols-2 gap-6 text-left">
            <div className="glass-panel p-4 rounded-xl border border-white/5 bg-white/5">
              <h3 className="text-primary font-semibold mb-2 flex items-center gap-2">
                <Shield className="h-4 w-4" /> Secure Access
              </h3>
              <p className="text-sm text-muted-foreground">
                End-to-end encrypted communication for sensitive data protection.
              </p>
            </div>
            <div className="glass-panel p-4 rounded-xl border border-white/5 bg-white/5">
              <h3 className="text-accent font-semibold mb-2 flex items-center gap-2">
                <AlertCircle className="h-4 w-4" /> Real-time Intel
              </h3>
              <p className="text-sm text-muted-foreground">
                Instant threat analysis and automated risk scoring.
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex flex-col justify-center px-4 sm:px-6 lg:px-20 relative z-10">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="w-full max-w-md mx-auto"
        >
          <div className="glass-card p-8 rounded-2xl border border-white/10 shadow-2xl bg-black/40 backdrop-blur-xl">
            {/* Mobile Logo */}
            <div className="lg:hidden flex items-center justify-center mb-8">
              <Shield className="h-12 w-12 text-primary mr-3" />
              <span className="text-2xl font-bold text-white font-heading">{APP_NAME}</span>
            </div>

            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-white font-heading">
                Authorized Access Only
              </h2>
              <p className="text-muted-foreground mt-2 text-sm">
                Enter your credentials to access the secure portal
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 bg-destructive/10 border border-destructive/30 rounded-lg flex items-start gap-3"
                >
                  <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-destructive">{error}</p>
                </motion.div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
                  placeholder="officer@army.mil"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Lock className="h-4 w-4" />
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all pr-12"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <CyberCheckbox
                  checked={rememberMe}
                  onChange={setRememberMe}
                  label="Remember me"
                />
                <Link
                  to="/forgot-password"
                  className="text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              <GetStartedButton type="submit" loading={loading} />

              <p className="text-center text-sm text-muted-foreground mt-6">
                Don't have an account?{" "}
                <Link to="/register" className="font-medium text-accent hover:text-accent/80 transition-colors">
                  Register here
                </Link>
              </p>
            </form>

            <div className="mt-8 pt-8 border-t border-white/10">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-4">
                Demo Credentials
              </p>
              <div className="space-y-2">
                {demoAccounts.map((account) => (
                  <div
                    key={account.email}
                    onClick={() => {
                      setEmail(account.email);
                      setPassword("demo123");
                    }}
                    className="flex justify-between items-center text-sm px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors cursor-pointer group"
                  >
                    <span className="text-white font-medium group-hover:text-primary transition-colors">{account.role}</span>
                    <span className="text-muted-foreground font-mono text-xs group-hover:text-accent transition-colors">{account.email}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Language & Theme Toggles - Top Right */}
      <div className="fixed top-6 right-6 z-50 flex items-center gap-3">
        <LanguageSwitcher />
        <ThemeToggle />
      </div>
    </div>
  );
};

export default Login;
