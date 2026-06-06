"use client";

import {
  BriefcaseBusiness,
  ChartNoAxesCombined,
  LayoutDashboard,
  Settings,
  Sparkles,
  Users,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Applicants", href: "/applicants", icon: Users },
  { name: "Jobs", href: "/jobs", icon: BriefcaseBusiness },
  { name: "AI Assistant", href: "/assistant", icon: Sparkles },
  { name: "Reports", href: "/reports", icon: ChartNoAxesCombined },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar({
  open,
  onClose,
  onAssistantOpen,
}: {
  open: boolean;
  onClose: () => void;
  onAssistantOpen: () => void;
}) {
  const pathname = usePathname();

  return (
    <>
      {open ? (
        <button
          aria-label="Close navigation"
          className="fixed inset-0 z-40 bg-slate-950/35 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      ) : null}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-200 lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-slate-100 px-5">
          <Link href="/" className="focus-ring flex items-center gap-2.5 rounded-lg" onClick={onClose}>
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-white shadow-sm">
              <Sparkles className="h-4 w-4" />
            </span>
            <span className="text-[15px] font-bold tracking-tight text-primary">
              TalentFlow <span className="text-accent">AI</span>
            </span>
          </Link>
          <button
            className="focus-ring rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 lg:hidden"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 p-3">
          <p className="px-3 pb-2 pt-3 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
            Workspace
          </p>
          {navigation.map((item) => {
            const active =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

            if (item.name === "AI Assistant") {
              return (
                <button
                  key={item.name}
                  onClick={() => {
                    onAssistantOpen();
                    onClose();
                  }}
                  className="focus-ring flex h-10 w-full items-center gap-3 rounded-lg px-3 text-sm font-medium text-slate-500 transition hover:bg-slate-50 hover:text-primary"
                >
                  <item.icon className="h-[18px] w-[18px]" />
                  {item.name}
                  <span className="ml-auto rounded bg-blue-50 px-1.5 py-0.5 text-[9px] font-bold text-blue-600">
                    AI
                  </span>
                </button>
              );
            }

            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "focus-ring flex h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium transition",
                  active
                    ? "bg-slate-100 text-primary"
                    : "text-slate-500 hover:bg-slate-50 hover:text-primary",
                )}
              >
                <item.icon className={cn("h-[18px] w-[18px]", active && "text-accent")} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="m-3 rounded-xl border border-blue-100 bg-blue-50/60 p-3.5">
          <div className="mb-2 flex items-center gap-2 text-xs font-bold text-primary">
            <span className="grid h-6 w-6 place-items-center rounded-md bg-white text-accent shadow-sm">
              <Sparkles className="h-3.5 w-3.5" />
            </span>
            AI processing
          </div>
          <p className="text-[11px] leading-4 text-slate-500">12 resumes analyzed this week</p>
          <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-blue-100">
            <div className="h-full w-3/4 rounded-full bg-accent" />
          </div>
        </div>

        <div className="border-t border-slate-100 p-3">
          <button className="focus-ring flex w-full items-center gap-3 rounded-lg p-2 text-left hover:bg-slate-50">
            <span className="grid h-9 w-9 place-items-center rounded-full bg-primary text-xs font-bold text-white">
              AS
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-semibold text-primary">Alex Smith</span>
              <span className="block truncate text-[11px] text-slate-400">Recruiting Lead</span>
            </span>
            <span className="text-slate-400">•••</span>
          </button>
        </div>
      </aside>
    </>
  );
}
