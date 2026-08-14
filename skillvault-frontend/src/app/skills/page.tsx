"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getSkills, searchSkills } from "@/api/client";
import StatusBadge from "@/components/ui/StatusBadge";
import { Brain, Search, Sparkles, Filter, Code2, ArrowRight } from "lucide-react";
import Link from "next/link";
import { clsx } from "clsx";

export default function SkillsExplorerPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [useSemanticSearch, setUseSemanticSearch] = useState(false);

  const { data: skillsData, isLoading } = useQuery({
    queryKey: ["skills", statusFilter, searchTerm, useSemanticSearch],
    queryFn: async () => {
      if (useSemanticSearch && searchTerm.trim()) {
        const results = await searchSkills(searchTerm, 10);
        return { items: results, total: results.length };
      }
      return getSkills({
        status: statusFilter === "ALL" ? undefined : statusFilter,
        name: !useSemanticSearch && searchTerm ? searchTerm : undefined,
        limit: 100,
      });
    },
  });

  const skills = (skillsData as any)?.items || [];

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1F242D] pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-[#B0EB0A]" />
            <h1 className="text-xl font-bold font-mono text-white">Skill Vault Library</h1>
          </div>
          <p className="text-xs text-zinc-400 font-sans">
            Searchable capability repository. Explore trusted built-in skills and agent-synthesized capabilities.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-zinc-400">
            Total Capabilities: <span className="text-[#B0EB0A] font-bold">{skills.length}</span>
          </span>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-4 space-y-4">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-zinc-500 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder={
                useSemanticSearch
                  ? "Enter semantic query (e.g., 'analyze employee salaries')..."
                  : "Filter skills by name..."
              }
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#0A0C0F] border border-[#222834] rounded-lg pl-10 pr-4 py-2.5 text-xs font-mono text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-[#B0EB0A] transition-colors"
            />
          </div>

          <button
            type="button"
            onClick={() => setUseSemanticSearch(!useSemanticSearch)}
            className={clsx(
              "flex items-center gap-2 px-3 py-2.5 rounded-lg border text-xs font-mono font-medium transition-colors shrink-0",
              useSemanticSearch
                ? "bg-[#B0EB0A]/10 border-[#B0EB0A] text-[#B0EB0A]"
                : "bg-[#161A22] border-[#222834] text-zinc-400 hover:text-zinc-200"
            )}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Semantic Vector Search</span>
          </button>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1">
          <span className="text-[11px] font-mono text-zinc-500 mr-2 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Filter:
          </span>
          {["ALL", "ACTIVE", "DRAFT", "BUILTIN", "GENERATED"].map((filter) => (
            <button
              key={filter}
              onClick={() => setStatusFilter(filter)}
              className={clsx(
                "px-3 py-1 rounded-md text-[11px] font-mono font-semibold uppercase tracking-wider transition-all",
                statusFilter === filter
                  ? "bg-[#B0EB0A] text-black"
                  : "bg-[#161A22] text-zinc-400 hover:bg-[#1E2430] hover:text-zinc-200 border border-[#222834]"
              )}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Skill Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-48 bg-[#12151B] border border-[#1F2531] rounded-xl animate-pulse" />
          ))}
        </div>
      ) : skills.length === 0 ? (
        <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-12 text-center space-y-4">
          <Brain className="w-10 h-10 text-zinc-600 mx-auto" />
          <div className="space-y-1">
            <h3 className="text-sm font-mono font-bold text-zinc-200">No Matching Capabilities Found</h3>
            <p className="text-xs text-zinc-500 font-sans max-w-md mx-auto">
              Give SkillVault a task in the Agent Playground and let the agent synthesize its first capability.
            </p>
          </div>
          <Link
            href="/playground"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#B0EB0A] text-black font-mono font-bold text-xs"
          >
            <span>Open Agent Playground</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {skills.map((skill: any) => {
            const isSearchResult = "score" in skill;
            const skillId = skill.id || skill.skill_id;

            return (
              <div
                key={skillId}
                className="bg-[#12151B] border border-[#1F2531] rounded-xl p-5 hover:border-[#2E374A] transition-all flex flex-col justify-between group space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="space-y-1">
                      <Link
                        href={`/skills/${skillId}`}
                        className="font-mono font-bold text-sm text-zinc-100 group-hover:text-[#B0EB0A] transition-colors line-clamp-1"
                      >
                        {skill.name}
                      </Link>
                      <p className="text-[10px] font-mono text-zinc-500">{skill.slug}</p>
                    </div>
                    <StatusBadge status={skill.status || "ACTIVE"} />
                  </div>

                  <p className="text-xs text-zinc-400 font-sans line-clamp-2 leading-relaxed">
                    {skill.description}
                  </p>

                  <div className="flex items-center gap-2 pt-1">
                    <StatusBadge status={skill.source_type || "BUILTIN"} type="source" />
                    {isSearchResult && (
                      <span className="text-[10px] font-mono font-bold text-[#B0EB0A] bg-[#B0EB0A]/10 border border-[#B0EB0A]/30 px-2 py-0.5 rounded">
                        Score: {skill.score}
                      </span>
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t border-[#1F242D] flex items-center justify-between text-[11px] font-mono text-zinc-400">
                  <div className="flex items-center gap-3">
                    <span>Executions: {skill.usage_count || 0}</span>
                    <span>•</span>
                    <span>
                      Success: {skill.success_rate ? `${(skill.success_rate * 100).toFixed(0)}%` : "100%"}
                    </span>
                  </div>
                  <Link
                    href={`/skills/${skillId}`}
                    className="text-[#B0EB0A] hover:underline flex items-center gap-1 font-semibold"
                  >
                    <span>Details</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
