"use client";

import { useQuery } from "@tanstack/react-query";
import { getExecutions } from "@/api/client";
import StatusBadge from "@/components/ui/StatusBadge";
import StrategyBadge from "@/components/ui/StrategyBadge";
import { History, ArrowRight, Clock, Terminal } from "lucide-react";
import Link from "next/link";

export default function ExecutionsPage() {
  const { data: executionsData, isLoading } = useQuery({
    queryKey: ["executions", "list"],
    queryFn: () => getExecutions(1, 50),
  });

  const executions = executionsData?.items || [];

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#1F242D] pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-[#B0EB0A]" />
            <h1 className="text-xl font-bold font-mono text-white">Execution History</h1>
          </div>
          <p className="text-xs text-zinc-400 font-sans">
            Audit trail of agent pipeline runs, strategy choices (REUSE vs GENERATE), latencies, and execution outputs.
          </p>
        </div>

        <span className="text-xs font-mono text-zinc-400">
          Total Runs: <span className="text-[#B0EB0A] font-bold">{executions.length}</span>
        </span>
      </div>

      {/* Executions Table */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl overflow-hidden shadow-xl">
        {isLoading ? (
          <div className="p-12 space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-[#171B24] rounded animate-pulse" />
            ))}
          </div>
        ) : executions.length === 0 ? (
          <div className="p-12 text-center space-y-3 font-mono text-xs">
            <History className="w-8 h-8 text-zinc-600 mx-auto" />
            <p className="text-zinc-400">No execution runs recorded yet.</p>
            <Link
              href="/playground"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#B0EB0A] text-black font-semibold"
            >
              <span>Run Task in Playground</span>
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-[#161A22] border-b border-[#1F242D] text-zinc-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-4">Task Input</th>
                  <th className="py-3 px-4">Strategy</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Latency</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F242D]">
                {executions.map((exec) => (
                  <tr key={exec.id} className="hover:bg-[#171B24] transition-colors group">
                    <td className="py-3.5 px-4 max-w-xs truncate text-zinc-200">
                      {exec.input_data?.input || `Task #${exec.task_id.slice(0, 8)}`}
                    </td>
                    <td className="py-3.5 px-4">
                      <StrategyBadge strategy={exec.strategy} />
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={exec.status} />
                    </td>
                    <td className="py-3.5 px-4 text-zinc-400">
                      {exec.latency_ms} ms
                    </td>
                    <td className="py-3.5 px-4 text-zinc-500 text-[11px]">
                      {new Date(exec.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/executions/${exec.id}`}
                        className="inline-flex items-center gap-1 text-[#B0EB0A] hover:underline font-semibold"
                      >
                        <span>View</span>
                        <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
