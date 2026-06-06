"use client";

import { useEffect, useRef, useState } from "react";
import {
  ArrowUp,
  Bot,
  FileBarChart,
  GitCompareArrows,
  MessageCircle,
  Minus,
  RotateCcw,
  Search,
  Sparkles,
  Users,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";

const suggestedPrompts = [
  { label: "Show top candidates", icon: Users },
  { label: "Find React developers", icon: Search },
  { label: "Compare candidates", icon: GitCompareArrows },
  { label: "Generate a report", icon: FileBarChart },
];

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function FloatingAssistant({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const messageEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function submitMessage(message: string) {
    const trimmedMessage = message.trim();
    if (!trimmedMessage) return;

    setMessages((current) => [
      ...current,
      { role: "user", content: trimmedMessage },
      {
        role: "assistant",
        content:
          "I found three strong matches: Maya Chen at 94, Ethan Wright at 91, and Sofia Rodriguez at 88. Maya leads on overall role fit, while Ethan has the strongest frontend background.",
      },
    ]);
    setInput("");
  }

  function resetConversation() {
    setMessages([]);
    setInput("");
  }

  return (
    <div className="pointer-events-none fixed inset-x-3 bottom-[max(0.75rem,env(safe-area-inset-bottom))] z-[60] flex flex-col items-end sm:inset-x-auto sm:bottom-6 sm:right-6">
      <section
        aria-label="TalentFlow AI assistant"
        className={cn(
          "pointer-events-auto mb-3 flex h-[min(620px,calc(100dvh-6.5rem))] w-full origin-bottom-right flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-floating transition duration-200 sm:w-[390px]",
          open
            ? "translate-y-0 scale-100 opacity-100"
            : "pointer-events-none translate-y-3 scale-95 opacity-0",
        )}
      >
        <header className="flex h-16 shrink-0 items-center gap-3 border-b border-slate-100 bg-primary px-4 text-white">
          <span className="relative grid h-9 w-9 place-items-center rounded-xl bg-white/10">
            <Sparkles className="h-[18px] w-[18px]" />
            <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-primary bg-success" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-bold">TalentFlow AI</p>
            <p className="text-[10px] text-slate-300">Recruiter assistant · Online</p>
          </div>
          <button
            onClick={resetConversation}
            aria-label="Start a new conversation"
            title="New conversation"
            className="focus-ring rounded-lg p-2 text-slate-300 hover:bg-white/10 hover:text-white"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          <button
            onClick={() => onOpenChange(false)}
            aria-label="Minimize assistant"
            className="focus-ring rounded-lg p-2 text-slate-300 hover:bg-white/10 hover:text-white"
          >
            <Minus className="h-4 w-4" />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto bg-slate-50/50">
          {messages.length === 0 ? (
            <div className="flex min-h-full flex-col px-4 py-5">
              <div className="flex gap-3">
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-primary text-white">
                  <Bot className="h-4 w-4" />
                </span>
                <div className="rounded-2xl rounded-tl-md border border-slate-200 bg-white px-3.5 py-3 shadow-sm">
                  <p className="text-xs leading-5 text-slate-600">
                    Hi Alex. I can help you find candidates, compare applicants, and understand
                    your hiring pipeline.
                  </p>
                </div>
              </div>

              <div className="mt-auto pt-7">
                <p className="mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Suggested questions
                </p>
                <div className="grid gap-2">
                  {suggestedPrompts.map((prompt) => (
                    <button
                      key={prompt.label}
                      onClick={() => submitMessage(prompt.label)}
                      className="focus-ring flex items-center gap-2.5 rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-left text-xs font-semibold text-slate-600 shadow-sm transition hover:border-blue-200 hover:bg-blue-50/50 hover:text-accent"
                    >
                      <prompt.icon className="h-3.5 w-3.5 text-slate-400" />
                      {prompt.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4 p-4">
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={cn("flex gap-2.5", message.role === "user" && "justify-end")}
                >
                  {message.role === "assistant" ? (
                    <span className="grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-primary text-white">
                      <Bot className="h-3.5 w-3.5" />
                    </span>
                  ) : null}
                  <div
                    className={cn(
                      "max-w-[82%] rounded-2xl px-3.5 py-2.5 text-xs leading-5 shadow-sm",
                      message.role === "user"
                        ? "rounded-br-md bg-accent text-white"
                        : "rounded-tl-md border border-slate-200 bg-white text-slate-600",
                    )}
                  >
                    {message.content}
                  </div>
                </div>
              ))}
              <div ref={messageEndRef} />
            </div>
          )}
        </div>

        <footer className="shrink-0 border-t border-slate-100 bg-white p-3">
          <form
            onSubmit={(event) => {
              event.preventDefault();
              submitMessage(input);
            }}
          >
            <div className="relative rounded-xl border border-slate-200 bg-white transition focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100">
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    submitMessage(input);
                  }
                }}
                placeholder="Ask about your candidates..."
                rows={1}
                className="min-h-12 w-full resize-none rounded-xl bg-transparent py-3.5 pl-3.5 pr-12 text-xs text-primary outline-none placeholder:text-slate-400"
              />
              <button
                type="submit"
                disabled={!input.trim()}
                aria-label="Send message"
                className="focus-ring absolute bottom-2 right-2 grid h-8 w-8 place-items-center rounded-lg bg-primary text-white transition hover:bg-secondary disabled:bg-slate-200"
              >
                <ArrowUp className="h-4 w-4" />
              </button>
            </div>
            <p className="mt-2 text-center text-[9px] text-slate-400">
              Review AI recommendations before taking action.
            </p>
          </form>
        </footer>
      </section>

      <button
        onClick={() => onOpenChange(!open)}
        aria-label={open ? "Close TalentFlow AI assistant" : "Open TalentFlow AI assistant"}
        aria-expanded={open}
        className={cn(
          "pointer-events-auto relative grid h-14 w-14 place-items-center rounded-full text-white shadow-floating transition duration-200 hover:-translate-y-0.5",
          open ? "bg-secondary" : "bg-accent hover:bg-blue-700",
        )}
      >
        <span
          className={cn(
            "absolute inset-0 grid place-items-center transition",
            open ? "rotate-0 scale-100 opacity-100" : "-rotate-90 scale-75 opacity-0",
          )}
        >
          <X className="h-5 w-5" />
        </span>
        <span
          className={cn(
            "absolute inset-0 grid place-items-center transition",
            open ? "rotate-90 scale-75 opacity-0" : "rotate-0 scale-100 opacity-100",
          )}
        >
          <MessageCircle className="h-6 w-6" />
        </span>
        {!open ? (
          <span className="absolute right-0 top-0 h-3.5 w-3.5 rounded-full border-2 border-white bg-success" />
        ) : null}
      </button>
    </div>
  );
}
