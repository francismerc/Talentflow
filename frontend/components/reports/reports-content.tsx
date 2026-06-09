"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  BriefcaseBusiness,
  CirclePercent,
  Download,
  FileText,
  Gauge,
  UsersRound,
} from "lucide-react";
import {
  MonthlyApplicationsChart,
  StatusDistributionChart,
  TopSkillsChart,
} from "@/components/dashboard/charts";
import { StatCard } from "@/components/dashboard/stat-card";
import { ReportsSkeleton } from "@/components/reports/reports-skeleton";
import { ApiErrorState } from "@/components/ui/api-state";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import {
  getRecruitmentReport,
  type RecruitmentReport,
} from "@/services/reports";

const reportRanges = [3, 6, 12];

const statusPresentation: Record<string, { name: string; color: string }> = {
  new: { name: "New", color: "#2563EB" },
  under_review: { name: "Under Review", color: "#F59E0B" },
  shortlisted: { name: "Shortlisted", color: "#22C55E" },
  interview: { name: "Interview", color: "#8B5CF6" },
  hired: { name: "Hired", color: "#14B8A6" },
  rejected: { name: "Rejected", color: "#EF4444" },
  withdrawn: { name: "Withdrawn", color: "#94A3B8" },
};

export function ReportsContent() {
  const [months, setMonths] = useState(6);
  const [report, setReport] = useState<RecruitmentReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadReport = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setReport(await getRecruitmentReport(months));
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The recruitment report could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }, [months]);

  useEffect(() => {
    void loadReport();
  }, [loadReport]);

  const statusData = useMemo(
    () =>
      (report?.status_distribution ?? [])
        .filter((item) => item.count > 0)
        .map((item) => ({
          name: statusPresentation[item.status]?.name ?? formatLabel(item.status),
          value: item.count,
          color: statusPresentation[item.status]?.color ?? "#64748B",
        })),
    [report],
  );

  if (loading && !report) return <ReportsSkeleton />;
  if (error && !report) {
    return (
      <div className="surface">
        <ApiErrorState message={error} onRetry={() => void loadReport()} />
      </div>
    );
  }
  if (!report) return null;

  const maximumPositionCount = Math.max(
    ...report.top_positions.map((position) => position.count),
    1,
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Recruitment analytics"
        description="Measure pipeline health, candidate quality, and hiring activity."
        actions={
          <>
            <select
              value={months}
              onChange={(event) => setMonths(Number(event.target.value))}
              disabled={loading}
              aria-label="Report period"
              className="focus-ring h-10 min-w-0 flex-1 rounded-lg border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-600 disabled:opacity-60 sm:flex-none"
            >
              {reportRanges.map((range) => (
                <option key={range} value={range}>
                  Last {range} months
                </option>
              ))}
            </select>
            <Button
              variant="outline"
              className="flex-1 sm:flex-none"
              onClick={() => exportReport(report)}
              disabled={loading}
            >
              <Download className="h-4 w-4" /> Export CSV
            </Button>
          </>
        }
      />

      {error ? (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
          {error} Showing the most recently loaded report.
        </div>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total Applications" value={String(report.total_applications)} icon={UsersRound} tone="bg-blue-50 text-blue-600" />
        <StatCard title="Open Positions" value={String(report.open_positions)} icon={BriefcaseBusiness} tone="bg-violet-50 text-violet-600" />
        <StatCard title="Average AI Score" value={report.average_candidate_score === null ? "N/A" : report.average_candidate_score.toFixed(1)} icon={Gauge} tone="bg-amber-50 text-amber-600" />
        <StatCard title="Shortlisted Rate" value={`${report.shortlisted_rate.toFixed(1)}%`} icon={CirclePercent} tone="bg-emerald-50 text-emerald-600" />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <ChartCard title="Monthly applications" description="Applications received across all positions">
          <div className="px-3 pb-3 pt-2">
            <MonthlyApplicationsChart data={report.monthly_applications} />
          </div>
        </ChartCard>
        <ChartCard title="Applicant status distribution" description="Current pipeline composition">
          <div className="px-5 py-5">
            {statusData.length ? (
              <StatusDistributionChart data={statusData} />
            ) : (
              <EmptyReportState label="No applicant statuses in this period" />
            )}
          </div>
        </ChartCard>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Top candidate skills" description="Most common skills across candidates in this period">
          <div className="px-3 py-2">
            {report.top_skills.length ? (
              <TopSkillsChart data={report.top_skills.map((item) => ({
                skill: item.skill,
                candidates: item.count,
              }))} />
            ) : (
              <EmptyReportState label="No candidate skills available" />
            )}
          </div>
        </ChartCard>
        <ChartCard title="Applications per position" description="Roles attracting the most candidate interest">
          {report.top_positions.length ? (
            <div className="space-y-5 p-5">
              {report.top_positions.map((position) => (
                <div key={position.job_id}>
                  <div className="mb-2 flex items-center justify-between gap-3 text-xs">
                    <span className="truncate font-semibold text-slate-600">{position.title}</span>
                    <span className="font-bold text-primary">{position.count}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-accent"
                      style={{
                        width: `${(position.count / maximumPositionCount) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyReportState label="No position activity in this period" />
          )}
        </ChartCard>
      </section>

      <section className="surface flex items-start gap-3 p-5">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-blue-50 text-accent">
          <FileText className="h-4 w-4" />
        </span>
        <div>
          <h2 className="text-sm font-bold text-primary">Recruitment summary</h2>
          <p className="mt-1.5 text-xs leading-6 text-slate-500">{report.summary}</p>
          <p className="mt-2 text-[10px] text-slate-400">
            Reporting period: {formatDate(report.period_start)} to {formatDate(report.period_end)}
          </p>
        </div>
      </section>
    </div>
  );
}

function ChartCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="surface overflow-hidden">
      <div className="border-b border-slate-100 px-5 py-4">
        <h2 className="text-sm font-bold text-primary">{title}</h2>
        <p className="mt-0.5 text-[11px] text-slate-400">{description}</p>
      </div>
      {children}
    </div>
  );
}

function EmptyReportState({ label }: { label: string }) {
  return (
    <div className="grid min-h-52 place-items-center px-4 text-center text-xs text-slate-400">
      {label}
    </div>
  );
}

function formatLabel(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function exportReport(report: RecruitmentReport) {
  const rows = [
    ["TalentFlow AI Recruitment Report"],
    ["Period", `${formatDate(report.period_start)} - ${formatDate(report.period_end)}`],
    ["Total applications", report.total_applications],
    ["Open positions", report.open_positions],
    ["Average AI score", report.average_candidate_score ?? "N/A"],
    ["Shortlisted rate", `${report.shortlisted_rate.toFixed(1)}%`],
    [],
    ["Monthly applications"],
    ["Month", "Applications", "Shortlisted or advanced"],
    ...report.monthly_applications.map((item) => [
      item.month,
      item.applications,
      item.shortlisted,
    ]),
    [],
    ["Top positions"],
    ["Position", "Applications"],
    ...report.top_positions.map((item) => [item.title, item.count]),
    [],
    ["Top skills"],
    ["Skill", "Candidates"],
    ...report.top_skills.map((item) => [item.skill, item.count]),
  ];
  const csv = rows
    .map((row) => row.map((value) => escapeCsvValue(value)).join(","))
    .join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = `talentflow-report-${report.months}-months.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

function escapeCsvValue(value: string | number): string {
  const text = String(value);
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}
