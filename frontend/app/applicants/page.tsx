"use client";

import { Download, Plus } from "lucide-react";
import { useState } from "react";
import { ApplicantsTable } from "@/components/applicants/applicants-table";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";

export default function ApplicantsPage() {
  const [addRequest, setAddRequest] = useState(0);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Applicants"
        description="Review, filter, and manage every candidate in your hiring pipeline."
        actions={
          <>
            <Button variant="outline" className="flex-1 sm:flex-none"><Download className="h-4 w-4" /> Export</Button>
            <Button className="flex-1 sm:flex-none" onClick={() => setAddRequest((value) => value + 1)}><Plus className="h-4 w-4" /> Add applicant</Button>
          </>
        }
      />
      <ApplicantsTable addRequest={addRequest} />
    </div>
  );
}
