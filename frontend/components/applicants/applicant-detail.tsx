"use client";

import { useState } from "react";
import {
  Check,
  CheckCircle2,
  Circle,
  Download,
  ExternalLink,
  FileText,
  LoaderCircle,
  Mail,
  MapPin,
  Phone,
  Sparkles,
  X,
} from "lucide-react";
import type { Applicant } from "@/types";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { ScoreRing } from "@/components/ui/score-ring";
import { StatusBadge } from "@/components/ui/badge";
import { ConfirmDialog } from "@/components/ui/modal";
import type { CandidateEmailType } from "@/services/applicants";

export function ApplicantDetail({
  applicant,
  actionLoading,
  actionError,
  analysisLoading,
  analysisError,
  onStatusChange,
  onSendEmail,
  onGenerateAnalysis,
}: {
  applicant: Applicant;
  actionLoading?: boolean;
  actionError?: string;
  analysisLoading?: boolean;
  analysisError?: string;
  onStatusChange?: (status: "shortlisted" | "rejected") => void;
  onSendEmail?: (emailType: CandidateEmailType) => void;
  onGenerateAnalysis?: () => void;
}) {
  const [tab, setTab] = useState<"profile" | "resume">("profile");
  const [pendingEmail, setPendingEmail] = useState<CandidateEmailType | null>(
    null,
  );
  const timeline = applicant.timeline ?? [];

  return (
    <div className="space-y-5">
      <section className="surface flex flex-col gap-5 p-4 sm:p-5 lg:flex-row lg:items-center">
        <Avatar name={applicant.name} className="h-16 w-16 text-lg" />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-primary">{applicant.name}</h1>
            <StatusBadge status={applicant.status} />
          </div>
          <p className="mt-1 text-sm font-medium text-slate-600">{applicant.position}</p>
          <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
            <span className="flex items-center gap-1.5"><Mail className="h-3.5 w-3.5" />{applicant.email}</span>
            <span className="flex items-center gap-1.5"><Phone className="h-3.5 w-3.5" />{applicant.phone}</span>
            <span className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5" />{applicant.location}</span>
          </div>
        </div>
        <div className="grid w-full grid-cols-3 gap-2 lg:flex lg:w-auto lg:flex-wrap">
          <Button
            variant="outline"
            className="px-2 sm:px-4"
            disabled={actionLoading}
            onClick={() => setPendingEmail("acknowledgment")}
          >
            <Mail className="h-4 w-4" /> <span className="hidden sm:inline">Email</span>
          </Button>
          <Button
            disabled={actionLoading || !["New", "Under Review", "Shortlisted", "Interview"].includes(applicant.status)}
            onClick={() => setPendingEmail("rejected")}
            variant="danger"
            className="px-2 sm:px-4"
          >
            <X className="h-4 w-4" /> <span className="hidden sm:inline">Reject</span>
          </Button>
          <Button
            disabled={actionLoading || !["New", "Under Review"].includes(applicant.status)}
            onClick={() => setPendingEmail("shortlisted")}
            className="px-2 sm:px-4"
          >
            <Check className="h-4 w-4" /> <span className="hidden sm:inline">Shortlist</span>
          </Button>
        </div>
      </section>
      {actionError ? (
        <p className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-xs text-red-700">
          {actionError}
        </p>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[1.45fr_1fr]">
        <div className="space-y-5">
          <section className="surface overflow-hidden">
            <div className="flex border-b border-slate-100 px-5">
              {(["profile", "resume"] as const).map((item) => (
                <button
                  key={item}
                  onClick={() => setTab(item)}
                  className={`border-b-2 px-1 py-4 text-xs font-bold capitalize transition ${
                    tab === item ? "border-accent text-accent" : "border-transparent text-slate-400"
                  } ${item === "resume" ? "ml-6" : ""}`}
                >
                  {item === "profile" ? "Candidate profile" : "Resume viewer"}
                </button>
              ))}
            </div>
            {tab === "profile" ? (
              <div className="p-4 sm:p-5">
                <h2 className="text-sm font-bold text-primary">Candidate information</h2>
                <div className="mt-4 grid gap-5 sm:grid-cols-2">
                  {[
                    ["Full name", applicant.name],
                    ["Email address", applicant.email],
                    ["Phone number", applicant.phone],
                    ["Education", applicant.education],
                    ["Professional experience", applicant.experience],
                    ["Location", applicant.location],
                  ].map(([label, value]) => (
                    <div key={label}>
                      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{label}</p>
                      <p className="mt-1.5 text-xs font-medium leading-5 text-slate-700">{value}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-6 border-t border-slate-100 pt-5">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Professional summary</p>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{applicant.summary}</p>
                </div>
              </div>
            ) : (
              <div className="p-3 sm:p-5">
                <div className="mb-3 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                    <FileText className="h-4 w-4 text-accent" /> {applicant.resumeFileName ?? "No resume uploaded"}
                  </div>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost"><Download className="h-3.5 w-3.5" /></Button>
                    <Button size="sm" variant="ghost"><ExternalLink className="h-3.5 w-3.5" /></Button>
                  </div>
                </div>
                <div className="min-h-[500px] overflow-x-auto rounded-lg border border-slate-200 bg-slate-100 p-2 sm:min-h-[620px] sm:p-5">
                  <div className="mx-auto min-h-[480px] min-w-[300px] max-w-lg bg-white px-5 py-6 shadow-card sm:min-h-[580px] sm:px-10 sm:py-8">
                    <h3 className="text-xl font-bold text-primary">{applicant.name}</h3>
                    <p className="mt-1 text-xs text-slate-500">{applicant.position} · {applicant.location}</p>
                    <div className="my-5 h-px bg-slate-200" />
                    <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Experience</p>
                    <p className="mt-3 text-xs leading-6 text-slate-500">{applicant.summary}</p>
                    <div className="mt-8 space-y-3">
                      {[92, 100, 82, 96, 72, 88, 62].map((width, index) => (
                        <div key={index} className="h-1.5 rounded-full bg-slate-100" style={{ width: `${width}%` }} />
                      ))}
                    </div>
                    <p className="mt-9 text-[10px] font-bold uppercase tracking-widest text-slate-500">Education</p>
                    <p className="mt-3 text-xs text-slate-500">{applicant.education}</p>
                  </div>
                </div>
              </div>
            )}
          </section>

          <section className="surface p-5">
            <h2 className="text-sm font-bold text-primary">Skill match</h2>
            <p className="mt-1 text-xs text-slate-400">Skills identified from the resume against role requirements.</p>
            <div className="mt-5 grid gap-5 md:grid-cols-2">
              <div>
                <p className="mb-3 flex items-center gap-1.5 text-xs font-bold text-emerald-700">
                  <CheckCircle2 className="h-4 w-4" /> Matched skills
                </p>
                <div className="flex flex-wrap gap-2">
                  {applicant.matchedSkills.map((skill) => (
                    <span key={skill} className="rounded-lg border border-emerald-100 bg-emerald-50 px-2.5 py-1.5 text-xs font-medium text-emerald-700">{skill}</span>
                  ))}
                  {!applicant.matchedSkills.length ? <span className="text-xs text-slate-400">AI analysis pending</span> : null}
                </div>
              </div>
              <div>
                <p className="mb-3 flex items-center gap-1.5 text-xs font-bold text-amber-700">
                  <Circle className="h-4 w-4" /> Missing skills
                </p>
                <div className="flex flex-wrap gap-2">
                  {applicant.missingSkills.map((skill) => (
                    <span key={skill} className="rounded-lg border border-amber-100 bg-amber-50 px-2.5 py-1.5 text-xs font-medium text-amber-700">{skill}</span>
                  ))}
                  {!applicant.missingSkills.length ? <span className="text-xs text-slate-400">AI analysis pending</span> : null}
                </div>
              </div>
            </div>
          </section>

          <section className="surface p-5">
            <h2 className="text-sm font-bold text-primary">Email history</h2>
            <p className="mt-1 text-xs text-slate-400">
              Candidate messages sent through the connected recruitment Gmail.
            </p>
            <div className="mt-4 space-y-3">
              {applicant.emails.map((email) => (
                <div
                  key={email.id}
                  className="rounded-xl border border-slate-100 bg-slate-50/70 p-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-xs font-bold text-primary">{email.subject}</p>
                    <span
                      className={`rounded-full px-2 py-1 text-[9px] font-bold uppercase ${
                        email.status === "sent"
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {email.status}
                    </span>
                  </div>
                  <p className="mt-1 text-[10px] text-slate-400">
                    {email.recipient} · {email.sentAt}
                  </p>
                  {email.error ? (
                    <p className="mt-2 text-[10px] leading-4 text-red-600">
                      {email.error}
                    </p>
                  ) : null}
                </div>
              ))}
              {!applicant.emails.length ? (
                <p className="text-xs text-slate-400">No candidate emails sent yet.</p>
              ) : null}
            </div>
          </section>
        </div>

        <div className="space-y-5">
          <section className="surface overflow-hidden">
            <div className="border-b border-slate-100 bg-gradient-to-br from-blue-50 to-white p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2 text-xs font-bold text-accent">
                  <Sparkles className="h-4 w-4" /> TalentFlow AI analysis
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={analysisLoading}
                  onClick={onGenerateAnalysis}
                >
                  {analysisLoading ? (
                    <LoaderCircle className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Sparkles className="h-3.5 w-3.5" />
                  )}
                  {analysisLoading
                    ? "Analyzing"
                    : applicant.hasAnalysis
                      ? "Reanalyze"
                      : "Generate analysis"}
                </Button>
              </div>
              <div className="mt-5 flex items-center gap-5">
                <ScoreRing score={applicant.score} size="lg" />
                <div>
                  <p className="text-sm font-bold text-primary">
                    {applicant.hasAnalysis
                      ? "Job-fit analysis ready"
                      : "Analysis pending"}
                  </p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    {applicant.hasAnalysis
                      ? "Review the evidence below before making a hiring decision."
                      : "Generate an evidence-based comparison with the job requirements."}
                  </p>
                </div>
              </div>
            </div>
            <div className="space-y-5 p-5">
              {analysisError ? (
                <p className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-xs text-red-700">
                  {analysisError}
                </p>
              ) : null}
              <div>
                <p className="text-xs font-bold text-primary">Strengths</p>
                <ul className="mt-2 space-y-2">
                  {applicant.strengths.map((strength) => (
                    <li key={strength} className="flex gap-2 text-xs leading-5 text-slate-600">
                      <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" /> {strength}
                    </li>
                  ))}
                  {!applicant.strengths.length ? (
                    <li className="text-xs leading-5 text-slate-400">
                      No analysis has been generated yet.
                    </li>
                  ) : null}
                </ul>
              </div>
              <div>
                <p className="text-xs font-bold text-primary">Areas to explore</p>
                <ul className="mt-2 space-y-2">
                  {applicant.weaknesses.map((weakness) => (
                    <li key={weakness} className="flex gap-2 text-xs leading-5 text-slate-600">
                      <Circle className="mt-1 h-2.5 w-2.5 shrink-0 text-amber-500" /> {weakness}
                    </li>
                  ))}
                  {!applicant.weaknesses.length ? (
                    <li className="text-xs leading-5 text-slate-400">
                      No areas have been identified yet.
                    </li>
                  ) : null}
                </ul>
              </div>
              <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-4">
                <p className="text-xs font-bold text-primary">Recommendation</p>
                <p className="mt-2 text-xs leading-5 text-slate-600">{applicant.recommendation}</p>
              </div>
              <p className="text-[10px] leading-4 text-slate-400">
                AI output is advisory. Recruiters must review the underlying resume
                evidence and make the final decision.
              </p>
            </div>
          </section>

          <section className="surface p-5">
            <h2 className="text-sm font-bold text-primary">Candidate timeline</h2>
            <div className="mt-5">
              {timeline.map((item, index) => (
                <div key={item.title} className="relative flex gap-3 pb-6 last:pb-0">
                  {index < timeline.length - 1 ? (
                    <div className="absolute left-[7px] top-4 h-full w-px bg-slate-200" />
                  ) : null}
                  <span className="relative z-10 mt-0.5 h-4 w-4 shrink-0 rounded-full border-4 border-white bg-accent ring-1 ring-blue-200" />
                  <div>
                    <p className="text-xs font-bold text-primary">{item.title}</p>
                    <p className="mt-1 text-[11px] leading-4 text-slate-500">{item.detail}</p>
                    <p className="mt-1.5 text-[10px] font-medium text-slate-400">{item.time}</p>
                  </div>
                </div>
              ))}
              {!timeline.length ? <p className="text-xs text-slate-400">No timeline events yet.</p> : null}
            </div>
          </section>
        </div>
      </div>
      <ConfirmDialog
        open={pendingEmail !== null}
        title={emailDialogCopy(pendingEmail).title}
        description={emailDialogCopy(pendingEmail).description}
        confirmLabel={emailDialogCopy(pendingEmail).confirmLabel}
        loadingLabel="Sending..."
        loading={actionLoading}
        tone={pendingEmail === "rejected" ? "danger" : "default"}
        onCancel={() => {
          if (!actionLoading) setPendingEmail(null);
        }}
        onConfirm={() => {
          if (!pendingEmail) return;
          const emailType = pendingEmail;
          setPendingEmail(null);
          if (emailType === "shortlisted" || emailType === "rejected") {
            onStatusChange?.(emailType);
          } else {
            onSendEmail?.(emailType);
          }
        }}
      />
    </div>
  );
}

function emailDialogCopy(emailType: CandidateEmailType | null) {
  if (emailType === "shortlisted") {
    return {
      title: "Shortlist candidate and send email?",
      description:
        "The applicant status will change to Shortlisted, then TalentFlow will send the shortlist email through your connected Gmail.",
      confirmLabel: "Shortlist & send",
    };
  }
  if (emailType === "rejected") {
    return {
      title: "Reject candidate and send email?",
      description:
        "The applicant status will change to Rejected before TalentFlow sends the rejection email. This action should be reviewed carefully.",
      confirmLabel: "Reject & send",
    };
  }
  return {
    title: "Send acknowledgment email?",
    description:
      "TalentFlow will confirm that the candidate's application was received. This does not change applicant status.",
    confirmLabel: "Send email",
  };
}
