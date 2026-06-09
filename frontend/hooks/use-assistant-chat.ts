"use client";

import { useCallback, useState } from "react";
import {
  sendAssistantMessage,
  type AssistantCandidate,
} from "@/services/assistant";

export interface AssistantUiMessage {
  role: "user" | "assistant";
  content: string;
  candidates?: AssistantCandidate[];
  suggestedPrompts?: string[];
}

export function useAssistantChat() {
  const [messages, setMessages] = useState<AssistantUiMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

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

  const resetConversation = useCallback(() => {
    setMessages([]);
    setError("");
  }, []);

  return {
    messages,
    isLoading,
    error,
    submitMessage,
    resetConversation,
  };
}
