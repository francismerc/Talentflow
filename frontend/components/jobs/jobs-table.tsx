"use client";

import { useCallback, useEffect, useState } from "react";
import {
  BriefcaseBusiness,
  Edit3,
  Eye,
  Search,
  Trash2,
} from "lucide-react";
import Link from "next/link";
import { deleteJob, getJobs } from "@/services/jobs";
import { JobFormModal } from "@/components/jobs/job-form-modal";
import { ApiErrorState, TableSkeleton } from "@/components/ui/api-state";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/badge";
import { ConfirmDialog } from "@/components/ui/modal";
import type { Job } from "@/types";

const PAGE_SIZE = 10;

export function JobsTable({ createRequest = 0 }: { createRequest?: number }) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [deletingJob, setDeletingJob] = useState<Job | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (createRequest > 0) {
      setEditingJob(null);
      setFormOpen(true);
    }
  }, [createRequest]);

  const loadJobs = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await getJobs({
        page,
        pageSize: PAGE_SIZE,
        search: search.trim() || undefined,
      });
      setJobs(response.data.items);
      setTotal(response.data.total);
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Jobs could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    const timer = window.setTimeout(loadJobs, 250);
    return () => window.clearTimeout(timer);
  }, [loadJobs]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const handleDelete = async () => {
    if (!deletingJob) return;
    setDeleting(true);
    setError("");
    try {
      await deleteJob(deletingJob.id);
      setDeletingJob(null);
      await loadJobs();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Job could not be deleted.");
      setDeletingJob(null);
    } finally {
      setDeleting(false);
    }
  };
  const openEdit = (job: Job) => {
    setEditingJob(job);
    setFormOpen(true);
  };

  return (
    <>
      <div className="surface overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative max-w-sm flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(event) => {
                setPage(1);
                setSearch(event.target.value);
              }}
              placeholder="Search jobs..."
              className="focus-ring h-10 w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm"
            />
          </div>
          <p className="text-xs font-medium text-slate-400">{total} positions</p>
        </div>

        {loading ? <TableSkeleton /> : null}
        {!loading && error ? (
          <ApiErrorState message={error} onRetry={loadJobs} />
        ) : null}
        {!loading && !error && jobs.length ? (
          <>
            <div className="divide-y divide-slate-100 md:hidden">
              {jobs.map((job) => (
                <JobMobileCard
                  key={job.id}
                  job={job}
                  onEdit={openEdit}
                  onDelete={setDeletingJob}
                />
              ))}
            </div>
            <JobDesktopTable jobs={jobs} onEdit={openEdit} onDelete={setDeletingJob} />
          </>
        ) : null}
        {!loading && !error && jobs.length === 0 ? (
          <div className="grid place-items-center px-5 py-16 text-center">
            <BriefcaseBusiness className="h-8 w-8 text-slate-300" />
            <p className="mt-3 text-sm font-bold text-primary">No jobs found</p>
            <p className="mt-1 text-xs text-slate-400">
              Create your first opening to begin receiving candidates.
            </p>
          </div>
        ) : null}
        {!loading && !error && total > 0 ? (
          <div className="flex items-center justify-between border-t border-slate-100 px-5 py-3 text-xs text-slate-500">
            <span>
              Showing {(page - 1) * PAGE_SIZE + 1}-{Math.min(page * PAGE_SIZE, total)} of {total}
            </span>
            <div className="flex gap-1">
              <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage((value) => value - 1)}>Previous</Button>
              <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)}>Next</Button>
            </div>
          </div>
        ) : null}
      </div>

      <JobFormModal
        open={formOpen}
        job={editingJob}
        onClose={() => setFormOpen(false)}
        onSaved={() => loadJobs()}
      />
      <ConfirmDialog
        open={Boolean(deletingJob)}
        title="Delete job?"
        description={
          deletingJob
            ? `This permanently deletes “${deletingJob.title}”. Jobs with applicants cannot be deleted.`
            : ""
        }
        confirmLabel="Delete job"
        loading={deleting}
        onCancel={() => setDeletingJob(null)}
        onConfirm={handleDelete}
      />
    </>
  );
}

function JobMobileCard({
  job,
  onEdit,
  onDelete,
}: {
  job: Job;
  onEdit: (job: Job) => void;
  onDelete: (job: Job) => void;
}) {
  return (
    <article className="p-4">
      <div className="flex items-start gap-3">
        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-slate-100 text-slate-600">
          <BriefcaseBusiness className="h-4 w-4" />
        </span>
        <div className="min-w-0 flex-1">
          <Link href={`/jobs/${job.id}`} className="block truncate text-sm font-bold text-primary">{job.title}</Link>
          <p className="mt-1 truncate text-[11px] text-slate-400">{job.type} · {job.location}</p>
        </div>
        <StatusBadge status={job.status} />
      </div>
      <div className="mt-4 flex flex-wrap gap-1.5">
        {job.skills.slice(0, 3).map((skill) => (
          <span key={skill} className="rounded-md bg-slate-100 px-2 py-1 text-[10px] font-medium text-slate-600">{skill}</span>
        ))}
      </div>
      <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
        <div>
          <p className="text-xs font-bold text-primary">{job.applicants} applicants</p>
          <p className="mt-0.5 text-[10px] text-slate-400">Created {job.createdAt}</p>
        </div>
        <JobActions job={job} onEdit={onEdit} onDelete={onDelete} />
      </div>
    </article>
  );
}

function JobDesktopTable({
  jobs,
  onEdit,
  onDelete,
}: {
  jobs: Job[];
  onEdit: (job: Job) => void;
  onDelete: (job: Job) => void;
}) {
  return (
    <div className="hidden overflow-x-auto md:block">
      <table className="w-full min-w-[860px] text-left">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50/60 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            <th className="px-5 py-3">Job title</th>
            <th className="px-4 py-3">Required skills</th>
            <th className="px-4 py-3">Applicants</th>
            <th className="px-4 py-3">Created</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-5 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id} className="table-row text-xs">
              <td className="px-5 py-4">
                <Link href={`/jobs/${job.id}`} className="flex items-center gap-3">
                  <span className="grid h-9 w-9 place-items-center rounded-lg bg-slate-100 text-slate-600"><BriefcaseBusiness className="h-4 w-4" /></span>
                  <span>
                    <span className="block font-bold text-primary">{job.title}</span>
                    <span className="mt-0.5 block text-[11px] text-slate-400">{job.type} · {job.location}</span>
                  </span>
                </Link>
              </td>
              <td className="max-w-[300px] px-4 py-4">
                <div className="flex flex-wrap gap-1">
                  {job.skills.slice(0, 3).map((skill) => <span key={skill} className="rounded-md bg-slate-100 px-2 py-1 text-[10px] font-medium text-slate-600">{skill}</span>)}
                </div>
              </td>
              <td className="px-4 py-4 font-bold text-primary">{job.applicants}</td>
              <td className="px-4 py-4 text-slate-500">{job.createdAt}</td>
              <td className="px-4 py-4"><StatusBadge status={job.status} /></td>
              <td className="px-5 py-4"><JobActions job={job} onEdit={onEdit} onDelete={onDelete} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function JobActions({
  job,
  onEdit,
  onDelete,
}: {
  job: Job;
  onEdit: (job: Job) => void;
  onDelete: (job: Job) => void;
}) {
  return (
    <div className="flex justify-end gap-1">
      <Link href={`/jobs/${job.id}`} className="focus-ring rounded-md p-2 text-slate-400 hover:bg-blue-50 hover:text-accent"><Eye className="h-4 w-4" /></Link>
      <button onClick={() => onEdit(job)} title="Edit job" className="focus-ring rounded-md p-2 text-slate-400 hover:bg-slate-100 hover:text-primary"><Edit3 className="h-4 w-4" /></button>
      <button onClick={() => onDelete(job)} title="Delete job" className="focus-ring rounded-md p-2 text-slate-400 hover:bg-red-50 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
    </div>
  );
}
