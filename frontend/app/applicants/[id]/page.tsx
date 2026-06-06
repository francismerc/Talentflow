import { notFound } from "next/navigation";
import { ApplicantDetail } from "@/components/applicants/applicant-detail";
import { applicants } from "@/lib/mock-data";

export function generateStaticParams() {
  return applicants.map((applicant) => ({ id: applicant.id }));
}

export default async function ApplicantDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const applicant = applicants.find((item) => item.id === id);
  if (!applicant) notFound();

  return <ApplicantDetail applicant={applicant} />;
}
