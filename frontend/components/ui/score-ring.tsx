import { cn } from "@/lib/utils";

export function ScoreRing({
  score,
  size = "md",
}: {
  score: number;
  size?: "sm" | "md" | "lg";
}) {
  const tone =
    score >= 90
      ? "text-emerald-600"
      : score >= 80
        ? "text-blue-600"
        : score >= 70
          ? "text-amber-600"
          : "text-red-600";
  const sizes = {
    sm: "h-10 w-10 text-xs",
    md: "h-14 w-14 text-base",
    lg: "h-24 w-24 text-2xl",
  };

  return (
    <div
      className={cn(
        "relative grid shrink-0 place-items-center rounded-full bg-slate-50 font-bold",
        sizes[size],
        tone,
      )}
      style={{
        background: `conic-gradient(currentColor ${score * 3.6}deg, #e2e8f0 0deg)`,
      }}
    >
      <div className="absolute inset-[4px] rounded-full bg-white" />
      <span className="relative">{score}</span>
    </div>
  );
}
