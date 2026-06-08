"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  BriefcaseBusiness,
  CalendarDays,
  Edit3,
  MapPin,
  Users,
} from "lucide-react";
import Link from "next/link";
import { getJob } from "@/services/jobs";
import { JobFormModal } from "@/components/jobs/job-form-modal";
import { ApiErrorState } from "@/components/ui/api-state";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { PageSkeleton } from "@/components/loading/page-skeleton";
import { ScoreRing } from "@/components/ui/score-ring";
import { StatusBadge } from "@/components/ui/badge";
import type { JobDetail } from "@/types";

export function JobDetailPage({ jobId }: { jobId: string }) {
  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editOpen, setEditOpen] = useState(false);

  const loadJob = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setJob(await getJob(jobId));
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Job details could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    loadJob();
  }, [loadJob]);

  if (loading) return <PageSkeleton />;
  if (error) {
    return (
      <div className="surface">
        <ApiErrorState message={error} onRetry={loadJob} />
      </div>
    );
  }
  if (!job) return null;

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
            <p className="mt-1 text-sm text-slate-500">{job.type}</p>
            <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
              <span className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5" />{job.location}</span>
              <span className="flex items-center gap-1.5"><CalendarDays className="h-3.5 w-3.5" />Created {job.createdAt}</span>
              <span className="flex items-center gap-1.5"><Users className="h-3.5 w-3.5" />{job.applicants} applicants</span>
            </div>
          </div>
          <Button onClick={() => setEditOpen(true)} variant="outline" className="w-full lg:w-auto">
            <Edit3 className="h-4 w-4" /> Edit job
          </Button>
        </div>
      </section>

      <div className="grid gap-5 xl:grid-cols-[1.4fr_1fr]">
        <div className="space-y-5">
          <section className="surface p-5">
            <h2 className="text-sm font-bold text-primary">Job information</h2>
            <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-600">
              {job.description || "No job description has been added."}
            </p>
          </section>
          <section className="surface p-5">
            <h2 className="text-sm font-bold text-primary">Required skills</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {job.skills.map((skill) => (
                <span key={skill} className="rounded-lg border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700">{skill}</span>
              ))}
              {!job.skills.length ? <p className="text-xs text-slate-400">No required skills added.</p> : null}
            </div>
          </section>
        </div>

        <section className="surface self-start overflow-hidden">
          <div className="border-b border-slate-100 px-5 py-4">
            <h2 className="text-sm font-bold text-primary">Top matching candidates</h2>
            <p className="mt-0.5 text-[11px] text-slate-400">Ranked by the current AI match score</p>
          </div>
          {job.candidates.length ? (
            <div className="divide-y divide-slate-100">
              {[...job.candidates]
                .sort((first, second) => second.score - first.score)
                .map((candidate, index) => (
                  <Link key={candidate.id} href={`/applicants/${candidate.id}`} className="flex items-center gap-3 px-5 py-4 hover:bg-slate-50">
                    <span className="w-4 text-[11px] font-bold text-slate-300">{index + 1}</span>
                    <Avatar name={candidate.name} />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-bold text-primary">{candidate.name}</p>
                      <p className="mt-0.5 truncate text-[11px] text-slate-400">{candidate.status}</p>
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
      <JobFormModal
        open={editOpen}
        job={job}
        onClose={() => setEditOpen(false)}
        onSaved={() => loadJob()}
      />
    </div>
  );
}
