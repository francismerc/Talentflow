import type { ApplicantStatus } from "@/types";
import { cn } from "@/lib/utils";

const statusStyles: Record<ApplicantStatus | "Active" | "Draft" | "Closed", string> = {
  New: "bg-blue-50 text-blue-700 ring-blue-600/15",
  "Under Review": "bg-amber-50 text-amber-700 ring-amber-600/15",
  Shortlisted: "bg-emerald-50 text-emerald-700 ring-emerald-600/15",
  Interview: "bg-violet-50 text-violet-700 ring-violet-600/15",
  Rejected: "bg-slate-100 text-slate-600 ring-slate-500/15",
  Active: "bg-emerald-50 text-emerald-700 ring-emerald-600/15",
  Draft: "bg-amber-50 text-amber-700 ring-amber-600/15",
  Closed: "bg-slate-100 text-slate-600 ring-slate-500/15",
};

export function StatusBadge({ status }: { status: keyof typeof statusStyles }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset",
        statusStyles[status],
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}
