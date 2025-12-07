/**
 * Unauthorized access page for WatchTower
 */

import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ShieldAlert, ArrowLeft, Lock } from "lucide-react";
import { Layout } from "@/components/Layout";
import { useAuth } from "@/hooks/useAuth";

const Unauthorized = () => {
  const { user } = useAuth();

  // Redirect reporters to /report, others to /dashboard
  const returnPath = user?.role === "reporter" ? "/report" : "/dashboard";
  const returnLabel = user?.role === "reporter" ? "Report Incident" : "Dashboard";

  return (
    <Layout>
      <div className="gov-container py-16 min-h-[80vh] flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="max-w-lg w-full text-center glass-card p-10 border-t-4 border-t-destructive"
        >
          <div className="mb-6 relative inline-block">
            <div className="absolute inset-0 bg-destructive/20 blur-xl rounded-full animate-pulse-slow" />
            <ShieldAlert className="h-24 w-24 text-destructive relative z-10 mx-auto" />
            <Lock className="h-8 w-8 text-white absolute bottom-0 right-0 bg-destructive rounded-full p-1.5 border-2 border-background" />
          </div>

          <h1 className="text-3xl font-bold text-foreground mb-2 font-heading">
            Access Denied
          </h1>
          <p className="text-xl text-destructive font-medium mb-6">
            Authorization Required
          </p>

          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 mb-8 text-left">
            <p className="text-muted-foreground text-sm leading-relaxed">
              You do not have permission to access this protected resource. This incident has been logged and reported to the system administrator.
            </p>
          </div>

          <Link to={returnPath} className="cyber-button-primary inline-flex items-center gap-2 w-full justify-center group">
            <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
            Return to {returnLabel}
          </Link>
        </motion.div>
      </div>
    </Layout>
  );
};

export default Unauthorized;
