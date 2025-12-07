/**
 * Risk Score Meter component for WatchTower
 * Displays AI-generated risk assessment
 */

import { motion } from "framer-motion";

interface RiskMeterProps {
  score: number;
  size?: "sm" | "md" | "lg";
}

export const RiskMeter = ({ score, size = "md" }: RiskMeterProps) => {
  const getSeverity = (score: number) => {
    if (score >= 90) return { label: "Critical", color: "hsl(0, 72%, 51%)" };
    if (score >= 70) return { label: "High", color: "hsl(25, 95%, 53%)" };
    if (score >= 40) return { label: "Medium", color: "hsl(38, 92%, 50%)" };
    return { label: "Low", color: "hsl(142, 76%, 36%)" };
  };

  const severity = getSeverity(score);
  
  const dimensions = {
    sm: { width: 120, height: 60, strokeWidth: 8 },
    md: { width: 180, height: 90, strokeWidth: 10 },
    lg: { width: 240, height: 120, strokeWidth: 12 },
  };

  const { width, height, strokeWidth } = dimensions[size];
  const radius = height - strokeWidth;
  const circumference = Math.PI * radius;
  const progress = (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <svg
        width={width}
        height={height + 10}
        viewBox={`0 0 ${width} ${height + 10}`}
        className="overflow-visible"
      >
        {/* Background Arc */}
        <path
          d={`M ${strokeWidth / 2} ${height} A ${radius} ${radius} 0 0 1 ${width - strokeWidth / 2} ${height}`}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Progress Arc */}
        <motion.path
          d={`M ${strokeWidth / 2} ${height} A ${radius} ${radius} 0 0 1 ${width - strokeWidth / 2} ${height}`}
          fill="none"
          stroke={severity.color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference - progress }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
        
        {/* Score Text */}
        <text
          x={width / 2}
          y={height - 10}
          textAnchor="middle"
          className="fill-foreground font-bold"
          fontSize={size === "lg" ? 32 : size === "md" ? 24 : 18}
        >
          {score}
        </text>
      </svg>
      
      <div
        className="px-3 py-1 rounded-full text-sm font-medium"
        style={{
          backgroundColor: `${severity.color}20`,
          color: severity.color,
        }}
      >
        {severity.label} Risk
      </div>
    </div>
  );
};
