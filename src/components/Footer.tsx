/**
 * Government-style footer for WatchTower
 */

import { Shield } from "lucide-react";
import { APP_NAME } from "@/utils/constants";

export const Footer = () => {
  return (
    <footer className="bg-secondary text-secondary-foreground mt-auto">
      <div className="gov-container py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Shield className="h-6 w-6 text-accent" />
            <div>
              <span className="font-semibold">{APP_NAME}</span>
              <span className="text-secondary-foreground/70 text-sm ml-2">
                | CERT-Army Cyber Portal
              </span>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row items-center gap-4 md:gap-8 text-sm text-secondary-foreground/70">
            <span>Ministry of Defence, Government of India</span>
            <span>•</span>
            <span>Smart India Hackathon 2025</span>
            <span>•</span>
            <span>Team Urban Dons</span>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t border-secondary-foreground/10 text-center text-xs text-secondary-foreground/50">
          <p>
            This portal is for authorized defence personnel only. Unauthorized access is prohibited.
          </p>
          <p className="mt-1">
            © {new Date().getFullYear()} {APP_NAME}. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};
