"use client";

import { useMemo, useState } from "react";
import {
  Check,
  ChevronDown,
  Eye,
  MoreHorizontal,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";
import Link from "next/link";
import { applicants } from "@/lib/mock-data";
import { Avatar } from "@/components/ui/avatar";
import { StatusBadge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { ApplicantStatus } from "@/types";

export function ApplicantsTable() {
  const [search, setSearch] = useState("");
  const [position, setPosition] = useState("All positions");
  const [status, setStatus] = useState("All statuses");
  const [score, setScore] = useState("All scores");

  const filteredApplicants = useMemo(() => {
    return applicants.filter((applicant) => {
      const matchesSearch =
        applicant.name.toLowerCase().includes(search.toLowerCase()) ||
        applicant.email.toLowerCase().includes(search.toLowerCase());
      const matchesPosition = position === "All positions" || applicant.position === position;
      const matchesStatus = status === "All statuses" || applicant.status === status;
      const matchesScore =
        score === "All scores" ||
        (score === "90+" && applicant.score >= 90) ||
        (score === "80-89" && applicant.score >= 80 && applicant.score < 90) ||
        (score === "Below 80" && applicant.score < 80);
      return matchesSearch && matchesPosition && matchesStatus && matchesScore;
    });
  }, [position, score, search, status]);

  const selectClass =
    "focus-ring h-10 appearance-none rounded-lg border border-slate-200 bg-white pl-3 pr-9 text-xs font-medium text-slate-600";

  return (
    <div className="surface overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-slate-100 p-4 xl:flex-row xl:items-center">
        <div className="relative min-w-0 flex-1 xl:max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by name or email..."
            className="focus-ring h-10 w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm placeholder:text-slate-400 focus:border-blue-300 focus:bg-white"
          />
        </div>
        <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap">
          {[
            {
              value: position,
              onChange: setPosition,
              options: ["All positions", ...Array.from(new Set(applicants.map((item) => item.position)))],
            },
            {
              value: status,
              onChange: setStatus,
              options: ["All statuses", "New", "Under Review", "Shortlisted", "Interview", "Rejected"],
            },
            {
              value: score,
              onChange: setScore,
              options: ["All scores", "90+", "80-89", "Below 80"],
            },
          ].map((filter) => (
            <label key={filter.options[0]} className="relative min-w-0">
              <select
                value={filter.value}
                onChange={(event) => filter.onChange(event.target.value)}
                className={`${selectClass} w-full`}
              >
                {filter.options.map((option) => <option key={option}>{option}</option>)}
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            </label>
          ))}
          <Button variant="outline" className="w-full px-3 sm:w-auto">
            <SlidersHorizontal className="h-4 w-4" />
            <span className="hidden sm:inline">More filters</span>
          </Button>
        </div>
      </div>

      <div className="divide-y divide-slate-100 md:hidden">
        {filteredApplicants.map((applicant) => (
          <article key={applicant.id} className="p-4">
            <div className="flex items-start gap-3">
              <Avatar name={applicant.name} />
              <div className="min-w-0 flex-1">
                <Link
                  href={`/applicants/${applicant.id}`}
                  className="block truncate text-sm font-bold text-primary"
                >
                  {applicant.name}
                </Link>
                <p className="mt-0.5 truncate text-xs text-slate-400">{applicant.email}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-primary">{applicant.score}</p>
                <p className="text-[9px] font-bold uppercase tracking-wide text-slate-400">AI score</p>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-xs font-semibold text-slate-600">{applicant.position}</p>
                <p className="mt-1 text-[10px] text-slate-400">Applied {applicant.appliedAt}</p>
              </div>
              <StatusBadge status={applicant.status as ApplicantStatus} />
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2 border-t border-slate-100 pt-3">
              <Link
                href={`/applicants/${applicant.id}`}
                className="focus-ring flex h-9 items-center justify-center gap-1.5 rounded-lg bg-blue-50 text-xs font-semibold text-accent"
              >
                <Eye className="h-3.5 w-3.5" /> View
              </Link>
              <button className="focus-ring flex h-9 items-center justify-center gap-1.5 rounded-lg bg-emerald-50 text-xs font-semibold text-emerald-700">
                <Check className="h-3.5 w-3.5" /> Shortlist
              </button>
              <button className="focus-ring flex h-9 items-center justify-center gap-1.5 rounded-lg bg-red-50 text-xs font-semibold text-red-600">
                <X className="h-3.5 w-3.5" /> Reject
              </button>
            </div>
          </article>
        ))}
      </div>

      <div className="hidden overflow-x-auto md:block">
        <table className="w-full min-w-[900px] text-left">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50/60 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              <th className="w-10 px-5 py-3"><input type="checkbox" className="rounded border-slate-300" /></th>
              <th className="px-3 py-3">Candidate</th>
              <th className="px-4 py-3">Position</th>
              <th className="px-4 py-3">AI Score</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Date Applied</th>
              <th className="px-5 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredApplicants.map((applicant) => (
              <tr key={applicant.id} className="table-row text-xs">
                <td className="px-5 py-3.5"><input type="checkbox" className="rounded border-slate-300" /></td>
                <td className="px-3 py-3.5">
                  <Link href={`/applicants/${applicant.id}`} className="flex items-center gap-3">
                    <Avatar name={applicant.name} />
                    <span>
                      <span className="block font-bold text-primary">{applicant.name}</span>
                      <span className="mt-0.5 block text-[11px] text-slate-400">{applicant.email}</span>
                    </span>
                  </Link>
                </td>
                <td className="px-4 py-3.5 font-medium text-slate-600">{applicant.position}</td>
                <td className="px-4 py-3.5">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-primary">{applicant.score}</span>
                    <div className="h-1.5 w-12 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={`h-full rounded-full ${
                          applicant.score >= 90
                            ? "bg-emerald-500"
                            : applicant.score >= 80
                              ? "bg-blue-500"
                              : "bg-amber-500"
                        }`}
                        style={{ width: `${applicant.score}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3.5">
                  <StatusBadge status={applicant.status as ApplicantStatus} />
                </td>
                <td className="px-4 py-3.5 text-slate-500">{applicant.appliedAt}</td>
                <td className="px-5 py-3.5">
                  <div className="flex items-center justify-end gap-1">
                    <Link
                      href={`/applicants/${applicant.id}`}
                      title="View applicant"
                      className="focus-ring rounded-md p-2 text-slate-400 hover:bg-blue-50 hover:text-accent"
                    >
                      <Eye className="h-4 w-4" />
                    </Link>
                    <button title="Shortlist" className="focus-ring rounded-md p-2 text-slate-400 hover:bg-emerald-50 hover:text-emerald-600">
                      <Check className="h-4 w-4" />
                    </button>
                    <button title="Reject" className="focus-ring rounded-md p-2 text-slate-400 hover:bg-red-50 hover:text-red-500">
                      <X className="h-4 w-4" />
                    </button>
                    <button title="More actions" className="focus-ring rounded-md p-2 text-slate-400 hover:bg-slate-100">
                      <MoreHorizontal className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredApplicants.length === 0 ? (
        <div className="grid place-items-center px-5 py-16 text-center">
          <Search className="mb-3 h-8 w-8 text-slate-300" />
          <p className="text-sm font-bold text-primary">No applicants found</p>
          <p className="mt-1 text-xs text-slate-400">Try changing your search or filter criteria.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3 border-t border-slate-100 px-4 py-3 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-5">
          <span>Showing {filteredApplicants.length} of 247 applicants</span>
          <div className="flex gap-1">
            <Button variant="outline" size="sm" disabled>Previous</Button>
            <Button variant="outline" size="sm">Next</Button>
          </div>
        </div>
      )}
    </div>
  );
}
