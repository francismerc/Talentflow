import { apiRequest } from "@/services/api-client";

export interface AssistantCandidate {
  applicant_id: string;
  name: string;
  job_title: string;
  score: number | null;
  status: string;
  reason: string;
}

export interface AssistantHistoryMessage {
  role: "user" | "assistant";
  content: string;
}

interface AssistantChatResponse {
  success: boolean;
  message: string;
  data: {
    answer: string;
    candidates: AssistantCandidate[];
    suggested_prompts: string[];
  };
}

export async function sendAssistantMessage(
  message: string,
  history: AssistantHistoryMessage[],
): Promise<AssistantChatResponse["data"]> {
  const response = await apiRequest<AssistantChatResponse>("/assistant/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      history: history.slice(-12),
    }),
  });
  return response.data;
}
