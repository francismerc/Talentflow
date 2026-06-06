import { ApplicantDetailPage } from "@/components/applicants/applicant-detail-page";

export default async function ApplicantDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ApplicantDetailPage applicantId={id} />;
}
