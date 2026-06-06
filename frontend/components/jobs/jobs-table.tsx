"use client";

import { useEffect, useState } from "react";
import { BriefcaseBusiness, Edit3, Eye, MoreHorizontal, Search, Trash2, X } from "lucide-react";
import Link from "next/link";
import { jobs } from "@/lib/mock-data";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/badge";

export function JobsTable({ createRequest = 0 }: { createRequest?: number }) {
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    if (createRequest > 0) setShowCreate(true);
  }, [createRequest]);

  return (
    <>
      <div className="surface overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative max-w-sm flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input placeholder="Search jobs..." className="focus-ring h-10 w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm" />
          </div>
          <p className="text-xs font-medium text-slate-400">{jobs.length} open and draft positions</p>
        </div>
        <div className="divide-y divide-slate-100 md:hidden">
          {jobs.map((job) => (
            <article key={job.id} className="p-4">
              <div className="flex items-start gap-3">
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-slate-100 text-slate-600">
                  <BriefcaseBusiness className="h-4 w-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <Link href={`/jobs/${job.id}`} className="block truncate text-sm font-bold text-primary">
                    {job.title}
                  </Link>
                  <p className="mt-1 truncate text-[11px] text-slate-400">
                    {job.department} · {job.location}
                  </p>
                </div>
                <StatusBadge status={job.status} />
              </div>
              <div className="mt-4 flex flex-wrap gap-1.5">
                {job.skills.slice(0, 3).map((skill) => (
                  <span key={skill} className="rounded-md bg-slate-100 px-2 py-1 text-[10px] font-medium text-slate-600">
                    {skill}
                  </span>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                <div>
                  <p className="text-xs font-bold text-primary">{job.applicants} applicants</p>
                  <p className="mt-0.5 text-[10px] text-slate-400">Created {job.createdAt}</p>
                </div>
                <div className="flex gap-1">
                  <Link href={`/jobs/${job.id}`} className="focus-ring rounded-lg bg-blue-50 p-2 text-accent">
                    <Eye className="h-4 w-4" />
                  </Link>
                  <button className="focus-ring rounded-lg bg-slate-100 p-2 text-slate-600">
                    <Edit3 className="h-4 w-4" />
                  </button>
                  <button className="focus-ring rounded-lg bg-red-50 p-2 text-red-500">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>

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
                      <span className="grid h-9 w-9 place-items-center rounded-lg bg-slate-100 text-slate-600">
                        <BriefcaseBusiness className="h-4 w-4" />
                      </span>
                      <span>
                        <span className="block font-bold text-primary">{job.title}</span>
                        <span className="mt-0.5 block text-[11px] text-slate-400">{job.department} · {job.location}</span>
                      </span>
                    </Link>
                  </td>
                  <td className="max-w-[300px] px-4 py-4">
                    <div className="flex flex-wrap gap-1">
                      {job.skills.slice(0, 3).map((skill) => (
                        <span key={skill} className="rounded-md bg-slate-100 px-2 py-1 text-[10px] font-medium text-slate-600">{skill}</span>
                      ))}
                      {job.skills.length > 3 ? <span className="px-1 py-1 text-[10px] text-slate-400">+{job.skills.length - 3}</span> : null}
                    </div>
                  </td>
                  <td className="px-4 py-4 font-bold text-primary">{job.applicants}</td>
                  <td className="px-4 py-4 text-slate-500">{job.createdAt}</td>
                  <td className="px-4 py-4"><StatusBadge status={job.status} /></td>
                  <td className="px-5 py-4">
                    <div className="flex justify-end gap-1">
                      <Link href={`/jobs/${job.id}`} className="focus-ring rounded-md p-2 text-slate-400 hover:bg-blue-50 hover:text-accent"><Eye className="h-4 w-4" /></Link>
                      <button className="focus-ring rounded-md p-2 text-slate-400 hover:bg-slate-100 hover:text-primary"><Edit3 className="h-4 w-4" /></button>
                      <button className="focus-ring rounded-md p-2 text-slate-400 hover:bg-red-50 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
                      <button className="focus-ring rounded-md p-2 text-slate-400 hover:bg-slate-100"><MoreHorizontal className="h-4 w-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showCreate ? (
        <div className="fixed inset-0 z-[70] grid place-items-center bg-slate-950/35 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-floating">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <div>
                <h2 className="text-sm font-bold text-primary">Create a new job</h2>
                <p className="mt-0.5 text-xs text-slate-400">Add the core details for this opening.</p>
              </div>
              <button onClick={() => setShowCreate(false)} className="focus-ring rounded-lg p-2 text-slate-400 hover:bg-slate-100"><X className="h-4 w-4" /></button>
            </div>
            <form className="space-y-4 p-5" onSubmit={(event) => { event.preventDefault(); setShowCreate(false); }}>
              <label className="block text-xs font-semibold text-slate-600">Job title<input required className="focus-ring mt-1.5 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm" placeholder="e.g. Senior Software Engineer" /></label>
              <label className="block text-xs font-semibold text-slate-600">Description<textarea required className="focus-ring mt-1.5 min-h-24 w-full rounded-lg border border-slate-200 p-3 text-sm" placeholder="Describe the role and responsibilities..." /></label>
              <label className="block text-xs font-semibold text-slate-600">Required skills<input required className="focus-ring mt-1.5 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm" placeholder="React, TypeScript, Next.js" /></label>
              <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
                <Button type="button" variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
                <Button type="submit">Create job</Button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </>
  );
}
