export type ApplicantStatus =
  | "New"
  | "Under Review"
  | "Shortlisted"
  | "Interview"
  | "Rejected";

export interface Applicant {
  id: string;
  name: string;
  email: string;
  phone: string;
  position: string;
  score: number;
  status: ApplicantStatus;
  appliedAt: string;
  education: string;
  experience: string;
  location: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  matchedSkills: string[];
  missingSkills: string[];
  recommendation: string;
}

export interface Job {
  id: string;
  title: string;
  department: string;
  location: string;
  type: string;
  description: string;
  skills: string[];
  createdAt: string;
  applicants: number;
  status: "Active" | "Draft" | "Closed";
}
