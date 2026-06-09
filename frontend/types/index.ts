export type ApplicantStatus =
  | "New"
  | "Under Review"
  | "Shortlisted"
  | "Interview"
  | "Hired"
  | "Rejected"
  | "Withdrawn";

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface ApiListResponse<T> {
  success: boolean;
  message: string;
  data: {
    items: T[];
    page: number;
    page_size: number;
    total: number;
  };
}

export interface ApplicantAnalysisApiRecord {
  id?: string;
  score: number;
  summary?: string | null;
  strengths: string[];
  weaknesses: string[];
  recommendation: string;
  recommendation_reason?: string | null;
  matched_skills: string[];
  missing_skills: string[];
  is_current: boolean;
}

export interface ApplicantApiRecord {
  id: string;
  job_id: string;
  full_name: string;
  email: string;
  phone: string | null;
  location: string | null;
  status: string;
  applied_at: string;
  created_at: string;
  job: {
    id: string;
    title: string;
  } | null;
  current_analysis: ApplicantAnalysisApiRecord | null;
}

export interface ApplicantDetailApiRecord extends ApplicantApiRecord {
  education: Array<Record<string, unknown>>;
  experience: Array<Record<string, unknown>>;
  total_experience_years: number | null;
  skills: string[];
  resume_file_name: string | null;
  resume_storage_path: string | null;
  timeline: Array<{
    id: string;
    title: string;
    description: string | null;
    occurred_at: string;
  }>;
}

export interface Applicant {
  id: string;
  jobId?: string;
  hasAnalysis: boolean;
  name: string;
  email: string;
  phone: string;
  position: string;
  score: number;
  status: ApplicantStatus;
  appliedAt: string;
  appliedAtRaw?: string;
  education: string;
  experience: string;
  location: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  matchedSkills: string[];
  missingSkills: string[];
  recommendation: string;
  resumeFileName?: string | null;
  resumeStoragePath?: string | null;
  timeline?: Array<{
    id: string;
    title: string;
    detail: string;
    time: string;
  }>;
}

export interface JobApiRecord {
  id: string;
  title: string;
  description: string;
  required_skills: string[];
  location: string | null;
  employment_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  applicant_count: number;
}

export interface JobDetailApiRecord extends JobApiRecord {
  applicants: Array<{
    id: string;
    full_name: string;
    email: string;
    status: string;
    applied_at: string;
    applicant_ai_analyses: Array<{
      score: number;
      recommendation: string;
      recommendation_reason: string;
      is_current: boolean;
    }>;
  }>;
}

export interface Job {
  id: string;
  title: string;
  department?: string;
  location: string;
  type: string;
  description: string;
  skills: string[];
  createdAt: string;
  applicants: number;
  status: "Active" | "Draft" | "Closed";
}

export interface JobDetail extends Job {
  candidates: Array<{
    id: string;
    name: string;
    email: string;
    status: string;
    appliedAt: string;
    score: number;
    recommendation: string | null;
  }>;
}
