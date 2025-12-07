/**
 * Loading spinner component for WatchTower
 */

import { motion } from "framer-motion";
import { Shield } from "lucide-react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
}

export const LoadingSpinner = ({ size = "md", text }: LoadingSpinnerProps) => {
  const dimensions = {
    sm: "h-8 w-8",
    md: "h-12 w-12",
    lg: "h-16 w-16",
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className={`${dimensions[size]} text-primary`}
      >
        <Shield className="w-full h-full" />
      </motion.div>
      {text && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-muted-foreground text-sm"
        >
          {text}
        </motion.p>
      )}
    </div>
  );
};
