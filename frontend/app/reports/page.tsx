import { BriefcaseBusiness, CirclePercent, Gauge, UsersRound } from "lucide-react";
import { MonthlyApplicationsChart, StatusDistributionChart, TopSkillsChart } from "@/components/dashboard/charts";
import { StatCard } from "@/components/dashboard/stat-card";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

const positions = [
  { name: "Frontend Engineer", count: 64, percent: 100 },
  { name: "Senior Product Designer", count: 48, percent: 75 },
  { name: "Backend Engineer", count: 37, percent: 58 },
  { name: "Product Manager", count: 29, percent: 45 },
  { name: "AI Engineer", count: 22, percent: 34 },
];

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Recruitment analytics"
        description="Measure pipeline health, candidate quality, and hiring activity."
        actions={
          <>
            <select className="focus-ring h-10 min-w-0 flex-1 rounded-lg border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-600 sm:flex-none"><option>Last 6 months</option></select>
            <Button variant="outline" className="flex-1 sm:flex-none"><Download className="h-4 w-4" /> Export report</Button>
          </>
        }
      />
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total Applications" value="543" change="14.2%" icon={UsersRound} tone="bg-blue-50 text-blue-600" />
        <StatCard title="Open Positions" value="12" change="9.1%" icon={BriefcaseBusiness} tone="bg-violet-50 text-violet-600" />
        <StatCard title="Average AI Score" value="81.4" change="2.8%" icon={Gauge} tone="bg-amber-50 text-amber-600" />
        <StatCard title="Shortlisted Rate" value="22.8%" change="4.6%" icon={CirclePercent} tone="bg-emerald-50 text-emerald-600" />
      </section>
      <section className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <ChartCard title="Monthly applications" description="Applications received across all positions">
          <div className="px-3 pb-3 pt-2"><MonthlyApplicationsChart /></div>
        </ChartCard>
        <ChartCard title="Applicant status distribution" description="Current pipeline composition">
          <div className="px-5 py-5"><StatusDistributionChart /></div>
        </ChartCard>
      </section>
      <section className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Top candidate skills" description="Most common skills across active candidates">
          <div className="px-3 py-2"><TopSkillsChart /></div>
        </ChartCard>
        <ChartCard title="Applications per position" description="Roles attracting the most candidate interest">
          <div className="space-y-5 p-5">
            {positions.map((position) => (
              <div key={position.name}>
                <div className="mb-2 flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-600">{position.name}</span>
                  <span className="font-bold text-primary">{position.count}</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                  <div className="h-full rounded-full bg-accent" style={{ width: `${position.percent}%` }} />
                </div>
              </div>
            ))}
          </div>
        </ChartCard>
      </section>
    </div>
  );
}

function ChartCard({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
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
