"use client";

import { useState, type ReactNode } from "react";
import { FloatingAssistant } from "@/components/assistant/floating-assistant";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export function AppShell({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(false);

  return (
    <div className="min-h-screen">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onAssistantOpen={() => setAssistantOpen(true)}
      />
      <div className="lg:pl-64">
        <Topbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="mx-auto max-w-[1600px] p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
      <FloatingAssistant open={assistantOpen} onOpenChange={setAssistantOpen} />
    </div>
  );
}
