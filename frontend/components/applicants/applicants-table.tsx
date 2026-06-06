"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Check,
  ChevronDown,
  Eye,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";
import Link from "next/link";
import { getApplicants } from "@/services/applicants";
import { getJobs } from "@/services/jobs";
import { ApiErrorState, TableSkeleton } from "@/components/ui/api-state";
import { Avatar } from "@/components/ui/avatar";
import { StatusBadge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Applicant, Job } from "@/types";

const PAGE_SIZE = 10;

const statusOptions: Array<{ label: string; value: string }> = [
  { label: "All statuses", value: "" },
  { label: "New", value: "new" },
  { label: "Under Review", value: "under_review" },
  { label: "Shortlisted", value: "shortlisted" },
  { label: "Interview", value: "interview" },
  { label: "Hired", value: "hired" },
  { label: "Rejected", value: "rejected" },
  { label: "Withdrawn", value: "withdrawn" },
];

const scoreOptions = [
  { label: "All scores", minimum: undefined, maximum: undefined },
  { label: "90+", minimum: 90, maximum: undefined },
  { label: "80-89", minimum: 80, maximum: 89.99 },
  { label: "Below 80", minimum: undefined, maximum: 79.99 },
];

export function ApplicantsTable() {
  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [search, setSearch] = useState("");
  const [jobId, setJobId] = useState("");
  const [status, setStatus] = useState("");
  const [scoreIndex, setScoreIndex] = useState(0);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getJobs({ pageSize: 100 })
      .then((response) => setJobs(response.data.items))
      .catch(() => setJobs([]));
  }, []);

  const loadApplicants = useCallback(async () => {
    setLoading(true);
    setError("");
    const score = scoreOptions[scoreIndex];

    try {
      const response = await getApplicants({
        page,
        pageSize: PAGE_SIZE,
        search: search.trim() || undefined,
        jobId: jobId || undefined,
        status: status || undefined,
        minimumScore: score.minimum,
        maximumScore: score.maximum,
      });
      setApplicants(response.data.items);
      setTotal(response.data.total);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Applicants could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }, [jobId, page, scoreIndex, search, status]);

  useEffect(() => {
    const timer = window.setTimeout(loadApplicants, 250);
    return () => window.clearTimeout(timer);
  }, [loadApplicants]);

  const updateFilter = (update: () => void) => {
    setPage(1);
    update();
  };
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const selectClass =
    "focus-ring h-10 appearance-none rounded-lg border border-slate-200 bg-white pl-3 pr-9 text-xs font-medium text-slate-600";

  return (
    <div className="surface overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-slate-100 p-4 xl:flex-row xl:items-center">
        <div className="relative min-w-0 flex-1 xl:max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(event) => updateFilter(() => setSearch(event.target.value))}
            placeholder="Search by name or email..."
            className="focus-ring h-10 w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm placeholder:text-slate-400"
          />
        </div>
        <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap">
          <FilterSelect
            value={jobId}
            onChange={(value) => updateFilter(() => setJobId(value))}
            options={[
              { label: "All positions", value: "" },
              ...jobs.map((job) => ({ label: job.title, value: job.id })),
            ]}
            className={selectClass}
          />
          <FilterSelect
            value={status}
            onChange={(value) => updateFilter(() => setStatus(value))}
            options={statusOptions}
            className={selectClass}
          />
          <FilterSelect
            value={String(scoreIndex)}
            onChange={(value) =>
              updateFilter(() => setScoreIndex(Number(value)))
            }
            options={scoreOptions.map((option, index) => ({
              label: option.label,
              value: String(index),
            }))}
            className={selectClass}
          />
          <Button variant="outline" className="w-full px-3 sm:w-auto" disabled>
            <SlidersHorizontal className="h-4 w-4" />
            <span className="hidden sm:inline">More filters</span>
          </Button>
        </div>
      </div>

      {loading ? <TableSkeleton /> : null}
      {!loading && error ? (
        <ApiErrorState message={error} onRetry={loadApplicants} />
      ) : null}
      {!loading && !error && applicants.length ? (
        <>
          <div className="divide-y divide-slate-100 md:hidden">
            {applicants.map((applicant) => (
              <ApplicantMobileCard key={applicant.id} applicant={applicant} />
            ))}
          </div>
          <ApplicantDesktopTable applicants={applicants} />
        </>
      ) : null}
      {!loading && !error && applicants.length === 0 ? (
        <div className="grid place-items-center px-5 py-16 text-center">
          <Search className="mb-3 h-8 w-8 text-slate-300" />
          <p className="text-sm font-bold text-primary">No applicants found</p>
          <p className="mt-1 text-xs text-slate-400">
            New candidates will appear here after they are added or received.
          </p>
        </div>
      ) : null}

      {!loading && !error && total > 0 ? (
        <div className="flex flex-col gap-3 border-t border-slate-100 px-4 py-3 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-5">
          <span>
            Showing {(page - 1) * PAGE_SIZE + 1}-
            {Math.min(page * PAGE_SIZE, total)} of {total} applicants
          </span>
          <div className="flex gap-1">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage((value) => value - 1)}>
              Previous
            </Button>
            <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)}>
              Next
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function FilterSelect({
  value,
  onChange,
  options,
  className,
}: {
  value: string;
  onChange: (value: string) => void;
  options: Array<{ label: string; value: string }>;
  className: string;
}) {
  return (
    <label className="relative min-w-0">
      <select value={value} onChange={(event) => onChange(event.target.value)} className={`${className} w-full`}>
        {options.map((option) => <option key={`${option.label}-${option.value}`} value={option.value}>{option.label}</option>)}
      </select>
      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
    </label>
  );
}

function ApplicantMobileCard({ applicant }: { applicant: Applicant }) {
  return (
    <article className="p-4">
      <div className="flex items-start gap-3">
        <Avatar name={applicant.name} />
        <div className="min-w-0 flex-1">
          <Link href={`/applicants/${applicant.id}`} className="block truncate text-sm font-bold text-primary">{applicant.name}</Link>
          <p className="mt-0.5 truncate text-xs text-slate-400">{applicant.email}</p>
        </div>
        <div className="text-right">
          <p className="text-sm font-bold text-primary">{applicant.score || "—"}</p>
          <p className="text-[9px] font-bold uppercase tracking-wide text-slate-400">AI score</p>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-xs font-semibold text-slate-600">{applicant.position}</p>
          <p className="mt-1 text-[10px] text-slate-400">Applied {applicant.appliedAt}</p>
        </div>
        <StatusBadge status={applicant.status} />
      </div>
      <ApplicantActions applicantId={applicant.id} mobile />
    </article>
  );
}

function ApplicantDesktopTable({ applicants }: { applicants: Applicant[] }) {
  return (
    <div className="hidden overflow-x-auto md:block">
      <table className="w-full min-w-[900px] text-left">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50/60 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            <th className="px-5 py-3">Candidate</th>
            <th className="px-4 py-3">Position</th>
            <th className="px-4 py-3">AI Score</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Date Applied</th>
            <th className="px-5 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {applicants.map((applicant) => (
            <tr key={applicant.id} className="table-row text-xs">
              <td className="px-5 py-3.5">
                <Link href={`/applicants/${applicant.id}`} className="flex items-center gap-3">
                  <Avatar name={applicant.name} />
                  <span>
                    <span className="block font-bold text-primary">{applicant.name}</span>
                    <span className="mt-0.5 block text-[11px] text-slate-400">{applicant.email}</span>
                  </span>
                </Link>
              </td>
              <td className="px-4 py-3.5 font-medium text-slate-600">{applicant.position}</td>
              <td className="px-4 py-3.5 font-bold text-primary">{applicant.score || "—"}</td>
              <td className="px-4 py-3.5"><StatusBadge status={applicant.status} /></td>
              <td className="px-4 py-3.5 text-slate-500">{applicant.appliedAt}</td>
              <td className="px-5 py-3.5"><ApplicantActions applicantId={applicant.id} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ApplicantActions({ applicantId, mobile = false }: { applicantId: string; mobile?: boolean }) {
  const className = mobile
    ? "mt-4 grid grid-cols-3 gap-2 border-t border-slate-100 pt-3"
    : "flex items-center justify-end gap-1";
  return (
    <div className={className}>
      <Link href={`/applicants/${applicantId}`} className={mobile ? "focus-ring flex h-9 items-center justify-center gap-1.5 rounded-lg bg-blue-50 text-xs font-semibold text-accent" : "focus-ring rounded-md p-2 text-slate-400 hover:bg-blue-50 hover:text-accent"}>
        <Eye className="h-4 w-4" /> {mobile ? "View" : null}
      </Link>
      <button disabled title="Recruiter sign-in is required" className={mobile ? "flex h-9 items-center justify-center gap-1.5 rounded-lg bg-slate-50 text-xs font-semibold text-slate-400" : "rounded-md p-2 text-slate-300"}>
        <Check className="h-4 w-4" /> {mobile ? "Shortlist" : null}
      </button>
      <button disabled title="Recruiter sign-in is required" className={mobile ? "flex h-9 items-center justify-center gap-1.5 rounded-lg bg-slate-50 text-xs font-semibold text-slate-400" : "rounded-md p-2 text-slate-300"}>
        <X className="h-4 w-4" /> {mobile ? "Reject" : null}
      </button>
    </div>
  );
}
