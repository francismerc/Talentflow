import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export function ApiErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="grid place-items-center px-5 py-16 text-center">
      <span className="grid h-10 w-10 place-items-center rounded-full bg-red-50 text-red-500">
        <AlertCircle className="h-5 w-5" />
      </span>
      <p className="mt-3 text-sm font-bold text-primary">Unable to load data</p>
      <p className="mt-1 max-w-md text-xs leading-5 text-slate-500">{message}</p>
      <Button variant="outline" size="sm" className="mt-4" onClick={onRetry}>
        <RefreshCw className="h-3.5 w-3.5" /> Retry
      </Button>
    </div>
  );
}

export function TableSkeleton({ rows = 6 }: { rows?: number }) {
  return (
    <div className="space-y-1 p-4" role="status" aria-label="Loading data">
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="flex items-center gap-3 border-b border-slate-100 py-3 last:border-0">
          <Skeleton className="h-9 w-9 shrink-0 rounded-full" />
          <div className="min-w-0 flex-1 space-y-2">
            <Skeleton className="h-3 w-36" />
            <Skeleton className="h-2.5 w-52 max-w-full" />
          </div>
          <Skeleton className="h-6 w-20 rounded-full" />
        </div>
      ))}
      <span className="sr-only">Loading TalentFlow data</span>
    </div>
  );
}
