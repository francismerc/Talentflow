"use client";

import { useSyncExternalStore } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  monthlyApplications as mockMonthlyApplications,
  skillsData,
  statusDistribution as mockStatusDistribution,
} from "@/lib/mock-data";

const tooltipStyle = {
  border: "1px solid #e2e8f0",
  borderRadius: "10px",
  boxShadow: "0 8px 20px rgba(15, 23, 42, 0.08)",
  fontSize: "12px",
};

const subscribe = () => () => {};

function useIsClient() {
  return useSyncExternalStore(subscribe, () => true, () => false);
}

export function MonthlyApplicationsChart({
  compact = false,
  data,
}: {
  compact?: boolean;
  data?: Array<{ month: string; applications: number; shortlisted: number }>;
}) {
  const isClient = useIsClient();
  const height = compact ? "h-[250px]" : "h-[285px]";

  if (!isClient) return <div className={`${height} animate-pulse rounded-xl bg-slate-50`} />;

  return (
    <div className={`${height} min-w-0`}>
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        minHeight={250}
        initialDimension={{ width: 640, height: compact ? 250 : 285 }}
      >
        <AreaChart data={data ?? mockMonthlyApplications} margin={{ top: 10, right: 8, left: -24, bottom: 0 }}>
          <defs>
            <linearGradient id="applicationsFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2563EB" stopOpacity={0.22} />
              <stop offset="100%" stopColor="#2563EB" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#eef2f7" />
          <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 11 }} />
          <YAxis axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 11 }} />
          <Tooltip contentStyle={tooltipStyle} cursor={{ stroke: "#cbd5e1", strokeDasharray: "4 4" }} />
          <Area
            type="monotone"
            dataKey="applications"
            stroke="#2563EB"
            strokeWidth={2.5}
            fill="url(#applicationsFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function StatusDistributionChart({
  data,
}: {
  data?: Array<{ name: string; value: number; color: string }>;
}) {
  const isClient = useIsClient();
  const chartData = data ?? mockStatusDistribution;
  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  if (!isClient) return <div className="h-[210px] animate-pulse rounded-xl bg-slate-50" />;

  return (
    <div className="flex flex-col items-center gap-2 sm:flex-row">
      <div className="relative h-[210px] min-w-0 w-full sm:w-[55%]">
        <ResponsiveContainer
          width="100%"
          height="100%"
          minWidth={0}
          minHeight={210}
          initialDimension={{ width: 320, height: 210 }}
        >
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={58}
              outerRadius={82}
              paddingAngle={3}
              dataKey="value"
              stroke="none"
            >
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 grid place-content-center text-center">
          <span className="text-2xl font-bold text-primary">{total}</span>
          <span className="text-[10px] font-medium uppercase tracking-wide text-slate-400">
            Applicants
          </span>
        </div>
      </div>
      <div className="grid w-full grid-cols-2 gap-x-4 gap-y-3 sm:w-[45%] sm:grid-cols-1">
        {chartData.map((item) => (
          <div key={item.name} className="flex items-center gap-2 text-xs">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="flex-1 text-slate-500">{item.name}</span>
            <span className="font-bold text-primary">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function TopSkillsChart({
  data,
}: {
  data?: Array<{ skill: string; candidates: number }>;
}) {
  const isClient = useIsClient();

  if (!isClient) return <div className="h-[300px] animate-pulse rounded-xl bg-slate-50" />;

  return (
    <div className="h-[300px] min-w-0">
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        minHeight={300}
        initialDimension={{ width: 640, height: 300 }}
      >
        <BarChart data={data ?? skillsData} layout="vertical" margin={{ top: 5, right: 15, left: 8, bottom: 5 }}>
          <CartesianGrid strokeDasharray="4 4" horizontal={false} stroke="#eef2f7" />
          <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 11 }} />
          <YAxis
            dataKey="skill"
            type="category"
            axisLine={false}
            tickLine={false}
            width={74}
            tick={{ fill: "#64748b", fontSize: 11 }}
          />
          <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "#f8fafc" }} />
          <Bar dataKey="candidates" fill="#2563EB" radius={[0, 5, 5, 0]} barSize={18} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
