import { Skeleton } from "@/components/ui/skeleton";

export function PageSkeleton() {
  return (
    <div className="space-y-6" role="status" aria-label="Loading page">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div className="space-y-2">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-8 w-52 sm:w-64" />
          <Skeleton className="h-4 w-full max-w-sm" />
        </div>
        <Skeleton className="h-10 w-36" />
      </div>

      <section className="grid grid-cols-2 gap-3 xl:grid-cols-5">
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="surface p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 space-y-3">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-7 w-14" />
              </div>
              <Skeleton className="h-9 w-9 rounded-xl" />
            </div>
            <Skeleton className="mt-4 h-3 w-28" />
          </div>
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <SkeletonCard heightClass="h-72" />
        <SkeletonCard heightClass="h-72" />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <div className="surface overflow-hidden">
          <SkeletonHeader />
          <div className="divide-y divide-slate-100 px-4">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="flex items-center gap-3 py-3">
                <Skeleton className="h-9 w-9 shrink-0 rounded-full" />
                <div className="min-w-0 flex-1 space-y-2">
                  <Skeleton className="h-3 w-32" />
                  <Skeleton className="h-2.5 w-44 max-w-full" />
                </div>
                <Skeleton className="h-6 w-16 rounded-full" />
              </div>
            ))}
          </div>
        </div>
        <SkeletonCard heightClass="h-72" />
      </section>
      <span className="sr-only">Loading TalentFlow AI</span>
    </div>
  );
}

function SkeletonCard({ heightClass }: { heightClass: string }) {
  return (
    <div className="surface overflow-hidden">
      <SkeletonHeader />
      <div className="p-4">
        <Skeleton className={`${heightClass} w-full rounded-xl`} />
      </div>
    </div>
  );
}

function SkeletonHeader() {
  return (
    <div className="space-y-2 border-b border-slate-100 px-5 py-4">
      <Skeleton className="h-3.5 w-32" />
      <Skeleton className="h-2.5 w-48 max-w-full" />
    </div>
  );
}
