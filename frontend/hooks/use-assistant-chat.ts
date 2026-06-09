"use client";

import { useCallback, useState } from "react";
import {
  executeAssistantAction,
  sendAssistantMessage,
  type AssistantActionProposal,
  type AssistantCandidate,
} from "@/services/assistant";

export interface AssistantUiMessage {
  role: "user" | "assistant";
  content: string;
  candidates?: AssistantCandidate[];
  suggestedPrompts?: string[];
  proposedActions?: AssistantActionProposal[];
}

export function useAssistantChat() {
  const [messages, setMessages] = useState<AssistantUiMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");

  const submitMessage = useCallback(
    async (message: string) => {
      const trimmed = message.trim();
      if (!trimmed || isLoading) return;

      const history = messages.map(({ role, content }) => ({ role, content }));
      setMessages((current) => [
        ...current,
        { role: "user", content: trimmed },
      ]);
      setIsLoading(true);
      setError("");
      try {
        const response = await sendAssistantMessage(trimmed, history);
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content: response.answer,
            candidates: response.candidates,
            suggestedPrompts: response.suggested_prompts,
            proposedActions: response.proposed_actions,
          },
        ]);
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "The assistant could not answer this request.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, messages],
  );

  const executeAction = useCallback(
    async (action: AssistantActionProposal): Promise<boolean> => {
      if (isActionLoading) return false;

      setIsActionLoading(true);
      setActionError("");
      try {
        const result = await executeAssistantAction(action);
        setMessages((current) => [
          ...current.map((message) => ({
            ...message,
            proposedActions: message.proposedActions?.filter(
              (proposal) =>
                proposal.action_type !== action.action_type ||
                proposal.applicant_id !== action.applicant_id,
            ),
          })),
          {
            role: "assistant",
            content: result.message,
            suggestedPrompts:
              result.action_type === "shortlist_candidate"
                ? [`Send shortlisted email to ${result.candidate_name}`]
                : result.action_type === "reject_candidate"
                  ? [`Send rejection email to ${result.candidate_name}`]
                  : [],
          },
        ]);
        return true;
      } catch (requestError) {
        setActionError(
          requestError instanceof Error
            ? requestError.message
            : "The confirmed action could not be completed.",
        );
        return false;
      } finally {
        setIsActionLoading(false);
      }
    },
    [isActionLoading],
  );

  const resetConversation = useCallback(() => {
    setMessages([]);
    setError("");
    setActionError("");
  }, []);

  return {
    messages,
    isLoading,
    isActionLoading,
    error,
    actionError,
    submitMessage,
    executeAction,
    resetConversation,
  };
}
