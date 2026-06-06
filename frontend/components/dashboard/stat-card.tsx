import type { LucideIcon } from "lucide-react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";

export function StatCard({
  title,
  value,
  change,
  trend = "up",
  icon: Icon,
  tone,
}: {
  title: string;
  value: string;
  change: string;
  trend?: "up" | "down";
  icon: LucideIcon;
  tone: string;
}) {
  const TrendIcon = trend === "up" ? ArrowUpRight : ArrowDownRight;
  return (
    <div className="surface p-4 xl:p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500">{title}</p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-primary">{value}</p>
        </div>
        <span className={cn("grid h-9 w-9 place-items-center rounded-xl", tone)}>
          <Icon className="h-[18px] w-[18px]" />
        </span>
      </div>
      <div className="mt-4 flex items-center gap-1 text-[11px]">
        <span
          className={cn(
            "inline-flex items-center font-bold",
            trend === "up" ? "text-emerald-600" : "text-red-500",
          )}
        >
          <TrendIcon className="mr-0.5 h-3 w-3" />
          {change}
        </span>
        <span className="text-slate-400">vs. last month</span>
      </div>
    </div>
  );
}
