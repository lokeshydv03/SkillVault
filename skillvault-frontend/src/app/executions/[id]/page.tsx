"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { getExecutionById } from "@/api/client";
import StatusBadge from "@/components/ui/StatusBadge";
import StrategyBadge from "@/components/ui/StrategyBadge";
import { History, ArrowLeft, Clock, Code2, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function ExecutionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id: executionId } = use(params);

  const { data: execution, isLoading } = useQuery({
    queryKey: ["execution", executionId],
    queryFn: () => getExecutionById(executionId),
  });

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="h-32 bg-[#12151B] border border-[#1F2531] rounded-xl animate-pulse" />
        <div className="h-64 bg-[#12151B] border border-[#1F2531] rounded-xl animate-pulse" />
      </div>
    );
  }

  if (!execution) {
    return (
      <div className="max-w-4xl mx-auto p-12 bg-[#12151B] border border-[#1F2531] rounded-xl text-center space-y-4 font-mono text-xs">
        <p className="text-zinc-400">Execution record '{executionId}' not found.</p>
        <Link href="/executions" className="text-[#B0EB0A] hover:underline">
          ← Return to Executions
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      <Link
        href="/executions"
        className="inline-flex items-center gap-2 text-xs font-mono text-zinc-400 hover:text-[#B0EB0A] transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Executions</span>
      </Link>

      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-[#1F242D] pb-4">
          <div className="space-y-1">
            <h1 className="text-lg font-bold font-mono text-white">
              Execution Log #{execution.id.slice(0, 8)}
            </h1>
            <p className="text-xs font-mono text-zinc-500">Task ID: {execution.task_id}</p>
          </div>
          <div className="flex items-center gap-2">
            <StrategyBadge strategy={execution.strategy} size="md" />
            <StatusBadge status={execution.status} size="md" />
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 font-mono text-xs pt-2">
          <div className="p-3 rounded bg-[#161B24] border border-[#222835]">
            <span className="text-zinc-500 text-[10px] uppercase">Latency</span>
            <div className="text-base font-bold text-cyan-400">{execution.latency_ms} ms</div>
          </div>
          <div className="p-3 rounded bg-[#161B24] border border-[#222835]">
            <span className="text-zinc-500 text-[10px] uppercase">Score</span>
            <div className="text-base font-bold text-[#B0EB0A]">
              {execution.retrieval_score || "1.00"}
            </div>
          </div>
          <div className="p-3 rounded bg-[#161B24] border border-[#222835]">
            <span className="text-zinc-500 text-[10px] uppercase">Executed At</span>
            <div className="text-xs font-bold text-zinc-200 pt-1">
              {new Date(execution.created_at).toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>

      {/* Input Data */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-3 font-mono text-xs">
        <h3 className="font-bold text-zinc-300 uppercase tracking-wider text-[11px]">
          Input Payload Data
        </h3>
        <pre className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] text-zinc-200 overflow-x-auto max-h-48">
          {JSON.stringify(execution.input_data, null, 2)}
        </pre>
      </div>

      {/* Output Data */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-3 font-mono text-xs">
        <h3 className="font-bold text-zinc-300 uppercase tracking-wider text-[11px]">
          Output Result Payload
        </h3>
        <pre className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] text-emerald-400 overflow-x-auto max-h-64">
          {JSON.stringify(execution.output_data || { notice: "No output data returned" }, null, 2)}
        </pre>
      </div>
    </div>
  );
}
