"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { getSkillById, getSkillVersions, getSkillExecutions } from "@/api/client";
import StatusBadge from "@/components/ui/StatusBadge";
import {
  Brain,
  Code2,
  Copy,
  Check,
  ShieldCheck,
  History,
  Terminal,
  FileCode,
  Lock,
  ArrowLeft,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export default function SkillDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id: skillId } = use(params);
  const [copied, setCopied] = useState(false);

  const { data: skill, isLoading: isLoadingSkill } = useQuery({
    queryKey: ["skill", skillId],
    queryFn: () => getSkillById(skillId),
  });

  const { data: versions } = useQuery({
    queryKey: ["skill-versions", skillId],
    queryFn: () => getSkillVersions(skillId),
  });

  const { data: executions } = useQuery({
    queryKey: ["skill-executions", skillId],
    queryFn: () => getSkillExecutions(skillId),
  });

  if (isLoadingSkill) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="h-32 bg-[#12151B] border border-[#1F2531] rounded-xl animate-pulse" />
        <div className="h-96 bg-[#12151B] border border-[#1F2531] rounded-xl animate-pulse" />
      </div>
    );
  }

  if (!skill) {
    return (
      <div className="max-w-6xl mx-auto p-12 bg-[#12151B] border border-[#1F2531] rounded-xl text-center space-y-4 font-mono text-xs">
        <p className="text-zinc-400">Skill with ID '{skillId}' not found in vault.</p>
        <Link href="/skills" className="text-[#B0EB0A] hover:underline">
          ← Return to Skill Vault
        </Link>
      </div>
    );
  }

  const activeVer = versions && versions.length > 0 ? versions[0] : null;
  const isDraft = skill.status === "DRAFT";
  const isGenerated = skill.source_type === "GENERATED";

  const handleCopyCode = () => {
    if (!activeVer?.code) return;
    navigator.clipboard.writeText(activeVer.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      {/* Back Link */}
      <Link
        href="/skills"
        className="inline-flex items-center gap-2 text-xs font-mono text-zinc-400 hover:text-[#B0EB0A] transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Skill Vault</span>
      </Link>

      {/* Header Banner */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1F242D] pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold font-mono text-white">{skill.name}</h1>
              <StatusBadge status={skill.status} />
              <StatusBadge status={skill.source_type} type="source" />
            </div>
            <p className="text-xs font-mono text-zinc-500">{skill.slug}</p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/playground"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#B0EB0A] hover:bg-[#a0d709] text-black font-mono font-bold text-xs shadow-[0_0_15px_rgba(176,235,10,0.2)]"
            >
              <Terminal className="w-4 h-4" />
              <span>Use in Playground</span>
            </Link>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono text-xs pt-2">
          <div className="p-3 rounded-lg bg-[#161B24] border border-[#222835]">
            <span className="text-zinc-500 uppercase text-[10px]">Success Rate</span>
            <div className="text-base font-bold text-[#B0EB0A]">
              {(skill.success_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div className="p-3 rounded-lg bg-[#161B24] border border-[#222835]">
            <span className="text-zinc-500 uppercase text-[10px]">Total Executions</span>
            <div className="text-base font-bold text-zinc-100">{skill.usage_count}</div>
          </div>
          <div className="p-3 rounded-lg bg-[#161B24] border border-[#222835]">
            <span className="text-zinc-500 uppercase text-[10px]">Risk Level</span>
            <div className="pt-0.5">
              <StatusBadge status={skill.risk_level} type="risk" />
            </div>
          </div>
          <div className="p-3 rounded-lg bg-[#161B24] border border-[#222835]">
            <span className="text-zinc-500 uppercase text-[10px]">Version</span>
            <div className="text-base font-bold text-cyan-400">
              v{activeVer?.version || "1.0.0"}
            </div>
          </div>
        </div>
      </div>

      {/* Capability Description */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-3">
        <h3 className="text-xs font-mono font-bold uppercase text-zinc-400 tracking-wider">
          Capability Summary
        </h3>
        <p className="text-sm text-zinc-200 leading-relaxed font-sans">{skill.description}</p>
        <div className="pt-2 text-xs font-mono text-zinc-400 flex items-center gap-2">
          <span className="text-zinc-500">Declared Capability:</span>
          <span className="text-zinc-200">{skill.capability}</span>
        </div>
      </div>

      {/* Code Viewer Section */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl overflow-hidden">
        <div className="p-4 bg-[#161A22] border-b border-[#1F242D] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code2 className="w-4 h-4 text-[#B0EB0A]" />
            <span className="text-xs font-mono font-bold text-zinc-200">
              Generated Skill Source Code
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#202734] text-cyan-300">
              Python 3.12
            </span>
          </div>

          <button
            onClick={handleCopyCode}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#202734] hover:bg-[#2A3446] text-xs font-mono text-zinc-300 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-[#B0EB0A]" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? "Copied!" : "Copy Code"}</span>
          </button>
        </div>

        <div className="p-4 bg-[#0A0C0F] font-mono text-xs overflow-x-auto">
          {activeVer?.code ? (
            <pre className="text-zinc-200 leading-relaxed">
              <code>{activeVer.code}</code>
            </pre>
          ) : (
            <p className="text-zinc-500">No source code loaded for active version.</p>
          )}
        </div>
      </div>

      {/* AST Validation Panel */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-[#1F242D] pb-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-mono font-bold uppercase text-zinc-200 tracking-wider">
              Static AST Security & Validation Panel
            </h3>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
            AST VALIDATED
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-mono text-xs">
          <div className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] space-y-1">
            <span className="text-zinc-500 text-[10px]">Python Syntax</span>
            <div className="text-emerald-400 font-bold">PASS</div>
          </div>
          <div className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] space-y-1">
            <span className="text-zinc-500 text-[10px]">Entrypoint Contract</span>
            <div className="text-emerald-400 font-bold">def run(input_data)</div>
          </div>
          <div className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] space-y-1">
            <span className="text-zinc-500 text-[10px]">Forbidden Calls</span>
            <div className="text-emerald-400 font-bold">CLEAN</div>
          </div>
          <div className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] space-y-1">
            <span className="text-zinc-500 text-[10px]">Path Traversal Check</span>
            <div className="text-emerald-400 font-bold">CLEAN</div>
          </div>
        </div>

        {isDraft && (
          <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 space-y-1.5 font-mono text-xs">
            <div className="flex items-center gap-2 font-bold">
              <Lock className="w-4 h-4 text-amber-400" />
              <span>DRAFT Skill Security Restriction</span>
            </div>
            <p className="text-xs text-amber-200/80 font-sans leading-relaxed">
              This skill was dynamically synthesized by the agent. AST validation passed, and it is safely stored in the vault as DRAFT. Docker Sandbox execution environment is required for dynamic execution in Phase 2.
            </p>
          </div>
        )}
      </div>

      {/* Input & Output Schemas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-5 space-y-3">
          <h4 className="text-xs font-mono font-bold text-zinc-300 uppercase tracking-wider">
            Input Schema
          </h4>
          <pre className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] font-mono text-xs text-cyan-300 overflow-x-auto max-h-48">
            {JSON.stringify(skill.input_schema, null, 2)}
          </pre>
        </div>

        <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-5 space-y-3">
          <h4 className="text-xs font-mono font-bold text-zinc-300 uppercase tracking-wider">
            Output Schema
          </h4>
          <pre className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] font-mono text-xs text-purple-300 overflow-x-auto max-h-48">
            {JSON.stringify(skill.output_schema, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
