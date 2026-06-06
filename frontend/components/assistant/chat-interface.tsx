"use client";

import { useState } from "react";
import {
  ArrowUp,
  Bot,
  ChevronLeft,
  FileBarChart,
  GitCompareArrows,
  Menu,
  MessageSquarePlus,
  MoreHorizontal,
  PanelLeftClose,
  Search,
  Sparkles,
  User,
  Users,
} from "lucide-react";
import { Avatar } from "@/components/ui/avatar";
import { applicants } from "@/lib/mock-data";

const prompts = [
  { label: "Show top candidates", icon: Users },
  { label: "Find React developers", icon: Search },
  { label: "Show applicants above 85 score", icon: Sparkles },
  { label: "Compare candidates", icon: GitCompareArrows },
  { label: "Generate recruitment report", icon: FileBarChart },
];

const history = [
  "Top frontend candidates",
  "May recruitment summary",
  "Product designer search",
  "Compare Maya and Sofia",
];

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function ChatInterface() {
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);

  function submitMessage(message: string) {
    const trimmed = message.trim();
    if (!trimmed) return;
    setMessages((current) => [
      ...current,
      { role: "user", content: trimmed },
      {
        role: "assistant",
        content:
          "Based on the current candidate pipeline, I found several strong matches. Maya Chen leads with a 94 AI score, followed by Ethan Wright at 91 and Sofia Rodriguez at 88. I can break down their experience, skills, and fit for a specific role.",
      },
    ]);
    setInput("");
  }

  return (
    <div className="surface flex min-h-[calc(100vh-8rem)] overflow-hidden">
      <aside className={`${sidebarOpen ? "w-64" : "w-0"} hidden shrink-0 overflow-hidden border-r border-slate-100 bg-slate-50/60 transition-all md:block`}>
        <div className="flex w-64 flex-col p-3">
          <button onClick={() => setMessages([])} className="focus-ring flex h-10 items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 text-xs font-bold text-primary shadow-sm hover:bg-slate-50">
            <MessageSquarePlus className="h-4 w-4" /> New conversation
          </button>
          <p className="px-2 pb-2 pt-6 text-[10px] font-bold uppercase tracking-wider text-slate-400">Recent</p>
          {history.map((item, index) => (
            <button key={item} className={`focus-ring flex items-center gap-2 rounded-lg px-2.5 py-2.5 text-left text-xs ${index === 0 ? "bg-white font-semibold text-primary shadow-sm" : "text-slate-500 hover:bg-white"}`}>
              <span className="truncate">{item}</span>
              {index === 0 ? <MoreHorizontal className="ml-auto h-3.5 w-3.5 shrink-0 text-slate-400" /> : null}
            </button>
          ))}
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex h-14 items-center border-b border-slate-100 px-4">
          <button onClick={() => setSidebarOpen((value) => !value)} className="focus-ring rounded-lg p-2 text-slate-400 hover:bg-slate-100">
            {sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
          <div className="ml-2">
            <p className="text-xs font-bold text-primary">Recruiter Assistant</p>
            <p className="text-[10px] text-emerald-600">● Ready to help</p>
          </div>
          <button className="focus-ring ml-auto rounded-lg p-2 text-slate-400 hover:bg-slate-100"><MoreHorizontal className="h-4 w-4" /></button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="mx-auto flex min-h-full max-w-2xl flex-col items-center justify-center px-5 py-12 text-center">
              <span className="grid h-12 w-12 place-items-center rounded-2xl bg-primary text-white shadow-lg shadow-slate-300">
                <Sparkles className="h-5 w-5" />
              </span>
              <h1 className="mt-5 text-xl font-bold tracking-tight text-primary">How can I help with hiring today?</h1>
              <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                Ask about candidates, compare applicants, explore your pipeline, or create a recruitment report.
              </p>
              <div className="mt-8 grid w-full gap-2 sm:grid-cols-2">
                {prompts.map((prompt, index) => (
                  <button
                    key={prompt.label}
                    onClick={() => submitMessage(prompt.label)}
                    className={`focus-ring flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3.5 text-left text-xs font-semibold text-slate-600 shadow-sm transition hover:border-blue-200 hover:bg-blue-50/40 hover:text-accent ${index === prompts.length - 1 ? "sm:col-span-2" : ""}`}
                  >
                    <span className="grid h-7 w-7 place-items-center rounded-lg bg-slate-100 text-slate-500"><prompt.icon className="h-3.5 w-3.5" /></span>
                    {prompt.label}
                    <ChevronLeft className="ml-auto h-3.5 w-3.5 rotate-180 text-slate-300" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mx-auto max-w-3xl space-y-7 px-5 py-8">
              {messages.map((message, index) => (
                <div key={index} className="flex gap-3">
                  {message.role === "assistant" ? (
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-primary text-white"><Bot className="h-4 w-4" /></span>
                  ) : (
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-slate-100 text-slate-600"><User className="h-4 w-4" /></span>
                  )}
                  <div className="pt-1">
                    <p className="text-xs font-bold text-primary">{message.role === "assistant" ? "TalentFlow AI" : "You"}</p>
                    <p className="mt-2 text-sm leading-7 text-slate-600">{message.content}</p>
                    {message.role === "assistant" && index === messages.length - 1 ? (
                      <div className="mt-4 grid gap-2 sm:grid-cols-3">
                        {applicants.slice(0, 3).map((candidate) => (
                          <div key={candidate.id} className="rounded-xl border border-slate-200 p-3 text-left">
                            <div className="flex items-center gap-2">
                              <Avatar name={candidate.name} className="h-7 w-7 text-[9px]" />
                              <div className="min-w-0">
                                <p className="truncate text-[11px] font-bold text-primary">{candidate.name}</p>
                                <p className="text-[10px] text-slate-400">{candidate.score}% match</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="border-t border-slate-100 bg-white p-4">
          <form
            onSubmit={(event) => {
              event.preventDefault();
              submitMessage(input);
            }}
            className="mx-auto max-w-3xl"
          >
            <div className="relative rounded-xl border border-slate-200 bg-white shadow-sm transition focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100">
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    submitMessage(input);
                  }
                }}
                placeholder="Ask TalentFlow AI about your candidates..."
                className="min-h-[56px] w-full resize-none rounded-xl bg-transparent py-4 pl-4 pr-14 text-sm outline-none placeholder:text-slate-400"
                rows={1}
              />
              <button
                type="submit"
                disabled={!input.trim()}
                className="focus-ring absolute bottom-2.5 right-2.5 grid h-8 w-8 place-items-center rounded-lg bg-primary text-white transition hover:bg-secondary disabled:bg-slate-200"
              >
                <ArrowUp className="h-4 w-4" />
              </button>
            </div>
            <p className="mt-2 text-center text-[10px] text-slate-400">TalentFlow AI can make mistakes. Review candidate recommendations before taking action.</p>
          </form>
        </div>
      </div>
    </div>
  );
}
