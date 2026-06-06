import { JobDetailPage } from "@/components/jobs/job-detail-page";

export default async function JobDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <JobDetailPage jobId={id} />;
}
