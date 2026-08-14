import { RefreshCw, Sparkles } from "lucide-react";
import { clsx } from "clsx";

interface StrategyBadgeProps {
  strategy: string;
  size?: "sm" | "md";
}

export default function StrategyBadge({ strategy, size = "sm" }: StrategyBadgeProps) {
  const norm = (strategy || "").toUpperCase();
  const isReuse = norm === "REUSE";

  const px = size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-3 py-1 text-xs";

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 font-mono font-semibold rounded-md border tracking-wider uppercase",
        isReuse
          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
          : "bg-purple-500/10 text-purple-400 border-purple-500/30 shadow-[0_0_12px_rgba(168,85,247,0.15)]",
        px
      )}
    >
      {isReuse ? <RefreshCw className="w-3 h-3 text-emerald-400 animate-spin-slow" /> : <Sparkles className="w-3 h-3 text-purple-400" />}
      <span>{isReuse ? "REUSE" : "GENERATE"}</span>
    </span>
  );
}
