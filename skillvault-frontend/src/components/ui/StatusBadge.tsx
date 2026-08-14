import { clsx } from "clsx";

interface StatusBadgeProps {
  status: string;
  type?: "status" | "source" | "risk";
  size?: "sm" | "md";
}

export default function StatusBadge({ status, type = "status", size = "sm" }: StatusBadgeProps) {
  const norm = (status || "").toUpperCase();

  let colorClasses = "bg-zinc-800/60 text-zinc-400 border-zinc-700/50";
  let dotColor = "bg-zinc-400";

  if (norm === "ACTIVE" || norm === "SUCCESS" || norm === "TRUSTED" || norm === "LOW") {
    colorClasses = "bg-[#B0EB0A]/10 text-[#B0EB0A] border-[#B0EB0A]/30";
    dotColor = "bg-[#B0EB0A]";
  } else if (norm === "DRAFT" || norm === "DRAFT_SAVED" || norm === "PENDING" || norm === "MEDIUM") {
    colorClasses = "bg-amber-500/10 text-amber-400 border-amber-500/30";
    dotColor = "bg-amber-400";
  } else if (norm === "GENERATED" || norm === "AGENT") {
    colorClasses = "bg-purple-500/10 text-purple-400 border-purple-500/30";
    dotColor = "bg-purple-400";
  } else if (norm === "BUILTIN" || norm === "SYSTEM") {
    colorClasses = "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
    dotColor = "bg-cyan-400";
  } else if (norm === "FAILED" || norm === "UNTRUSTED" || norm === "HIGH" || norm === "DEPRECATED") {
    colorClasses = "bg-rose-500/10 text-rose-400 border-rose-500/30";
    dotColor = "bg-rose-400";
  }

  const px = size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs";

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 font-mono font-semibold rounded-md border tracking-wider uppercase",
        colorClasses,
        px
      )}
    >
      <span className={clsx("w-1.5 h-1.5 rounded-full", dotColor)} />
      <span>{norm}</span>
    </span>
  );
}
