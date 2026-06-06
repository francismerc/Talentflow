"use client";

import { Plus } from "lucide-react";
import { useState } from "react";
import { JobsTable } from "@/components/jobs/jobs-table";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";

export default function JobsPage() {
  const [createRequest, setCreateRequest] = useState(0);
  return (
    <div className="space-y-6">
      <PageHeader
        title="Jobs"
        description="Create openings and track candidate interest across active roles."
        actions={<Button className="w-full sm:w-auto" onClick={() => setCreateRequest((value) => value + 1)}><Plus className="h-4 w-4" /> Create job</Button>}
      />
      <JobsTable createRequest={createRequest} />
    </div>
  );
}
