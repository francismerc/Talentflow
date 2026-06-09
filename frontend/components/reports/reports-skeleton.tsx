import { Skeleton } from "@/components/ui/skeleton";

export function ReportsSkeleton() {
  return (
    <div className="space-y-6" role="status" aria-label="Loading recruitment report">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-80 max-w-full" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-10 w-36" />
          <Skeleton className="h-10 w-36" />
        </div>
      </div>
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="surface p-5">
            <Skeleton className="h-3 w-28" />
            <Skeleton className="mt-3 h-8 w-20" />
            <Skeleton className="mt-4 h-3 w-32" />
          </div>
        ))}
      </section>
      <section className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <ReportCardSkeleton />
        <ReportCardSkeleton />
      </section>
      <section className="grid gap-4 xl:grid-cols-2">
        <ReportCardSkeleton />
        <ReportCardSkeleton />
      </section>
      <span className="sr-only">Loading report data</span>
    </div>
  );
}

function ReportCardSkeleton() {
  return (
    <div className="surface overflow-hidden">
      <div className="space-y-2 border-b border-slate-100 px-5 py-4">
        <Skeleton className="h-4 w-36" />
        <Skeleton className="h-3 w-52 max-w-full" />
      </div>
      <div className="p-4">
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    </div>
  );
}
