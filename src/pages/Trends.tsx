/**
 * Analytics and Trends page for WatchTower
 * Displays incident statistics and visualizations
 */

import { motion } from "framer-motion";
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";
import { TrendingUp, AlertTriangle, Shield, Calendar, Activity } from "lucide-react";
import { Layout } from "@/components/Layout";

const Trends = () => {
  // Mock data for charts
  const weeklyData = [
    { day: "Mon", incidents: 12, critical: 2 },
    { day: "Tue", incidents: 19, critical: 4 },
    { day: "Wed", incidents: 15, critical: 3 },
    { day: "Thu", incidents: 25, critical: 6 },
    { day: "Fri", incidents: 22, critical: 5 },
    { day: "Sat", incidents: 8, critical: 1 },
    { day: "Sun", incidents: 6, critical: 1 },
  ];

  const riskDistribution = [
    { name: "Critical", value: 15, color: "hsl(0, 62%, 30%)" }, // destructive
    { name: "High", value: 28, color: "hsl(32, 100%, 50%)" }, // accent
    { name: "Medium", value: 35, color: "hsl(45, 93%, 47%)" }, // yellow
    { name: "Low", value: 22, color: "hsl(142, 71%, 45%)" }, // green
  ];

  const incidentTypes = [
    { type: "URL", count: 45 },
    { type: "Message", count: 32 },
    { type: "File", count: 23 },
  ];

  const topDomains = [
    { domain: "army-welfare-*.com", incidents: 15 },
    { domain: "mod-gov-*.in", incidents: 12 },
    { domain: "pension-portal-*.net", incidents: 9 },
    { domain: "cantonment-*.org", incidents: 7 },
    { domain: "defence-update-*.com", incidents: 5 },
  ];

  const monthlyTrend = [
    { month: "Jun", incidents: 45 },
    { month: "Jul", incidents: 52 },
    { month: "Aug", incidents: 48 },
    { month: "Sep", incidents: 65 },
    { month: "Oct", incidents: 78 },
    { month: "Nov", incidents: 107 },
  ];

  return (
    <Layout>
      <div className="gov-container py-8 min-h-screen">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground flex items-center gap-2 font-heading">
              <TrendingUp className="h-8 w-8 text-primary" />
              Incident Analytics & Trends
            </h1>
            <p className="text-muted-foreground mt-1 text-lg">
              Overview of cyber threat patterns and incident statistics
            </p>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="glass-card p-6 border-l-4 border-l-primary">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-primary/10 rounded-xl">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-foreground font-heading">107</p>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">This Month</p>
                </div>
              </div>
            </div>
            <div className="glass-card p-6 border-l-4 border-l-destructive">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-destructive/10 rounded-xl">
                  <AlertTriangle className="h-6 w-6 text-destructive" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-foreground font-heading">15</p>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">Critical</p>
                </div>
              </div>
            </div>
            <div className="glass-card p-6 border-l-4 border-l-emerald-500">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-emerald-500/10 rounded-xl">
                  <Calendar className="h-6 w-6 text-emerald-500" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-foreground font-heading">92%</p>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">Resolved</p>
                </div>
              </div>
            </div>
            <div className="glass-card p-6 border-l-4 border-l-accent">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-accent/10 rounded-xl">
                  <Activity className="h-6 w-6 text-accent" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-foreground font-heading">+37%</p>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">vs Last Month</p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-6 mb-6">
            {/* Weekly Incidents */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-foreground mb-6 uppercase tracking-wider">
                Weekly Incident Pattern
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weeklyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                    <XAxis
                      dataKey="day"
                      tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "rgba(0,0,0,0.8)",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: "8px",
                        backdropFilter: "blur(8px)",
                        color: "#fff"
                      }}
                      cursor={{ fill: "rgba(255,255,255,0.05)" }}
                    />
                    <Legend wrapperStyle={{ paddingTop: "20px" }} />
                    <Bar
                      dataKey="incidents"
                      name="Total Incidents"
                      fill="hsl(var(--primary))"
                      radius={[4, 4, 0, 0]}
                      barSize={20}
                    />
                    <Bar
                      dataKey="critical"
                      name="Critical"
                      fill="hsl(var(--destructive))"
                      radius={[4, 4, 0, 0]}
                      barSize={20}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Risk Distribution */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-foreground mb-6 uppercase tracking-wider">
                Risk Level Distribution
              </h3>
              <div className="h-72 flex items-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={80}
                      outerRadius={110}
                      paddingAngle={4}
                      dataKey="value"
                      stroke="none"
                    >
                      {riskDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "rgba(0,0,0,0.8)",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: "8px",
                        backdropFilter: "blur(8px)",
                        color: "#fff"
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-3 pr-8">
                  {riskDistribution.map((item) => (
                    <div key={item.name} className="flex items-center gap-3">
                      <div
                        className="w-3 h-3 rounded-full shadow-[0_0_10px_currentColor]"
                        style={{ backgroundColor: item.color, color: item.color }}
                      />
                      <span className="text-sm text-muted-foreground font-medium">
                        {item.name}: <span className="text-foreground">{item.value}%</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-6 mb-6">
            {/* Monthly Trend */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-foreground mb-6 uppercase tracking-wider">
                Monthly Incident Trend
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={monthlyTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                    <XAxis
                      dataKey="month"
                      tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "rgba(0,0,0,0.8)",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: "8px",
                        backdropFilter: "blur(8px)",
                        color: "#fff"
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="incidents"
                      stroke="hsl(var(--accent))"
                      strokeWidth={3}
                      dot={{ fill: "hsl(var(--accent))", r: 4, strokeWidth: 0 }}
                      activeDot={{ r: 8, strokeWidth: 0, fill: "hsl(var(--accent))" }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Incident Types */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-foreground mb-6 uppercase tracking-wider">
                Incidents by Type
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={incidentTypes} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                    <XAxis
                      type="number"
                      tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      type="category"
                      dataKey="type"
                      tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                      width={80}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "rgba(0,0,0,0.8)",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: "8px",
                        backdropFilter: "blur(8px)",
                        color: "#fff"
                      }}
                      cursor={{ fill: "rgba(255,255,255,0.05)" }}
                    />
                    <Bar dataKey="count" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} barSize={30} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Top Malicious Domains */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-foreground mb-6 uppercase tracking-wider">
              Top Malicious Domains
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-4 px-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      Rank
                    </th>
                    <th className="text-left py-4 px-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      Domain Pattern
                    </th>
                    <th className="text-left py-4 px-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      Incidents
                    </th>
                    <th className="text-left py-4 px-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      Threat Level
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {topDomains.map((item, index) => (
                    <tr key={index} className="border-b border-white/5 last:border-0 hover:bg-white/5 transition-colors">
                      <td className="py-4 px-4 text-sm text-foreground font-medium">
                        #{index + 1}
                      </td>
                      <td className="py-4 px-4 font-mono text-sm text-primary">
                        {item.domain}
                      </td>
                      <td className="py-4 px-4 text-sm text-foreground font-bold">
                        {item.incidents}
                      </td>
                      <td className="py-4 px-4">
                        <div className="w-full bg-white/10 rounded-full h-2 max-w-[200px]">
                          <div
                            className="bg-destructive h-2 rounded-full shadow-[0_0_10px_rgba(var(--destructive),0.5)]"
                            style={{ width: `${(item.incidents / 15) * 100}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default Trends;
