import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  accentColor?: string;
}

export default function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  accentColor = "text-[#B0EB0A]",
}: MetricCardProps) {
  return (
    <div className="bg-[#12151C] border border-[#1F2531] rounded-xl p-5 hover:border-[#2E3647] transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-zinc-400">
          {title}
        </span>
        <div className={`p-2 rounded-lg bg-[#191F2B] border border-[#273042] ${accentColor}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="text-2xl font-bold font-mono text-zinc-100 mb-1">{value}</div>
      {subtitle && <p className="text-[11px] text-zinc-500 font-mono">{subtitle}</p>}
    </div>
  );
}
