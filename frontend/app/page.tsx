import {
  CircleCheckBig,
  Clock3,
  UserRoundCheck,
  UserRoundPlus,
  UsersRound,
} from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/dashboard/stat-card";
import {
  MonthlyApplicationsChart,
  StatusDistributionChart,
} from "@/components/dashboard/charts";
import {
  RecentApplicantsTable,
  TopCandidatesTable,
} from "@/components/dashboard/applicant-tables";

function SectionTitle({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-slate-100 px-4 py-4 sm:items-center sm:px-5">
      <div className="min-w-0">
        <h2 className="text-sm font-bold text-primary">{title}</h2>
        {description ? <p className="mt-0.5 text-[11px] text-slate-400">{description}</p> : null}
      </div>
      {action}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Saturday, June 6"
        title="Good morning, Alex"
        description="Here is what is happening with your recruitment pipeline today."
        actions={
          <Link href="/applicants">
            <Button>
              <UserRoundPlus className="h-4 w-4" />
              Add applicant
            </Button>
          </Link>
        }
      />

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard title="Total Applicants" value="247" change="12.4%" icon={UsersRound} tone="bg-blue-50 text-blue-600" />
        <StatCard title="New Applicants" value="52" change="8.2%" icon={UserRoundPlus} tone="bg-cyan-50 text-cyan-600" />
        <StatCard title="Under Review" value="74" change="4.1%" icon={Clock3} tone="bg-amber-50 text-amber-600" />
        <StatCard title="Shortlisted" value="38" change="16.8%" icon={CircleCheckBig} tone="bg-emerald-50 text-emerald-600" />
        <StatCard title="Rejected" value="59" change="3.2%" trend="down" icon={UserRoundCheck} tone="bg-rose-50 text-rose-600" />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.65fr_1fr]">
        <div className="surface overflow-hidden">
          <SectionTitle
            title="Monthly applications"
            description="Applicant volume over the last six months"
            action={
              <select className="focus-ring rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] font-medium text-slate-500">
                <option>Last 6 months</option>
              </select>
            }
          />
          <div className="px-3 pb-2 pt-3"><MonthlyApplicationsChart compact /></div>
        </div>
        <div className="surface overflow-hidden">
          <SectionTitle title="Application status" description="Current pipeline distribution" />
          <div className="px-4 py-3"><StatusDistributionChart /></div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.65fr_1fr]">
        <div className="surface overflow-hidden">
          <SectionTitle
            title="Recent applicants"
            description="Candidates received from your recruitment inbox"
            action={
              <Link href="/applicants" className="text-xs font-semibold text-accent hover:text-blue-700">
                View all
              </Link>
            }
          />
          <RecentApplicantsTable />
        </div>
        <div className="surface overflow-hidden">
          <SectionTitle title="Top candidates" description="Ranked by TalentFlow AI match score" />
          <TopCandidatesTable />
        </div>
      </section>
    </div>
  );
}
