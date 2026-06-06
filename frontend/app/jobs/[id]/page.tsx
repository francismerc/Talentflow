import { ArrowLeft, BriefcaseBusiness, CalendarDays, Edit3, MapPin, Users } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { applicants, jobs } from "@/lib/mock-data";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { ScoreRing } from "@/components/ui/score-ring";
import { StatusBadge } from "@/components/ui/badge";

export function generateStaticParams() {
  return jobs.map((job) => ({ id: job.id }));
}

export default async function JobDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const job = jobs.find((item) => item.id === id);
  if (!job) notFound();

  const matchingCandidates = applicants
    .filter((applicant) => applicant.position === job.title)
    .sort((a, b) => b.score - a.score);

  return (
    <div className="space-y-5">
      <Link href="/jobs" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-primary">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to jobs
      </Link>
      <section className="surface p-4 sm:p-5">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start">
          <span className="grid h-14 w-14 shrink-0 place-items-center rounded-xl bg-blue-50 text-accent">
            <BriefcaseBusiness className="h-6 w-6" />
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight text-primary">{job.title}</h1>
              <StatusBadge status={job.status} />
            </div>
            <p className="mt-1 text-sm text-slate-500">{job.department} · {job.type}</p>
            <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
              <span className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5" />{job.location}</span>
              <span className="flex items-center gap-1.5"><CalendarDays className="h-3.5 w-3.5" />Created {job.createdAt}</span>
              <span className="flex items-center gap-1.5"><Users className="h-3.5 w-3.5" />{job.applicants} applicants</span>
            </div>
          </div>
          <Button variant="outline" className="w-full lg:w-auto"><Edit3 className="h-4 w-4" /> Edit job</Button>
        </div>
      </section>

      <div className="grid gap-5 xl:grid-cols-[1.4fr_1fr]">
        <div className="space-y-5">
          <section className="surface p-5">
            <h2 className="text-sm font-bold text-primary">Job information</h2>
            <p className="mt-4 text-sm leading-7 text-slate-600">{job.description}</p>
            <h3 className="mt-6 text-xs font-bold text-primary">What you will do</h3>
            <ul className="mt-3 space-y-2 text-xs leading-5 text-slate-600">
              <li>• Own high-impact initiatives from discovery through production.</li>
              <li>• Collaborate closely with product, design, and engineering partners.</li>
              <li>• Improve team standards, systems, and customer outcomes.</li>
            </ul>
          </section>
          <section className="surface p-5">
            <h2 className="text-sm font-bold text-primary">Required skills</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {job.skills.map((skill) => (
                <span key={skill} className="rounded-lg border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700">{skill}</span>
              ))}
            </div>
          </section>
        </div>

        <section className="surface self-start overflow-hidden">
          <div className="border-b border-slate-100 px-5 py-4">
            <h2 className="text-sm font-bold text-primary">Top matching candidates</h2>
            <p className="mt-0.5 text-[11px] text-slate-400">Ranked by AI match score for this role</p>
          </div>
          {matchingCandidates.length ? (
            <div className="divide-y divide-slate-100">
              {matchingCandidates.map((candidate, index) => (
                <Link key={candidate.id} href={`/applicants/${candidate.id}`} className="flex items-center gap-3 px-5 py-4 hover:bg-slate-50">
                  <span className="w-4 text-[11px] font-bold text-slate-300">{index + 1}</span>
                  <Avatar name={candidate.name} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-bold text-primary">{candidate.name}</p>
                    <p className="mt-0.5 truncate text-[11px] text-slate-400">{candidate.experience} experience</p>
                  </div>
                  <ScoreRing score={candidate.score} size="sm" />
                </Link>
              ))}
            </div>
          ) : (
            <div className="px-5 py-12 text-center">
              <Users className="mx-auto h-8 w-8 text-slate-300" />
              <p className="mt-3 text-xs font-bold text-primary">No candidates yet</p>
              <p className="mt-1 text-[11px] text-slate-400">Matching candidates will appear here.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
