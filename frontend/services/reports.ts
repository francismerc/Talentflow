import { apiRequest } from "@/services/api-client";

export interface RecruitmentReport {
  months: number;
  period_start: string;
  period_end: string;
  total_applications: number;
  open_positions: number;
  average_candidate_score: number | null;
  shortlisted_rate: number;
  monthly_applications: Array<{
    month: string;
    month_start: string;
    applications: number;
    shortlisted: number;
  }>;
  status_distribution: Array<{
    status: string;
    count: number;
  }>;
  top_skills: Array<{
    skill: string;
    count: number;
  }>;
  top_positions: Array<{
    job_id: string;
    title: string;
    count: number;
  }>;
  summary: string;
}

interface RecruitmentReportResponse {
  success: boolean;
  message: string;
  data: RecruitmentReport;
}

export async function getRecruitmentReport(
  months: number,
): Promise<RecruitmentReport> {
  const response = await apiRequest<RecruitmentReportResponse>(
    `/reports/overview?months=${months}`,
  );
  return response.data;
}
