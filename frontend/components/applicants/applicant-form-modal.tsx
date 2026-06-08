"use client";

import { useEffect, useState, type FormEvent } from "react";
import { createApplicant } from "@/services/applicants";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import type { Applicant, Job } from "@/types";

const inputClass =
  "focus-ring mt-1.5 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm";

export function ApplicantFormModal({
  open,
  jobs,
  onClose,
  onSaved,
}: {
  open: boolean;
  jobs: Job[];
  onClose: () => void;
  onSaved: (applicant: Applicant) => void;
}) {
  const [jobId, setJobId] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [location, setLocation] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setJobId(jobs[0]?.id ?? "");
    setFullName("");
    setEmail("");
    setPhone("");
    setLocation("");
    setError("");
  }, [jobs, open]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const applicant = await createApplicant({
        job_id: jobId,
        full_name: fullName,
        email,
        phone: phone || null,
        location: location || null,
      });
      onSaved(applicant);
      onClose();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Applicant could not be created.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      open={open}
      title="Add applicant"
      description="Manually add a candidate to an active recruitment pipeline."
      onClose={onClose}
    >
      <form className="space-y-4 p-5" onSubmit={handleSubmit}>
        <label className="block text-xs font-semibold text-slate-600">
          Position
          <select required value={jobId} onChange={(event) => setJobId(event.target.value)} className={inputClass}>
            {jobs.map((job) => <option key={job.id} value={job.id}>{job.title}</option>)}
          </select>
        </label>
        <label className="block text-xs font-semibold text-slate-600">
          Full name
          <input required value={fullName} onChange={(event) => setFullName(event.target.value)} className={inputClass} />
        </label>
        <label className="block text-xs font-semibold text-slate-600">
          Email address
          <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className={inputClass} />
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block text-xs font-semibold text-slate-600">
            Phone
            <input value={phone} onChange={(event) => setPhone(event.target.value)} className={inputClass} />
          </label>
          <label className="block text-xs font-semibold text-slate-600">
            Location
            <input value={location} onChange={(event) => setLocation(event.target.value)} className={inputClass} />
          </label>
        </div>
        {!jobs.length ? (
          <p className="rounded-lg border border-amber-100 bg-amber-50 px-3 py-2.5 text-xs text-amber-700">
            Create an active job before adding an applicant.
          </p>
        ) : null}
        {error ? <p className="rounded-lg border border-red-100 bg-red-50 px-3 py-2.5 text-xs text-red-700">{error}</p> : null}
        <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={submitting || !jobs.length}>{submitting ? "Adding..." : "Add applicant"}</Button>
        </div>
      </form>
    </Modal>
  );
}
