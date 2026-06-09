"use client";

import { useState } from "react";
import {
  BriefcaseBusiness,
  Eye,
  Mail,
  MessagesSquare,
  ShieldCheck,
  UserRoundCheck,
  UserRoundX,
} from "lucide-react";
import { ConfirmDialog } from "@/components/ui/modal";
import { cn } from "@/lib/utils";
import type { AssistantActionProposal } from "@/services/assistant";

const actionIcons = {
  mark_under_review: Eye,
  shortlist_candidate: UserRoundCheck,
  move_to_interview: MessagesSquare,
  mark_hired: BriefcaseBusiness,
  reject_candidate: UserRoundX,
  send_shortlisted_email: Mail,
  send_rejected_email: Mail,
};

export function ActionProposal({
  action,
  compact = false,
  loading,
  onConfirm,
}: {
  action: AssistantActionProposal;
  compact?: boolean;
  loading: boolean;
  onConfirm: (action: AssistantActionProposal) => Promise<boolean>;
}) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const Icon = actionIcons[action.action_type] ?? ShieldCheck;

  return (
    <>
      <div
        className={cn(
          "mt-3 rounded-xl border border-blue-200 bg-blue-50/60",
          compact ? "p-2.5" : "p-3.5",
        )}
      >
        <div className="flex items-start gap-2.5">
          <span className="grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-white text-accent shadow-sm">
            <Icon className="h-3.5 w-3.5" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-[11px] font-bold text-primary">{action.title}</p>
            {!compact ? (
              <p className="mt-1 text-[10px] leading-4 text-slate-500">
                {action.description}
              </p>
            ) : null}
            <button
              type="button"
              onClick={() => setDialogOpen(true)}
              disabled={loading}
              className={cn(
                "focus-ring mt-2 rounded-lg px-3 py-1.5 text-[10px] font-bold text-white disabled:opacity-50",
                action.tone === "danger"
                  ? "bg-red-500 hover:bg-red-600"
                  : "bg-accent hover:bg-blue-700",
              )}
            >
              Review action
            </button>
          </div>
        </div>
      </div>
      <ConfirmDialog
        open={dialogOpen}
        title={action.title}
        description={`${action.description} TalentFlow will not proceed until you confirm.`}
        confirmLabel={action.confirm_label}
        loadingLabel="Completing..."
        loading={loading}
        tone={action.tone}
        onCancel={() => {
          if (!loading) setDialogOpen(false);
        }}
        onConfirm={() => {
          void onConfirm(action).then((completed) => {
            if (completed) setDialogOpen(false);
          });
        }}
      />
    </>
  );
}
