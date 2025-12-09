/**
 * Login page for Raksha Netra
 */

import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Shield, Mail, Lock, AlertCircle, Eye, EyeOff, ArrowRight, User } from "lucide-react";
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await login(email, password);
    if (result.success) {
      // Get user from auth state after successful login
      const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
      const userRole = storedUser.role;
      
      // Redirect based on role
      if (userRole === 'admin') {
        navigate('/dashboard', { replace: true });
      } else {
        navigate('/report', { replace: true });
      }
    }
  };

  const demoAccounts = [
    { email: "reporter@army.mil", role: "Reporter" },
    { email: "admin@rakshanetra.mil", role: "Admin" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-orange-50 flex flex-col">
      {/* Government Header */}
      <div className="bg-white border-b-4 border-orange-500 shadow-sm">
        <div className="max-w-[1400px] mx-auto px-8 py-3 flex items-center gap-4">
          <img src="/media/logo.png" alt="Emblem" className="h-14" />
          <div>
            <h1 className="text-sm font-semibold text-gray-900">भारत सरकार | Government of India</h1>
            <p className="text-xs text-gray-600">रक्षा मंत्रालय | Ministry of Defence</p>
          </div>
        </div>
      </div>

      {/* Login Form */}
      <div className="flex-1 flex items-center justify-center py-12 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full bg-white border-2 border-gray-300 shadow-lg p-8"
        >
          <div className="text-center mb-6">
            <div className="mb-4">
              <RakshaNetraLogo />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Authorized Access Only
            </h2>
            <p className="text-sm text-gray-600 border-b pb-4 mb-4">
              Official Login Portal | आधिकारिक लॉगिन पोर्टल
            </p>
          </div>

          <div className="mb-6 p-3 bg-blue-50 border-l-4 border-blue-700">
            <p className="text-xs text-blue-900">
              <strong>💡 Demo:</strong> Username "admin" → Admin | Others → Reporter
            </p>
          </div>

          <div>
            <form onSubmit={handleSubmit} className="space-y-5">
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
                <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Username / Email
                </label>
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onFocus={(e) => e.target.placeholder = ""}
                  onBlur={(e) => { if (!e.target.value) e.target.placeholder = "admin or user@example.com"; }}
                  className="w-full px-4 py-3 border-2 border-gray-300 focus:border-blue-600 focus:outline-none text-gray-900"
                  placeholder="admin or user@example.com"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Lock className="h-4 w-4" />
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 pr-12 border-2 border-gray-300 focus:border-blue-600 focus:outline-none text-gray-900"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 border-2 border-gray-300 text-blue-900 focus:ring-blue-600"
                  />
                  Remember me
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm font-medium text-blue-900 hover:text-blue-700 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-6 bg-blue-900 text-white font-medium hover:bg-blue-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Signing In..." : "Sign In"}
              </button>

              <p className="text-center text-sm text-gray-600 mt-6">
                Don't have an account?{" "}
                <Link to="/register" className="font-medium text-blue-900 hover:text-blue-700 transition-colors">
                  Register here
                </Link>
              </p>
            </form>

            <div className="mt-8 pt-8 border-t border-gray-300">
              <p className="text-xs font-medium text-gray-600 uppercase tracking-wider mb-4">
                Demo Credentials (Testing)
              </p>
              <div className="space-y-2">
                {demoAccounts.map((account) => (
                  <div
                    key={account.email}
                    onClick={() => {
                      setEmail(account.email);
                      setPassword("demo123");
                    }}
                    className="flex justify-between items-center text-sm px-3 py-2 border border-gray-300 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer group"
                  >
                    <span className="text-gray-900 font-medium">{account.role}</span>
                    <span className="text-gray-600 font-mono text-xs">{account.email}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Language Switcher - Top Right */}
      <div className="fixed top-6 right-6 z-50">
        <LanguageSwitcher />
      </div>
    </div>
  );
};

export default Login;
