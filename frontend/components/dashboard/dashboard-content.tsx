"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CircleCheckBig,
  Clock3,
  UserRoundCheck,
  UserRoundPlus,
  UsersRound,
} from "lucide-react";
import Link from "next/link";
import { getAllApplicants } from "@/services/applicants";
import { useAuth } from "@/components/auth/auth-provider";
import { RecentApplicantsTable, TopCandidatesTable } from "@/components/dashboard/applicant-tables";
import { MonthlyApplicationsChart, StatusDistributionChart } from "@/components/dashboard/charts";
import { StatCard } from "@/components/dashboard/stat-card";
import { PageSkeleton } from "@/components/loading/page-skeleton";
import { ApiErrorState } from "@/components/ui/api-state";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import type { Applicant, ApplicantStatus } from "@/types";

const statusColors: Record<ApplicantStatus, string> = {
  New: "#2563EB",
  "Under Review": "#F59E0B",
  Shortlisted: "#22C55E",
  Interview: "#8B5CF6",
  Hired: "#14B8A6",
  Rejected: "#CBD5E1",
  Withdrawn: "#64748B",
};

export function DashboardContent() {
  const { user } = useAuth();
  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setApplicants(await getAllApplicants());
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Dashboard data could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const statusCounts = useMemo(
    () =>
      applicants.reduce<Record<string, number>>((counts, applicant) => {
        counts[applicant.status] = (counts[applicant.status] ?? 0) + 1;
        return counts;
      }, {}),
    [applicants],
  );
  const monthlyData = useMemo(() => buildMonthlyData(applicants), [applicants]);
  const statusData = Object.entries(statusColors).map(([name, color]) => ({
    name,
    color,
    value: statusCounts[name] ?? 0,
  }));
  const recentApplicants = applicants.slice(0, 5);
  const topCandidates = [...applicants]
    .filter((applicant) => applicant.score > 0)
    .sort((first, second) => second.score - first.score)
    .slice(0, 4);
  const recruiterName =
    user?.user_metadata.full_name || user?.email?.split("@")[0] || "Recruiter";

  if (loading) return <PageSkeleton />;
  if (error) {
    return (
      <div className="surface">
        <ApiErrorState message={error} onRetry={loadDashboard} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={new Intl.DateTimeFormat("en-US", { dateStyle: "full" }).format(new Date())}
        title={`Good day, ${recruiterName}`}
        description="Here is the current state of your recruitment pipeline."
        actions={
          <Link href="/applicants">
            <Button><UserRoundPlus className="h-4 w-4" /> Add applicant</Button>
          </Link>
        }
      />

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard title="Total Applicants" value={String(applicants.length)} icon={UsersRound} tone="bg-blue-50 text-blue-600" />
        <StatCard title="New Applicants" value={String(statusCounts.New ?? 0)} icon={UserRoundPlus} tone="bg-cyan-50 text-cyan-600" />
        <StatCard title="Under Review" value={String(statusCounts["Under Review"] ?? 0)} icon={Clock3} tone="bg-amber-50 text-amber-600" />
        <StatCard title="Shortlisted" value={String(statusCounts.Shortlisted ?? 0)} icon={CircleCheckBig} tone="bg-emerald-50 text-emerald-600" />
        <StatCard title="Rejected" value={String(statusCounts.Rejected ?? 0)} icon={UserRoundCheck} tone="bg-rose-50 text-rose-600" />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.65fr_1fr]">
        <DashboardCard title="Monthly applications" description="Applicant volume over the last six months">
          <div className="px-3 pb-2 pt-3"><MonthlyApplicationsChart compact data={monthlyData} /></div>
        </DashboardCard>
        <DashboardCard title="Application status" description="Current pipeline distribution">
          <div className="px-4 py-3"><StatusDistributionChart data={statusData} /></div>
        </DashboardCard>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.65fr_1fr]">
        <DashboardCard
          title="Recent applicants"
          description="Latest candidates in your recruitment pipeline"
          action={<Link href="/applicants" className="text-xs font-semibold text-accent hover:text-blue-700">View all</Link>}
        >
          {recentApplicants.length ? <RecentApplicantsTable applicants={recentApplicants} /> : <EmptyDashboardState label="No applicants yet" />}
        </DashboardCard>
        <DashboardCard title="Top candidates" description="Ranked by current AI match score">
          {topCandidates.length ? <TopCandidatesTable applicants={topCandidates} /> : <EmptyDashboardState label="AI scores will appear here" />}
        </DashboardCard>
      </section>
    </div>
  );
}

function DashboardCard({
  title,
  description,
  action,
  children,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="surface overflow-hidden">
      <div className="flex items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">
        <div>
          <h2 className="text-sm font-bold text-primary">{title}</h2>
          <p className="mt-0.5 text-[11px] text-slate-400">{description}</p>
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}

function EmptyDashboardState({ label }: { label: string }) {
  return <p className="px-5 py-12 text-center text-xs text-slate-400">{label}</p>;
}

function buildMonthlyData(applicants: Applicant[]) {
  const now = new Date();
  return Array.from({ length: 6 }, (_, index) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (5 - index), 1);
    const month = new Intl.DateTimeFormat("en-US", { month: "short" }).format(date);
    const matchingApplicants = applicants.filter((applicant) => {
      if (!applicant.appliedAtRaw) return false;
      const appliedAt = new Date(applicant.appliedAtRaw);
      return appliedAt.getFullYear() === date.getFullYear() && appliedAt.getMonth() === date.getMonth();
    });
    return {
      month,
      applications: matchingApplicants.length,
      shortlisted: matchingApplicants.filter((applicant) => applicant.status === "Shortlisted").length,
    };
  });
}
