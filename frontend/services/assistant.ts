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

export type AssistantActionType =
  | "mark_under_review"
  | "shortlist_candidate"
  | "move_to_interview"
  | "mark_hired"
  | "reject_candidate"
  | "send_shortlisted_email"
  | "send_rejected_email";

export interface AssistantActionProposal {
  action_type: AssistantActionType;
  applicant_id: string;
  candidate_name: string;
  title: string;
  description: string;
  confirm_label: string;
  tone: "default" | "danger";
}

interface AssistantChatResponse {
  success: boolean;
  message: string;
  data: {
    answer: string;
    candidates: AssistantCandidate[];
    suggested_prompts: string[];
    proposed_actions: AssistantActionProposal[];
  };
}

interface AssistantActionResponse {
  success: boolean;
  message: string;
  data: {
    action_type: AssistantActionType;
    applicant_id: string;
    candidate_name: string;
    status: string;
    message: string;
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

export async function executeAssistantAction(
  action: AssistantActionProposal,
): Promise<AssistantActionResponse["data"]> {
  const response = await apiRequest<AssistantActionResponse>(
    "/assistant/actions",
    {
      method: "POST",
      body: JSON.stringify({
        action_type: action.action_type,
        applicant_id: action.applicant_id,
      }),
    },
  );
  return response.data;
}
