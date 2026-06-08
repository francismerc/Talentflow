"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  Bot,
  Check,
  ChevronRight,
  LoaderCircle,
  Mail,
  RefreshCw,
  Save,
  Settings2,
  UploadCloud,
  Unplug,
  UserRound,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  disconnectGmail,
  getGmailAuthorizationUrl,
  getGmailConnection,
  processGmailInbox,
  type GmailConnection,
  type GmailProcessResult,
} from "@/services/gmail";
import {
  processStoredResumes,
  type ResumeProcessResult,
} from "@/services/resumes";

const sections = [
  { id: "profile", label: "Recruiter Profile", icon: UserRound },
  { id: "gmail", label: "Gmail Integration", icon: Mail },
  { id: "ai", label: "AI Settings", icon: Bot },
  { id: "preferences", label: "System Preferences", icon: Settings2 },
] as const;

export function SettingsPanels() {
  const [active, setActive] = useState<(typeof sections)[number]["id"]>("profile");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (new URLSearchParams(window.location.search).has("gmail")) {
      setActive("gmail");
    }
  }, []);

  function save() {
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1800);
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[240px_1fr]">
      <nav className="surface self-start p-2">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActive(section.id)}
            className={`focus-ring flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-xs font-semibold transition ${
              active === section.id ? "bg-slate-100 text-primary" : "text-slate-500 hover:bg-slate-50"
            }`}
          >
            <section.icon className={`h-4 w-4 ${active === section.id ? "text-accent" : ""}`} />
            {section.label}
            <ChevronRight className="ml-auto h-3.5 w-3.5 text-slate-300" />
          </button>
        ))}
      </nav>

      <div className="surface overflow-hidden">
        {active === "profile" ? <ProfileSettings /> : null}
        {active === "gmail" ? <GmailSettings /> : null}
        {active === "ai" ? <AISettings /> : null}
        {active === "preferences" ? <PreferenceSettings /> : null}
        <div className="flex items-center justify-end gap-3 border-t border-slate-100 bg-slate-50/60 px-6 py-4">
          {saved ? <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600"><Check className="h-3.5 w-3.5" /> Changes saved</span> : null}
          <Button onClick={save}><Save className="h-4 w-4" /> Save changes</Button>
        </div>
      </div>
    </div>
  );
}

function PanelHeader({ title, description }: { title: string; description: string }) {
  return (
    <div className="border-b border-slate-100 px-6 py-5">
      <h2 className="text-sm font-bold text-primary">{title}</h2>
      <p className="mt-1 text-xs text-slate-400">{description}</p>
    </div>
  );
}

const inputClass = "focus-ring mt-1.5 h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-primary";

function ProfileSettings() {
  return (
    <>
      <PanelHeader title="Recruiter profile" description="Manage your personal information and recruiting identity." />
      <div className="p-6">
        <div className="mb-6 flex items-center gap-4">
          <span className="grid h-16 w-16 place-items-center rounded-full bg-primary text-lg font-bold text-white">AS</span>
          <div><Button variant="outline" size="sm">Change photo</Button><p className="mt-1.5 text-[10px] text-slate-400">JPG or PNG. Maximum 2 MB.</p></div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="First name" defaultValue="Alex" />
          <Field label="Last name" defaultValue="Smith" />
          <Field label="Work email" defaultValue="alex@acme.com" type="email" />
          <Field label="Job title" defaultValue="Recruiting Lead" />
          <Field label="Company" defaultValue="Acme Inc." />
          <Field label="Time zone" defaultValue="Pacific Time (PT)" />
        </div>
      </div>
    </>
  );
}

function GmailSettings() {
  const [connection, setConnection] = useState<GmailConnection | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processResult, setProcessResult] = useState<GmailProcessResult | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [parseResult, setParseResult] = useState<ResumeProcessResult | null>(null);

  const loadConnection = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setConnection(await getGmailConnection());
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Unable to load the Gmail connection.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadConnection();
  }, [loadConnection]);

  async function connect() {
    setIsSubmitting(true);
    setError(null);
    try {
      window.location.assign(await getGmailAuthorizationUrl());
    } catch (connectError) {
      setError(
        connectError instanceof Error
          ? connectError.message
          : "Unable to start Gmail authorization.",
      );
      setIsSubmitting(false);
    }
  }

  async function disconnect() {
    if (!window.confirm("Disconnect this Gmail account from TalentFlow?")) return;

    setIsSubmitting(true);
    setError(null);
    try {
      await disconnectGmail();
      await loadConnection();
    } catch (disconnectError) {
      setError(
        disconnectError instanceof Error
          ? disconnectError.message
          : "Unable to disconnect Gmail.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function processInbox() {
    setIsProcessing(true);
    setError(null);
    setProcessResult(null);
    try {
      const result = await processGmailInbox();
      setProcessResult(result);
      await loadConnection();
    } catch (processError) {
      setError(
        processError instanceof Error
          ? processError.message
          : "Unable to process the Gmail inbox.",
      );
    } finally {
      setIsProcessing(false);
    }
  }

  async function parseStoredResumes() {
    setIsParsing(true);
    setError(null);
    setParseResult(null);
    try {
      setParseResult(await processStoredResumes());
    } catch (parseError) {
      setError(
        parseError instanceof Error
          ? parseError.message
          : "Unable to parse stored resumes.",
      );
    } finally {
      setIsParsing(false);
    }
  }

  return (
    <>
      <PanelHeader title="Gmail integration" description="Connect the inbox TalentFlow monitors for incoming applications." />
      <div className="space-y-5 p-6">
        {isLoading ? (
          <GmailConnectionSkeleton />
        ) : (
          <div
            className={`flex flex-col gap-4 rounded-xl border p-4 sm:flex-row sm:items-center ${
              connection?.connected
                ? "border-emerald-200 bg-emerald-50/50"
                : "border-slate-200 bg-slate-50"
            }`}
          >
            <span className="grid h-10 w-10 place-items-center rounded-lg bg-white text-red-500 shadow-sm"><Mail className="h-5 w-5" /></span>
            <div className="flex-1">
              <p className="text-xs font-bold text-primary">
                {connection?.connected
                  ? connection.gmail_address
                  : "No Gmail account connected"}
              </p>
              <p className={`mt-1 text-[11px] ${connection?.connected ? "text-emerald-700" : "text-slate-500"}`}>
                {connection?.connected
                  ? formatSyncStatus(connection.last_synced_at)
                  : connection?.oauth_configured
                    ? "Connect the recruitment inbox that receives candidate resumes."
                    : "Gmail OAuth must be configured in the backend environment first."}
              </p>
            </div>
            <div className="flex gap-2">
              {connection?.connected ? (
                <>
                  <Button variant="outline" size="sm" onClick={connect} disabled={isSubmitting}>
                    <RefreshCw className="h-3.5 w-3.5" /> Reconnect
                  </Button>
                  <Button variant="outline" size="sm" onClick={disconnect} disabled={isSubmitting}>
                    <Unplug className="h-3.5 w-3.5" /> Disconnect
                  </Button>
                </>
              ) : (
                <Button size="sm" onClick={connect} disabled={isSubmitting || !connection?.oauth_configured}>
                  {isSubmitting ? <LoaderCircle className="h-3.5 w-3.5 animate-spin" /> : <Mail className="h-3.5 w-3.5" />}
                  Connect Gmail
                </Button>
              )}
            </div>
          </div>
        )}
        {connection?.connected ? (
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-bold text-primary">Manual inbox processing</p>
                <p className="mt-1 text-[11px] leading-4 text-slate-500">
                  Scan unread Gmail messages with PDF, DOC, or DOCX attachments and store resumes securely.
                </p>
              </div>
              <Button size="sm" onClick={processInbox} disabled={isProcessing}>
                {isProcessing ? <LoaderCircle className="h-3.5 w-3.5 animate-spin" /> : <UploadCloud className="h-3.5 w-3.5" />}
                {isProcessing ? "Processing..." : "Process inbox"}
              </Button>
            </div>
            {processResult ? (
              <div className="mt-4 grid gap-2 text-[11px] font-semibold text-slate-600 sm:grid-cols-3">
                <ProcessMetric label="Scanned" value={processResult.messages_scanned} />
                <ProcessMetric label="Processed" value={processResult.messages_processed} />
                <ProcessMetric label="Resumes stored" value={processResult.attachments_stored} />
                <ProcessMetric label="Duplicates" value={processResult.duplicates_skipped} />
                <ProcessMetric label="Unsupported" value={processResult.unsupported_skipped} />
                <ProcessMetric label="Errors" value={processResult.errors} tone={processResult.errors ? "danger" : "default"} />
              </div>
            ) : null}
          </div>
        ) : null}
        {connection?.connected ? (
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-bold text-primary">Stored resume parsing</p>
                <p className="mt-1 text-[11px] leading-4 text-slate-500">
                  Extract candidate details, match the email subject to an active job, and create applicant records.
                </p>
              </div>
              <Button size="sm" onClick={parseStoredResumes} disabled={isParsing}>
                {isParsing ? <LoaderCircle className="h-3.5 w-3.5 animate-spin" /> : <UploadCloud className="h-3.5 w-3.5" />}
                {isParsing ? "Parsing..." : "Parse stored resumes"}
              </Button>
            </div>
            {parseResult ? (
              <div className="mt-4 grid gap-2 text-[11px] font-semibold text-slate-600 sm:grid-cols-4">
                <ProcessMetric label="Scanned" value={parseResult.attachments_scanned} />
                <ProcessMetric label="Applicants created" value={parseResult.applicants_created} />
                <ProcessMetric label="Needs review" value={parseResult.needs_review} tone={parseResult.needs_review ? "warning" : "default"} />
                <ProcessMetric label="Failed" value={parseResult.failed} tone={parseResult.failed ? "danger" : "default"} />
              </div>
            ) : null}
          </div>
        ) : null}
        {error ? (
          <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-700">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <div className="flex-1">
              <p className="font-semibold">Gmail connection unavailable</p>
              <p className="mt-1 leading-5">{error}</p>
            </div>
            <Button variant="outline" size="sm" onClick={() => void loadConnection()}>
              Retry
            </Button>
          </div>
        ) : null}
        <Field
          label="Current scan scope"
          defaultValue="Unread inbox messages with PDF, DOC, or DOCX attachments"
          readOnly
        />
        <ToggleRow
          title="Process new attachments automatically"
          description="Available after the manual inbox workflow is validated."
          disabled
        />
        <ToggleRow
          title="Send acknowledgment emails"
          description="Will be enabled in the automated email phase."
          disabled
        />
        <ToggleRow
          title="Include email body in analysis"
          description="Will be enabled when resume parsing and AI analysis are connected."
          disabled
        />
      </div>
    </>
  );
}

function GmailConnectionSkeleton() {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-slate-200 p-4" role="status">
      <Skeleton className="h-10 w-10 shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-3 w-44" />
        <Skeleton className="h-2.5 w-64 max-w-full" />
      </div>
      <Skeleton className="hidden h-8 w-28 sm:block" />
      <span className="sr-only">Loading Gmail connection</span>
    </div>
  );
}

function formatSyncStatus(lastSyncedAt: string | null): string {
  if (!lastSyncedAt) return "Connected. Inbox processing has not run yet.";
  return `Connected and syncing · Last checked ${new Date(lastSyncedAt).toLocaleString()}`;
}

function ProcessMetric({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: number;
  tone?: "default" | "warning" | "danger";
}) {
  const toneClass = {
    default: "border-slate-100 bg-slate-50",
    warning: "border-amber-200 bg-amber-50 text-amber-700",
    danger: "border-red-200 bg-red-50 text-red-700",
  }[tone];
  return (
    <div className={`rounded-lg border px-3 py-2 ${toneClass}`}>
      <span className="block text-[10px] uppercase tracking-wide text-slate-400">{label}</span>
      <span className="mt-1 block text-sm font-bold">{value}</span>
    </div>
  );
}

function AISettings() {
  return (
    <>
      <PanelHeader title="AI settings" description="Configure how TalentFlow analyzes and recommends candidates." />
      <div className="space-y-5 p-6">
        <label className="block text-xs font-semibold text-slate-600">AI model<select className={inputClass}><option>Gemini 2.5 Pro</option><option>Gemini 2.5 Flash</option></select></label>
        <label className="block text-xs font-semibold text-slate-600">Default scoring emphasis<select className={inputClass}><option>Balanced skills and experience</option><option>Skills weighted</option><option>Experience weighted</option></select></label>
        <ToggleRow title="Show score explanations" description="Display the evidence and reasoning behind every AI score." checked />
        <ToggleRow title="Flag uncertain recommendations" description="Clearly mark outputs that need additional recruiter review." checked />
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-800">AI recommendations are advisory only. TalentFlow never changes applicant records or hiring status without recruiter action.</div>
      </div>
    </>
  );
}

function PreferenceSettings() {
  return (
    <>
      <PanelHeader title="System preferences" description="Choose your default workspace behavior and notifications." />
      <div className="space-y-5 p-6">
        <label className="block text-xs font-semibold text-slate-600">Default applicants view<select className={inputClass}><option>All applicants</option><option>New applicants</option><option>Under review</option></select></label>
        <ToggleRow title="Daily pipeline summary" description="Receive a concise email summary every weekday morning." checked />
        <ToggleRow title="New high-score alerts" description="Notify me when a candidate scores 90 or above." checked />
        <ToggleRow title="Compact table density" description="Show more rows at once in applicant and job tables." />
      </div>
    </>
  );
}

function Field({ label, defaultValue, type = "text", readOnly = false }: { label: string; defaultValue: string; type?: string; readOnly?: boolean }) {
  return <label className="block text-xs font-semibold text-slate-600">{label}<input type={type} defaultValue={defaultValue} readOnly={readOnly} className={`${inputClass} ${readOnly ? "bg-slate-50 text-slate-500" : ""}`} /></label>;
}

function ToggleRow({ title, description, checked = false, disabled = false }: { title: string; description: string; checked?: boolean; disabled?: boolean }) {
  return (
    <label className={`flex items-center justify-between gap-5 ${disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}>
      <span><span className="block text-xs font-semibold text-slate-700">{title}</span><span className="mt-1 block text-[11px] leading-4 text-slate-400">{description}</span></span>
      <span className="relative shrink-0">
        <input type="checkbox" defaultChecked={checked} disabled={disabled} className="peer sr-only" />
        <span className="block h-6 w-11 rounded-full bg-slate-200 transition peer-checked:bg-accent" />
        <span className="absolute left-1 top-1 h-4 w-4 rounded-full bg-white shadow-sm transition peer-checked:translate-x-5" />
      </span>
    </label>
  );
}
