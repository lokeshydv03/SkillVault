"use client";

import { useQuery } from "@tanstack/react-query";
import { getExecutions, getTasks } from "@/api/client";
import StrategyBadge from "@/components/ui/StrategyBadge";
import StatusBadge from "@/components/ui/StatusBadge";
import { Activity, Terminal, Brain, Sparkles, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function ActivityPage() {
  const { data: executionsData, isLoading } = useQuery({
    queryKey: ["activity-executions"],
    queryFn: () => getExecutions(1, 30),
    refetchInterval: 5000,
  });

  const executions = executionsData?.items || [];

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      <div className="flex items-center justify-between border-b border-[#1F242D] pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-[#B0EB0A]" />
            <h1 className="text-xl font-bold font-mono text-white">Agent Activity Observability Stream</h1>
          </div>
          <p className="text-xs text-zinc-400 font-sans">
            Real-time observational telemetry of agent pipeline runs, strategy choices, and vault state changes.
          </p>
        </div>

        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#131720] border border-[#1E2430] text-[11px] font-mono text-zinc-400">
          <span className="w-2 h-2 rounded-full bg-[#B0EB0A] animate-pulse" />
          <span>Live Stream Active</span>
        </div>
      </div>

      {/* Stream List */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-4">
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-[#171B24] rounded animate-pulse" />
            ))}
          </div>
        ) : executions.length === 0 ? (
          <div className="p-12 text-center space-y-3 font-mono text-xs text-zinc-400">
            <Activity className="w-8 h-8 text-zinc-600 mx-auto" />
            <p>No real-time event activity recorded yet.</p>
            <Link
              href="/playground"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#B0EB0A] text-black font-semibold"
            >
              <span>Run Task in Playground</span>
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {executions.map((exec) => (
              <div
                key={exec.id}
                className="p-4 rounded-lg bg-[#161A22] border border-[#222834] flex flex-col sm:flex-row sm:items-center justify-between gap-4 font-mono text-xs hover:border-[#2D3647] transition-colors"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-3">
                    <span className="text-[11px] text-zinc-500 font-semibold">
                      {new Date(exec.created_at).toLocaleTimeString()}
                    </span>
                    <StrategyBadge strategy={exec.strategy} />
                    <StatusBadge status={exec.status} />
                  </div>
                  <p className="text-zinc-200 font-medium">
                    {exec.input_data?.input || `Task Event Run #${exec.id.slice(0, 8)}`}
                  </p>
                </div>

                <div className="flex items-center gap-4 text-right">
                  <div className="text-[11px] text-zinc-400">
                    <span>Latency: {exec.latency_ms}ms</span>
                  </div>
                  <Link
                    href={`/executions/${exec.id}`}
                    className="px-3 py-1 rounded bg-[#202734] hover:bg-[#2A3446] text-[#B0EB0A] text-[11px] font-semibold transition-colors"
                  >
                    View Trace
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
