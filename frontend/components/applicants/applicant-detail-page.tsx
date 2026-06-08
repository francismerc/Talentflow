"use client";

import { useCallback, useEffect, useState } from "react";
import { getApplicant, updateApplicantStatus } from "@/services/applicants";
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
      setApplicant(await updateApplicantStatus(applicantId, status));
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
      onStatusChange={handleStatusChange}
    />
  ) : null;
}
