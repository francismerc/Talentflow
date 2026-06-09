import { apiRequest } from "@/services/api-client";

export interface ResumeProcessResult {
  attachments_scanned: number;
  applicants_created: number;
  needs_review: number;
  failed: number;
  acknowledgments_sent: number;
  acknowledgment_errors: number;
}

interface ResumeProcessResponse {
  success: boolean;
  message: string;
  data: ResumeProcessResult;
}

export async function processStoredResumes(): Promise<ResumeProcessResult> {
  const response = await apiRequest<ResumeProcessResponse>("/resumes/process", {
    method: "POST",
    body: JSON.stringify({ max_attachments: 25 }),
  });
  return response.data;
}
