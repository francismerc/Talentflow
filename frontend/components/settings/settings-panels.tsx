"use client";

import { useState } from "react";
import { Bot, Check, ChevronRight, Mail, Save, Settings2, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";

const sections = [
  { id: "profile", label: "Recruiter Profile", icon: UserRound },
  { id: "gmail", label: "Gmail Integration", icon: Mail },
  { id: "ai", label: "AI Settings", icon: Bot },
  { id: "preferences", label: "System Preferences", icon: Settings2 },
] as const;

export function SettingsPanels() {
  const [active, setActive] = useState<(typeof sections)[number]["id"]>("profile");
  const [saved, setSaved] = useState(false);

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
  return (
    <>
      <PanelHeader title="Gmail integration" description="Connect the inbox TalentFlow monitors for incoming applications." />
      <div className="space-y-5 p-6">
        <div className="flex flex-col gap-4 rounded-xl border border-emerald-200 bg-emerald-50/50 p-4 sm:flex-row sm:items-center">
          <span className="grid h-10 w-10 place-items-center rounded-lg bg-white text-red-500 shadow-sm"><Mail className="h-5 w-5" /></span>
          <div className="flex-1"><p className="text-xs font-bold text-primary">recruiting@acme.com</p><p className="mt-1 text-[11px] text-emerald-700">Connected and syncing · Last checked 2 minutes ago</p></div>
          <Button variant="outline" size="sm">Reconnect</Button>
        </div>
        <Field label="Monitored label" defaultValue="Applications" />
        <ToggleRow title="Process new attachments automatically" description="Analyze supported resume files as soon as they arrive." checked />
        <ToggleRow title="Send acknowledgment emails" description="Confirm receipt of every successfully processed application." checked />
        <ToggleRow title="Include email body in analysis" description="Use candidate notes from the email as additional context." />
      </div>
    </>
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

function Field({ label, defaultValue, type = "text" }: { label: string; defaultValue: string; type?: string }) {
  return <label className="block text-xs font-semibold text-slate-600">{label}<input type={type} defaultValue={defaultValue} className={inputClass} /></label>;
}

function ToggleRow({ title, description, checked = false }: { title: string; description: string; checked?: boolean }) {
  return (
    <label className="flex cursor-pointer items-center justify-between gap-5">
      <span><span className="block text-xs font-semibold text-slate-700">{title}</span><span className="mt-1 block text-[11px] leading-4 text-slate-400">{description}</span></span>
      <span className="relative shrink-0">
        <input type="checkbox" defaultChecked={checked} className="peer sr-only" />
        <span className="block h-6 w-11 rounded-full bg-slate-200 transition peer-checked:bg-accent" />
        <span className="absolute left-1 top-1 h-4 w-4 rounded-full bg-white shadow-sm transition peer-checked:translate-x-5" />
      </span>
    </label>
  );
}
