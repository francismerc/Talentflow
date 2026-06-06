import { cn, getInitials } from "@/lib/utils";

const colors = [
  "bg-blue-100 text-blue-700",
  "bg-violet-100 text-violet-700",
  "bg-emerald-100 text-emerald-700",
  "bg-amber-100 text-amber-700",
  "bg-rose-100 text-rose-700",
];

export function Avatar({
  name,
  className,
}: {
  name: string;
  className?: string;
}) {
  const colorIndex = name.charCodeAt(0) % colors.length;
  return (
    <span
      className={cn(
        "inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xs font-bold",
        colors[colorIndex],
        className,
      )}
    >
      {getInitials(name)}
    </span>
  );
}
