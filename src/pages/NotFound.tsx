import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Home } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/5 via-background to-background" />
        <div className="absolute top-0 left-0 w-full h-full bg-[url('/grid.svg')] opacity-10" />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center relative z-10 p-8 glass-card max-w-lg mx-4"
      >
        <div className="mb-6 relative inline-block">
          <div className="absolute inset-0 bg-destructive/20 blur-xl rounded-full animate-pulse-slow" />
          <AlertTriangle className="h-24 w-24 text-destructive relative z-10 mx-auto" />
        </div>

        <h1 className="mb-2 text-6xl font-bold font-heading text-foreground">404</h1>
        <h2 className="mb-6 text-2xl font-semibold text-muted-foreground">Page Not Found</h2>

        <p className="mb-8 text-muted-foreground">
          The requested resource <span className="text-primary font-mono bg-primary/10 px-2 py-0.5 rounded">{location.pathname}</span> could not be located on this server.
        </p>

        <Link
          to="/"
          className="cyber-button-primary inline-flex items-center gap-2 group"
        >
          <Home className="h-4 w-4 group-hover:scale-110 transition-transform" />
          Return to Home
        </Link>
      </motion.div>
    </div>
  );
};

export default NotFound;
