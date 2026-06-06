import { Download, Plus } from "lucide-react";
import { ApplicantsTable } from "@/components/applicants/applicants-table";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";

export default function ApplicantsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Applicants"
        description="Review, filter, and manage every candidate in your hiring pipeline."
        actions={
          <>
            <Button variant="outline" className="flex-1 sm:flex-none"><Download className="h-4 w-4" /> Export</Button>
            <Button className="flex-1 sm:flex-none"><Plus className="h-4 w-4" /> Add applicant</Button>
          </>
        }
      />
      <ApplicantsTable />
    </div>
  );
}
