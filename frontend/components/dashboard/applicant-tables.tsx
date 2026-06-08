import { ArrowUpRight, MoreHorizontal } from "lucide-react";
import Link from "next/link";
import { Avatar } from "@/components/ui/avatar";
import { StatusBadge } from "@/components/ui/badge";
import { ScoreRing } from "@/components/ui/score-ring";
import type { Applicant } from "@/types";

export function RecentApplicantsTable({ applicants }: { applicants: Applicant[] }) {
  return (
    <>
      <div className="divide-y divide-slate-100 sm:hidden">
        {applicants.slice(0, 5).map((applicant) => (
          <Link
            key={applicant.id}
            href={`/applicants/${applicant.id}`}
            className="flex items-center gap-3 px-4 py-3.5 hover:bg-slate-50"
          >
            <Avatar name={applicant.name} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-bold text-primary">{applicant.name}</p>
              <p className="mt-0.5 truncate text-[11px] text-slate-400">{applicant.position}</p>
            </div>
            <div className="text-right">
              <p className="text-xs font-bold text-primary">{applicant.score}</p>
              <p className="mt-1 text-[10px] text-slate-400">{applicant.appliedAt}</p>
            </div>
          </Link>
        ))}
      </div>
      <div className="hidden overflow-x-auto sm:block">
        <table className="w-full min-w-[620px] text-left">
        <thead>
          <tr className="border-b border-slate-100 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            <th className="px-5 py-3">Candidate</th>
            <th className="px-4 py-3">Role</th>
            <th className="px-4 py-3">Score</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-5 py-3 text-right">Applied</th>
          </tr>
        </thead>
        <tbody>
          {applicants.slice(0, 5).map((applicant) => (
            <tr key={applicant.id} className="table-row text-xs">
              <td className="px-5 py-3">
                <Link href={`/applicants/${applicant.id}`} className="flex items-center gap-3">
                  <Avatar name={applicant.name} />
                  <span>
                    <span className="block font-semibold text-primary">{applicant.name}</span>
                    <span className="mt-0.5 block text-[11px] text-slate-400">{applicant.email}</span>
                  </span>
                </Link>
              </td>
              <td className="px-4 py-3 font-medium text-slate-600">{applicant.position}</td>
              <td className="px-4 py-3">
                <span className="font-bold text-primary">{applicant.score}</span>
                <span className="text-slate-400">/100</span>
              </td>
              <td className="px-4 py-3"><StatusBadge status={applicant.status} /></td>
              <td className="px-5 py-3 text-right text-slate-500">{applicant.appliedAt}</td>
            </tr>
          ))}
        </tbody>
        </table>
      </div>
    </>
  );
}

export function TopCandidatesTable({ applicants }: { applicants: Applicant[] }) {
  return (
    <div className="divide-y divide-slate-100">
      {applicants.slice(0, 4).map((applicant, index) => (
        <div key={applicant.id} className="flex items-center gap-3 px-5 py-3.5 hover:bg-slate-50/70">
          <span className="w-4 text-center text-[11px] font-bold text-slate-300">{index + 1}</span>
          <Avatar name={applicant.name} />
          <div className="min-w-0 flex-1">
            <Link
              href={`/applicants/${applicant.id}`}
              className="truncate text-xs font-bold text-primary hover:text-accent"
            >
              {applicant.name}
            </Link>
            <p className="truncate text-[11px] text-slate-400">{applicant.position}</p>
          </div>
          <ScoreRing score={applicant.score} size="sm" />
          <button className="focus-ring rounded-md p-1 text-slate-400 hover:bg-slate-100">
            <MoreHorizontal className="h-4 w-4" />
          </button>
        </div>
      ))}
      <Link
        href="/applicants"
        className="flex items-center justify-center gap-1.5 px-5 py-3 text-xs font-semibold text-accent hover:bg-blue-50/50"
      >
        View all candidates <ArrowUpRight className="h-3.5 w-3.5" />
      </Link>
    </div>
  );
}
