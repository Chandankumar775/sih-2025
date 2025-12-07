/**
 * Registration page for WatchTower
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Shield, Mail, Lock, User, AlertCircle, Eye, EyeOff, CheckCircle, ArrowRight } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { APP_NAME } from "@/utils/constants";

const Register = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const { register, loading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (password !== confirmPassword) {
      setLocalError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setLocalError("Password must be at least 6 characters");
      return;
    }

    const result = await register(name, email, password);
    if (result.success) {
      navigate("/dashboard");
    }
  };

  const displayError = localError || error;

  return (
    <div className="min-h-screen bg-background flex overflow-hidden relative">
      {/* Background Elements */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/5 via-background to-background" />
        <div className="absolute top-0 left-0 w-full h-full bg-[url('/grid.svg')] opacity-10" />
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: "2s" }} />
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
            <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse-slow" />
            <Shield className="h-32 w-32 text-primary relative z-10" />
            <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-24 h-1 bg-primary/50 blur-sm" />
          </div>

          <h1 className="text-5xl font-bold text-white mb-6 font-heading tracking-tight">
            {APP_NAME}
          </h1>
          <p className="text-xl text-muted-foreground mb-12 leading-relaxed">
            Join the Defence Cyber Incident Network
          </p>

          <div className="mt-8 space-y-4 text-left">
            {[
              "Report suspicious URLs, messages, and files",
              "AI-powered instant threat analysis",
              "End-to-end encrypted submissions",
              "Direct escalation to CERT-Army",
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + (index * 0.1) }}
                className="flex items-center gap-3 text-gray-300 bg-white/5 p-3 rounded-lg border border-white/5"
              >
                <CheckCircle className="h-5 w-5 text-primary flex-shrink-0" />
                <span>{feature}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Right Panel - Register Form */}
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
                Create Account
              </h2>
              <p className="text-muted-foreground mt-2 text-sm">
                Register to report cyber incidents
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {displayError && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm"
                >
                  <AlertCircle className="h-5 w-5 flex-shrink-0" />
                  <span>{displayError}</span>
                </motion.div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 ml-1">
                  Full Name
                </label>
                <div className="relative group">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Captain John Doe"
                    required
                    className="cyber-input pl-10"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 ml-1">
                  Official Email
                </label>
                <div className="relative group">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="officer@army.mil"
                    required
                    className="cyber-input pl-10"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 ml-1">
                  Password
                </label>
                <div className="relative group">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min. 6 characters"
                    required
                    className="cyber-input pl-10 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 ml-1">
                  Confirm Password
                </label>
                <div className="relative group">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter password"
                    required
                    className="cyber-input pl-10"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full cyber-button-primary group relative overflow-hidden"
              >
                <span className="relative z-10 flex items-center justify-center gap-2">
                  {loading ? "Creating Account..." : "Register"}
                  {!loading && <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />}
                </span>
              </button>
            </form>

            <div className="mt-6 text-center">
              <span className="text-muted-foreground text-sm">
                Already have an account?{" "}
              </span>
              <Link to="/login" className="text-primary font-medium hover:text-primary/80 hover:underline text-sm transition-colors">
                Sign in here
              </Link>
            </div>

            <p className="mt-6 text-xs text-muted-foreground text-center border-t border-white/10 pt-4">
              By registering, you agree to the Terms of Service and acknowledge that this portal is for authorized defence personnel only.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Register;
