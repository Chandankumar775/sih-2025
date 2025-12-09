/**
 * Submitted Report Confirmation Page
 * Simple confirmation after incident submission
 */

import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { CheckCircle } from "lucide-react";
import { Layout } from "@/components/Layout";
import { toast } from "sonner";

const SubmittedReport = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const incidentId = searchParams.get("id");

  useEffect(() => {
    // Show toast notification
    toast.success("Report Submitted", {
      description: "Your incident report has been successfully submitted.",
      duration: 2000,
    });
  }, []);

  // Redirect if no incident ID
  useEffect(() => {
    if (!incidentId) {
      navigate("/report");
    }
  }, [incidentId, navigate]);

  return (
    <Layout>
      {/* Government Header */}
      <div className="bg-white border-b-4 border-orange-500">
        <div className="max-w-[1400px] mx-auto px-8 py-3 flex items-center gap-3">
          <img src="/media/logo.png" alt="Emblem" className="h-12" />
          <div>
            <h1 className="text-sm font-semibold text-gray-900">भारत सरकार | Government of India</h1>
            <p className="text-xs text-gray-600">रक्षा मंत्रालय | Ministry of Defence</p>
            <p className="text-xs text-blue-900 font-medium">Cyber Incident Submission Confirmation</p>
          </div>
        </div>
      </div>
      
      <div className="min-h-[80vh] bg-gradient-to-b from-white to-green-50 flex items-center justify-center py-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full mx-4"
        >
          <div className="bg-white border-2 border-gray-300 p-8 text-center space-y-6 shadow-lg">
            {/* Success Icon */}
            <div className="flex justify-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>
            </div>

            {/* Message */}
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Report Submitted Successfully
              </h1>
              <p className="text-gray-600">
                Thank you for helping keep our community safe.
              </p>
            </div>

            {/* Incident ID */}
            {incidentId && (
              <div className="bg-blue-50 border-2 border-blue-300 p-4">
                <div className="text-sm text-blue-700 font-medium mb-1">
                  Incident ID
                </div>
                <div className="font-mono text-lg font-bold text-blue-900">
                  {incidentId}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="space-y-3 pt-4">
              <button
                onClick={() => navigate("/report")}
                className="w-full py-3 px-6 bg-blue-900 text-white font-medium hover:bg-blue-800 transition-colors"
              >
                Report Another Incident
              </button>
              <button
                onClick={() => navigate("/dashboard")}
                className="w-full py-3 px-6 bg-gray-200 text-gray-900 font-medium hover:bg-gray-300 transition-colors"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default SubmittedReport;
