"use client";

import { useEffect, useState, type FormEvent } from "react";
import { createJob, updateJob, type JobMutationInput } from "@/services/jobs";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import type { Job } from "@/types";

const inputClass =
  "focus-ring mt-1.5 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm";

export function JobFormModal({
  open,
  job,
  onClose,
  onSaved,
}: {
  open: boolean;
  job?: Job | null;
  onClose: () => void;
  onSaved: (job: Job) => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [skills, setSkills] = useState("");
  const [location, setLocation] = useState("");
  const [employmentType, setEmploymentType] = useState("full_time");
  const [status, setStatus] = useState("draft");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setTitle(job?.title ?? "");
    setDescription(job?.description ?? "");
    setSkills(job?.skills.join(", ") ?? "");
    setLocation(job?.location === "Location not specified" ? "" : job?.location ?? "");
    setEmploymentType(toApiValue(job?.type ?? "Full Time"));
    setStatus(job?.status.toLowerCase() ?? "draft");
    setError("");
  }, [job, open]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    const payload: JobMutationInput = {
      title,
      description,
      required_skills: skills.split(",").map((skill) => skill.trim()).filter(Boolean),
      location: location || null,
      employment_type: employmentType,
      status,
    };
    try {
      const savedJob = job
        ? await updateJob(job.id, payload)
        : await createJob(payload);
      onSaved(savedJob);
      onClose();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Job could not be saved.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      open={open}
      title={job ? "Edit job" : "Create a new job"}
      description="Keep the role requirements clear so candidate matching remains explainable."
      onClose={onClose}
    >
      <form className="space-y-4 p-5" onSubmit={handleSubmit}>
        <label className="block text-xs font-semibold text-slate-600">
          Job title
          <input required value={title} onChange={(event) => setTitle(event.target.value)} className={inputClass} />
        </label>
        <label className="block text-xs font-semibold text-slate-600">
          Description
          <textarea required value={description} onChange={(event) => setDescription(event.target.value)} className="focus-ring mt-1.5 min-h-28 w-full rounded-lg border border-slate-200 p-3 text-sm" />
        </label>
        <label className="block text-xs font-semibold text-slate-600">
          Required skills
          <input required value={skills} onChange={(event) => setSkills(event.target.value)} className={inputClass} placeholder="React, TypeScript, Next.js" />
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block text-xs font-semibold text-slate-600">
            Location
            <input value={location} onChange={(event) => setLocation(event.target.value)} className={inputClass} placeholder="Remote" />
          </label>
          <label className="block text-xs font-semibold text-slate-600">
            Employment type
            <select value={employmentType} onChange={(event) => setEmploymentType(event.target.value)} className={inputClass}>
              <option value="full_time">Full time</option>
              <option value="part_time">Part time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
              <option value="temporary">Temporary</option>
            </select>
          </label>
        </div>
        <label className="block text-xs font-semibold text-slate-600">
          Status
          <select value={status} onChange={(event) => setStatus(event.target.value)} className={inputClass}>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
          </select>
        </label>
        {error ? <p className="rounded-lg border border-red-100 bg-red-50 px-3 py-2.5 text-xs text-red-700">{error}</p> : null}
        <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={submitting}>{submitting ? "Saving..." : job ? "Save changes" : "Create job"}</Button>
        </div>
      </form>
    </Modal>
  );
}

function toApiValue(value: string): string {
  return value.toLowerCase().replaceAll(" ", "_");
}
