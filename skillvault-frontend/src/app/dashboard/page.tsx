"use client";

import { useQuery } from "@tanstack/react-query";
import { getSkills, getExecutions, getTasks } from "@/api/client";
import MetricCard from "@/components/dashboard/MetricCard";
import StatusBadge from "@/components/ui/StatusBadge";
import StrategyBadge from "@/components/ui/StrategyBadge";
import { Brain, CheckCircle2, History, Sparkles, Terminal, Activity, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { data: skillsData, isLoading: isLoadingSkills } = useQuery({
    queryKey: ["skills", "all"],
    queryFn: () => getSkills({ limit: 100 }),
  });

  const { data: executionsData, isLoading: isLoadingExecs } = useQuery({
    queryKey: ["executions", "all"],
    queryFn: () => getExecutions(1, 20),
  });

  const { data: tasksData } = useQuery({
    queryKey: ["tasks", "all"],
    queryFn: () => getTasks(1, 10),
  });

  const skills = skillsData?.items || [];
  const executions = executionsData?.items || [];

  const totalSkills = skills.length;
  const activeSkills = skills.filter((s) => s.status === "ACTIVE").length;
  const draftSkills = skills.filter((s) => s.status === "DRAFT").length;
  const totalExecutions = executionsData?.total || 0;

  const successfulExecs = executions.filter((e) => e.status === "SUCCESS" || e.status === "DRAFT_SAVED").length;
  const successRate = totalExecutions > 0 ? ((successfulExecs / totalExecutions) * 100).toFixed(1) : "100";

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#12151B] border border-[#1F2531] rounded-2xl p-6 relative overflow-hidden">
        <div className="space-y-1.5 z-10">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#B0EB0A]" />
            <span className="text-xs font-mono font-semibold uppercase tracking-wider text-[#B0EB0A]">
              Self-Evolving Capability Memory
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-mono">SkillVault Infrastructure</h1>
          <p className="text-xs text-zinc-400 max-w-2xl leading-relaxed">
            Persistent AI capability repository. When your agent encounters a task, it searches its vault for an existing reusable Skill, or synthesizes, AST-validates, and stores a new capability.
          </p>
        </div>
        <div className="flex items-center gap-3 z-10">
          <Link
            href="/playground"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#B0EB0A] hover:bg-[#a0d709] text-black font-semibold text-xs transition-colors shadow-[0_0_20px_rgba(176,235,10,0.2)]"
          >
            <Terminal className="w-4 h-4" />
            <span>Open Agent Playground</span>
          </Link>
        </div>
        {/* Background glow */}
        <div className="absolute right-0 top-0 w-96 h-96 bg-[#B0EB0A]/5 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Total Skills"
          value={isLoadingSkills ? "..." : totalSkills}
          subtitle="Persistent Vault Capabilities"
          icon={Brain}
        />
        <MetricCard
          title="Active Skills"
          value={isLoadingSkills ? "..." : activeSkills}
          subtitle="Production Ready"
          icon={CheckCircle2}
          accentColor="text-emerald-400"
        />
        <MetricCard
          title="Draft Skills"
          value={isLoadingSkills ? "..." : draftSkills}
          subtitle="Synthesized & Validated"
          icon={Sparkles}
          accentColor="text-amber-400"
        />
        <MetricCard
          title="Total Executions"
          value={isLoadingExecs ? "..." : totalExecutions}
          subtitle="Task Pipeline Runs"
          icon={History}
          accentColor="text-cyan-400"
        />
        <MetricCard
          title="Success Rate"
          value={`${successRate}%`}
          subtitle="Pipeline Execution Rate"
          icon={Activity}
          accentColor="text-purple-400"
        />
      </div>

      {/* Main Grid Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Skill Status Distribution */}
        <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-[#1F242D] pb-4">
            <h3 className="text-sm font-semibold font-mono text-zinc-100">Skill Vault Breakdown</h3>
            <Link href="/skills" className="text-xs text-[#B0EB0A] hover:underline font-mono">
              View All →
            </Link>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-[#171B24] border border-[#222835]">
              <div className="flex items-center gap-3">
                <StatusBadge status="ACTIVE" />
                <span className="text-xs font-medium text-zinc-300">Production Active</span>
              </div>
              <span className="font-mono text-sm font-bold text-zinc-100">{activeSkills}</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-[#171B24] border border-[#222835]">
              <div className="flex items-center gap-3">
                <StatusBadge status="DRAFT" />
                <span className="text-xs font-medium text-zinc-300">Generated Drafts</span>
              </div>
              <span className="font-mono text-sm font-bold text-zinc-100">{draftSkills}</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-[#171B24] border border-[#222835]">
              <div className="flex items-center gap-3">
                <StatusBadge status="BUILTIN" type="source" />
                <span className="text-xs font-medium text-zinc-300">Trusted Built-ins</span>
              </div>
              <span className="font-mono text-sm font-bold text-zinc-100">
                {skills.filter((s) => s.source_type === "BUILTIN").length}
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-[#171B24] border border-[#222835]">
              <div className="flex items-center gap-3">
                <StatusBadge status="GENERATED" type="source" />
                <span className="text-xs font-medium text-zinc-300">Agent Synthesized</span>
              </div>
              <span className="font-mono text-sm font-bold text-zinc-100">
                {skills.filter((s) => s.source_type === "GENERATED").length}
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Recent Activity Feed */}
        <div className="lg:col-span-2 bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-[#1F242D] pb-4">
            <h3 className="text-sm font-semibold font-mono text-zinc-100">Recent Agent Activity</h3>
            <Link href="/activity" className="text-xs text-[#B0EB0A] hover:underline font-mono">
              View Activity Stream →
            </Link>
          </div>

          <div className="space-y-3">
            {executions.length === 0 ? (
              <div className="p-8 text-center border border-dashed border-[#222835] rounded-xl space-y-3">
                <Brain className="w-8 h-8 text-zinc-600 mx-auto" />
                <p className="text-xs text-zinc-400 font-mono">No execution runs recorded yet.</p>
                <Link
                  href="/playground"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#B0EB0A] text-black text-xs font-semibold"
                >
                  <span>Run First Task in Playground</span>
                </Link>
              </div>
            ) : (
              executions.slice(0, 5).map((exec) => (
                <Link
                  key={exec.id}
                  href={`/executions/${exec.id}`}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 rounded-lg bg-[#171B24] border border-[#222835] hover:border-[#2F374A] transition-colors gap-3 group"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <StrategyBadge strategy={exec.strategy} />
                      <span className="text-xs font-mono font-medium text-zinc-200 group-hover:text-[#B0EB0A] transition-colors truncate max-w-md">
                        {exec.input_data?.input || `Task Execution #${exec.id.slice(0, 8)}`}
                      </span>
                    </div>
                    <div className="text-[11px] text-zinc-500 font-mono flex items-center gap-3">
                      <span>Latency: {exec.latency_ms}ms</span>
                      <span>•</span>
                      <span>{new Date(exec.created_at).toLocaleTimeString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={exec.status} />
                    <ArrowRight className="w-4 h-4 text-zinc-600 group-hover:text-[#B0EB0A] transition-transform group-hover:translate-x-0.5" />
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
