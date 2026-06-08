import { apiRequest } from "@/services/api-client";
import type {
  ApiListResponse,
  ApiResponse,
  Job,
  JobApiRecord,
  JobDetail,
  JobDetailApiRecord,
} from "@/types";

export interface JobListParams {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: "draft" | "active" | "closed";
}

export interface JobMutationInput {
  title: string;
  description: string;
  required_skills: string[];
  location: string | null;
  employment_type: string;
  status: string;
}

export async function getJobs(
  params: JobListParams = {},
): Promise<ApiListResponse<Job>> {
  const searchParams = new URLSearchParams({
    page: String(params.page ?? 1),
    page_size: String(params.pageSize ?? 20),
  });
  if (params.search) searchParams.set("search", params.search);
  if (params.status) searchParams.set("status", params.status);

  const response = await apiRequest<
    ApiListResponse<JobApiRecord>
  >(`/jobs?${searchParams.toString()}`);

  return {
    ...response,
    data: {
      ...response.data,
      items: response.data.items.map(mapJob),
    },
  };
}

export async function getJob(jobId: string): Promise<JobDetail> {
  const response = await apiRequest<ApiResponse<JobDetailApiRecord>>(
    `/jobs/${jobId}`,
  );
  return mapJobDetail(response.data);
}

export async function createJob(payload: JobMutationInput): Promise<Job> {
  const response = await apiRequest<ApiResponse<JobDetailApiRecord>>("/jobs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return mapJob(response.data);
}

export async function updateJob(
  jobId: string,
  payload: JobMutationInput,
): Promise<JobDetail> {
  const response = await apiRequest<ApiResponse<JobDetailApiRecord>>(
    `/jobs/${jobId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
  return mapJobDetail(response.data);
}

export async function deleteJob(jobId: string): Promise<void> {
  await apiRequest(`/jobs/${jobId}`, { method: "DELETE" });
}

function mapJob(record: JobApiRecord): Job {
  return {
    id: record.id,
    title: record.title,
    location: record.location ?? "Location not specified",
    type: formatLabel(record.employment_type),
    description: record.description,
    skills: record.required_skills,
    createdAt: formatDate(record.created_at),
    applicants: record.applicant_count,
    status: formatLabel(record.status) as Job["status"],
  };
}

function mapJobDetail(record: JobDetailApiRecord): JobDetail {
  return {
    ...mapJob(record),
    candidates: record.applicants.map((candidate) => {
      const analysis = candidate.applicant_ai_analyses.find(
        (item) => item.is_current,
      );
      return {
        id: candidate.id,
        name: candidate.full_name,
        email: candidate.email,
        status: formatLabel(candidate.status),
        appliedAt: formatDate(candidate.applied_at),
        score: analysis?.score ?? 0,
        recommendation: analysis?.recommendation_reason ?? null,
      };
    }),
  };
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function formatLabel(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
