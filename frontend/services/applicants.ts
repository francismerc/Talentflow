import { apiRequest } from "@/services/api-client";
import type {
  ApiListResponse,
  ApiResponse,
  Applicant,
  ApplicantApiRecord,
  ApplicantDetailApiRecord,
  ApplicantStatus,
} from "@/types";

export interface ApplicantListParams {
  page?: number;
  pageSize?: number;
  search?: string;
  jobId?: string;
  status?: string;
  minimumScore?: number;
  maximumScore?: number;
}

export interface ApplicantCreateInput {
  job_id: string;
  full_name: string;
  email: string;
  phone?: string | null;
  location?: string | null;
}

export async function getApplicants(
  params: ApplicantListParams = {},
): Promise<ApiListResponse<Applicant>> {
  const searchParams = new URLSearchParams({
    page: String(params.page ?? 1),
    page_size: String(params.pageSize ?? 20),
  });
  if (params.search) searchParams.set("search", params.search);
  if (params.jobId) searchParams.set("job_id", params.jobId);
  if (params.status) searchParams.set("status", params.status);
  if (params.minimumScore !== undefined) {
    searchParams.set("minimum_score", String(params.minimumScore));
  }
  if (params.maximumScore !== undefined) {
    searchParams.set("maximum_score", String(params.maximumScore));
  }

  const response = await apiRequest<
    ApiListResponse<ApplicantApiRecord>
  >(`/applicants?${searchParams.toString()}`);

  return {
    ...response,
    data: {
      ...response.data,
      items: response.data.items.map(mapApplicant),
    },
  };
}

export async function getApplicant(applicantId: string): Promise<Applicant> {
  const response = await apiRequest<ApiResponse<ApplicantDetailApiRecord>>(
    `/applicants/${applicantId}`,
  );
  return mapApplicant(response.data);
}

export async function getAllApplicants(): Promise<Applicant[]> {
  const firstPage = await getApplicants({ page: 1, pageSize: 100 });
  const items = [...firstPage.data.items];
  const totalPages = Math.ceil(firstPage.data.total / firstPage.data.page_size);

  for (let page = 2; page <= totalPages; page += 1) {
    const response = await getApplicants({ page, pageSize: 100 });
    items.push(...response.data.items);
  }
  return items;
}

export async function createApplicant(
  payload: ApplicantCreateInput,
): Promise<Applicant> {
  const response = await apiRequest<ApiResponse<ApplicantDetailApiRecord>>(
    "/applicants",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
  return mapApplicant(response.data);
}

export async function updateApplicantStatus(
  applicantId: string,
  status: "shortlisted" | "rejected",
  note?: string,
): Promise<Applicant> {
  const response = await apiRequest<ApiResponse<ApplicantDetailApiRecord>>(
    `/applicants/${applicantId}/status`,
    {
      method: "PATCH",
      body: JSON.stringify({ status, note }),
    },
  );
  return mapApplicant(response.data);
}

function mapApplicant(record: ApplicantApiRecord): Applicant {
  const analysis = record.current_analysis;
  const detail = record as ApplicantDetailApiRecord;

  return {
    id: record.id,
    name: record.full_name,
    email: record.email,
    phone: record.phone ?? "Not provided",
    position: record.job?.title ?? "Unassigned position",
    jobId: record.job_id,
    score: analysis?.score ?? 0,
    status: formatStatus(record.status),
    appliedAt: formatDate(record.applied_at),
    appliedAtRaw: record.applied_at,
    education: formatStructuredItems(detail.education, "Education not provided"),
    experience:
      detail.total_experience_years !== undefined
        ? formatExperience(detail.total_experience_years)
        : "Experience not provided",
    location: record.location ?? "Location not provided",
    summary: analysis?.summary ?? "AI analysis has not been generated yet.",
    strengths: analysis?.strengths ?? [],
    weaknesses: analysis?.weaknesses ?? [],
    matchedSkills: analysis?.matched_skills ?? [],
    missingSkills: analysis?.missing_skills ?? [],
    recommendation:
      analysis?.recommendation_reason ??
      "No recruiter recommendation is available yet.",
    resumeFileName: detail.resume_file_name ?? null,
    resumeStoragePath: detail.resume_storage_path ?? null,
    timeline: (detail.timeline ?? []).map((item) => ({
      id: item.id,
      title: item.title,
      detail: item.description ?? "",
      time: formatDateTime(item.occurred_at),
    })),
  };
}

function formatStatus(value: string): ApplicantStatus {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ") as ApplicantStatus;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatExperience(years: number | null): string {
  if (years === null) return "Experience not provided";
  return `${years} ${years === 1 ? "year" : "years"}`;
}

function formatStructuredItems(
  items: Array<Record<string, unknown>> | undefined,
  fallback: string,
): string {
  if (!items?.length) return fallback;

  return items
    .map((item) =>
      Object.values(item)
        .filter((value) => typeof value === "string" && value.trim())
        .join(", "),
    )
    .filter(Boolean)
    .join("; ");
}
