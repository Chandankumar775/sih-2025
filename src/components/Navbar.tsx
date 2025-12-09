/**
 * Government-style top navigation bar for WatchTower
 */

import { Link, useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, LogOut, Menu, X, User, ChevronDown } from "lucide-react";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { APP_NAME } from "@/utils/constants";
import { ThemeToggle } from "@/components/ThemeToggle";

interface NavbarProps {
  hideAuthButtons?: boolean;
}

export const Navbar = ({ hideAuthButtons = false }: NavbarProps = {}) => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  
  // Auto-hide auth buttons on non-home pages
  const isHomePage = location.pathname === '/' || location.pathname === '/index';
  const shouldShowAuthButtons = isHomePage && !hideAuthButtons;

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navLinks = [
    { label: "Dashboard", path: "/dashboard", roles: ["admin"] },
    { label: "Report Incident", path: "/report", roles: ["reporter", "admin"] },
    { label: "Analytics", path: "/analysis-admin", roles: ["admin"] },
    { label: "Zero Trust", path: "/zero-trust", roles: ["admin"] },
    { label: "Trends", path: "/trends", roles: ["admin"] },
  ];

  // Hide nav links on homepage
  const showNavLinks = !isHomePage;

  const filteredLinks = navLinks.filter(
    (link) => !user || link.roles.includes(user.role)
  );

  const isActive = (path: string) => location.pathname === path;

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, type: "spring", stiffness: 100 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? "py-2" : "py-4"
        }`}
    >
      <div className="gov-container">
        <div
          className={`bg-white/95 backdrop-blur-md shadow-lg border border-gray-200 rounded-2xl px-6 transition-all duration-300 ${scrolled ? "h-16" : "h-20"
            } flex items-center justify-between`}
        >
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative">
              <img 
                src="/media/logo.png" 
                alt="RakshaNetra Logo" 
                className="h-12 w-12 object-contain transition-transform duration-300 group-hover:scale-110"
              />
            </div>
            <div className="flex flex-col">
              <span className="text-gray-900 font-bold text-lg leading-tight tracking-tight font-heading">
                {APP_NAME}
              </span>
              <span className="text-blue-900 text-[10px] uppercase tracking-widest">
                Cyber Defence
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {isAuthenticated && showNavLinks &&
              filteredLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${isActive(link.path)
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                    } group overflow-hidden`}
                >
                  <span className="relative z-10">{link.label}</span>
                  {isActive(link.path) && (
                    <motion.div
                      layoutId="activeNav"
                      className="absolute inset-0 bg-primary/10 rounded-lg border border-primary/20"
                      transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    />
                  )}
                </Link>
              ))}
          </nav>

          {/* User Menu & Theme Toggle */}
          <div className="hidden md:flex items-center gap-4">
            <ThemeToggle />

            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-3 px-3 py-1.5 bg-secondary/50 border border-white/5 rounded-lg backdrop-blur-sm">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-foreground text-xs font-medium">
                      {user?.name}
                    </span>
                    <span className="text-[10px] text-accent uppercase tracking-wider">
                      {user?.role}
                    </span>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-all duration-300"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            ) : shouldShowAuthButtons ? (
              <div className="flex items-center gap-3">
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="cyber-button-primary text-sm px-5 py-2"
                >
                  Register
                </Link>
              </div>
            ) : null}
          </div>

          {/* Mobile Menu Toggle */}
          <div className="flex items-center gap-4 md:hidden">
            <ThemeToggle />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-foreground hover:bg-white/5 rounded-lg transition-colors"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0, marginTop: 0 }}
              animate={{ opacity: 1, height: "auto", marginTop: 8 }}
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              className="md:hidden glass-panel rounded-xl overflow-hidden"
            >
              <nav className="flex flex-col p-4 gap-2">
                {isAuthenticated &&
                  filteredLinks.map((link, index) => (
                    <motion.div
                      key={link.path}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Link
                        to={link.path}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`block px-4 py-3 rounded-lg text-sm font-medium transition-all ${isActive(link.path)
                          ? "bg-primary/10 text-primary border border-primary/20"
                          : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                          }`}
                      >
                        {link.label}
                      </Link>
                    </motion.div>
                  ))}

                <div className="h-px bg-white/10 my-2" />

                {isAuthenticated ? (
                  <div className="flex items-center justify-between px-4 py-2">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30">
                        <User className="h-4 w-4 text-primary" />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-foreground text-sm font-medium">
                          {user?.name}
                        </span>
                        <span className="text-xs text-accent uppercase">
                          {user?.role}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="p-2 text-muted-foreground hover:text-destructive transition-colors"
                    >
                      <LogOut className="h-5 w-5" />
                    </button>
                  </div>
                ) : shouldShowAuthButtons ? (
                  <div className="flex flex-col gap-2">
                    <Link
                      to="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full px-4 py-3 text-center text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-lg transition-colors"
                    >
                      Sign In
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full cyber-button-primary text-center text-sm py-3"
                    >
                      Register
                    </Link>
                  </div>
                ) : null}
              </nav>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.header>
  );
};
