"use client";

import { useCallback, useEffect, useState } from "react";
import { getApplicant } from "@/services/applicants";
import { ApplicantDetail } from "@/components/applicants/applicant-detail";
import { ApiErrorState } from "@/components/ui/api-state";
import { PageSkeleton } from "@/components/loading/page-skeleton";
import type { Applicant } from "@/types";

export function ApplicantDetailPage({ applicantId }: { applicantId: string }) {
  const [applicant, setApplicant] = useState<Applicant | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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

  if (loading) return <PageSkeleton />;
  if (error) {
    return (
      <div className="surface">
        <ApiErrorState message={error} onRetry={loadApplicant} />
      </div>
    );
  }
  return applicant ? <ApplicantDetail applicant={applicant} /> : null;
}
