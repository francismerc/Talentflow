"use client";

import { useCallback, useEffect, useState } from "react";
import {
  generateApplicantAnalysis,
  getApplicant,
  sendCandidateEmail,
  type CandidateEmailType,
  updateApplicantStatus,
} from "@/services/applicants";
import { ApplicantDetail } from "@/components/applicants/applicant-detail";
import { ApiErrorState } from "@/components/ui/api-state";
import { PageSkeleton } from "@/components/loading/page-skeleton";
import type { Applicant } from "@/types";

export function ApplicantDetailPage({ applicantId }: { applicantId: string }) {
  const [applicant, setApplicant] = useState<Applicant | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState("");
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  const loadApplicant = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setApplicant(await getApplicant(applicantId));
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Applicant details could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }, [applicantId]);

  useEffect(() => {
    loadApplicant();
  }, [loadApplicant]);

  const handleStatusChange = async (status: "shortlisted" | "rejected") => {
    setActionLoading(true);
    setActionError("");
    try {
      const updatedApplicant = await updateApplicantStatus(applicantId, status);
      setApplicant(updatedApplicant);
      try {
        await sendCandidateEmail(applicantId, status);
        setApplicant(await getApplicant(applicantId));
      } catch (emailError) {
        setActionError(
          `Status updated, but the email was not sent: ${
            emailError instanceof Error
              ? emailError.message
              : "Unknown email delivery error."
          }`,
        );
      }
    } catch (requestError) {
      setActionError(
        requestError instanceof Error
          ? requestError.message
          : "Applicant status could not be updated.",
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleSendEmail = async (emailType: CandidateEmailType) => {
    setActionLoading(true);
    setActionError("");
    try {
      await sendCandidateEmail(applicantId, emailType);
      setApplicant(await getApplicant(applicantId));
    } catch (requestError) {
      setActionError(
        requestError instanceof Error
          ? requestError.message
          : "Candidate email could not be sent.",
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateAnalysis = async () => {
    setAnalysisLoading(true);
    setAnalysisError("");
    try {
      setApplicant(await generateApplicantAnalysis(applicantId));
    } catch (requestError) {
      setAnalysisError(
        requestError instanceof Error
          ? requestError.message
          : "Candidate analysis could not be generated.",
      );
    } finally {
      setAnalysisLoading(false);
    }
  };

  if (loading) return <PageSkeleton />;
  if (error) {
    return (
      <div className="surface">
        <ApiErrorState message={error} onRetry={loadApplicant} />
      </div>
    );
  }
  return applicant ? (
    <ApplicantDetail
      applicant={applicant}
      actionLoading={actionLoading}
      actionError={actionError}
      analysisLoading={analysisLoading}
      analysisError={analysisError}
      onStatusChange={handleStatusChange}
      onSendEmail={handleSendEmail}
      onGenerateAnalysis={handleGenerateAnalysis}
    />
  ) : null;
}
