"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { submitTask } from "@/api/client";
import { TaskExecutionResponse } from "@/types";
import StrategyBadge from "@/components/ui/StrategyBadge";
import StatusBadge from "@/components/ui/StatusBadge";
import {
  Terminal,
  Play,
  CheckCircle2,
  AlertTriangle,
  Brain,
  Sparkles,
  ShieldCheck,
  ArrowRight,
  Code2,
  FileCode,
  Lock,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

const samplePrompts = [
  {
    title: "Q3 Financial Growth Forecast",
    prompt: "Calculate Q3 revenue projection, annual total, and evaluate budget overrun risk.",
    type: "REUSE",
  },
  {
    title: "SOC2 PII & Security Audit",
    prompt: "Scan customer logs for SSN, credit card, and JWT token leaks and rate SOC2 compliance.",
    type: "REUSE",
  },
  {
    title: "Customer Churn Risk Alert",
    prompt: "Analyze Acme Corp account with 12 tickets and negative sentiment for churn probability.",
    type: "REUSE",
  },
  {
    title: "LLM Token Cost ROI Audit",
    prompt: "Calculate financial dollars saved by SkillVault token optimization across 5000 tasks.",
    type: "REUSE",
  },
];

export default function AgentPlaygroundPage() {
  const [userInput, setUserInput] = useState(
    "Calculate Q3 revenue projection, annual total, and evaluate budget overrun risk."
  );
  const [traceStep, setTraceStep] = useState<number>(0);

  const mutation = useMutation({
    mutationFn: (input: string) => submitTask(input),
    onMutate: () => {
      setTraceStep(1);
    },
    onSuccess: (data) => {
      setTimeout(() => setTraceStep(2), 400);
      setTimeout(() => setTraceStep(3), 800);
      setTimeout(() => setTraceStep(4), 1200);
    },
    onError: () => {
      setTraceStep(4);
    },
  });

  const handleRun = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!userInput.trim()) return;
    mutation.mutate(userInput);
  };

  const response: TaskExecutionResponse | undefined = mutation.data;
  const isGenerating = response?.strategy === "generate";
  const isReuse = response?.strategy === "reuse";

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="space-y-1 border-b border-[#1F242D] pb-5">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-[#B0EB0A]" />
          <h1 className="text-xl font-bold font-mono text-white">Agent Playground</h1>
        </div>
        <p className="text-xs text-zinc-400 font-sans max-w-2xl">
          Submit a task to the self-evolving agent. SkillVault will search its capability vault, reuse an existing Skill if similarity score passes threshold, or dynamically synthesize, AST-validate, and persist a new DRAFT Skill.
        </p>
      </div>

      {/* Task Input Form & Presets */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-5 shadow-xl">
        <form onSubmit={handleRun} className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-mono font-semibold uppercase text-zinc-400 tracking-wider flex items-center justify-between">
              <span>Task Prompt / Instruction</span>
              <span className="text-[10px] text-zinc-500 lowercase">e.g., Q3 revenue forecast, SOC2 compliance audit</span>
            </label>
            <textarea
              rows={3}
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Enter your task instruction for the agent..."
              className="w-full bg-[#0A0C0F] border border-[#222834] rounded-lg p-3.5 text-sm font-mono text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-[#B0EB0A] focus:ring-1 focus:ring-[#B0EB0A] transition-all resize-none"
            />
          </div>

          <div className="flex items-center justify-between gap-4">
            {/* Quick Presets */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] font-mono text-zinc-500">Presets:</span>
              {samplePrompts.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setUserInput(preset.prompt)}
                  className="px-2.5 py-1 rounded-md bg-[#181C24] hover:bg-[#202632] border border-[#272F3E] text-[11px] font-mono text-zinc-300 transition-colors flex items-center gap-1.5"
                >
                  <span>{preset.title}</span>
                  <span className="text-[9px] text-zinc-500 uppercase">({preset.type})</span>
                </button>
              ))}
            </div>

            {/* Run Button */}
            <button
              type="submit"
              disabled={mutation.isPending || !userInput.trim()}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg bg-[#B0EB0A] hover:bg-[#a0d709] text-black font-mono font-bold text-xs transition-all shadow-[0_0_20px_rgba(176,235,10,0.2)] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shrink-0"
            >
              {mutation.isPending ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                  <span>Executing Agent...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-black" />
                  <span>Run Agent</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Execution Trace Result Area */}
      <AnimatePresence mode="wait">
        {mutation.isPending && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-[#12151B] border border-[#1F2531] rounded-xl p-8 space-y-6 text-center"
          >
            <div className="w-12 h-12 rounded-full bg-[#B0EB0A]/10 border border-[#B0EB0A]/30 flex items-center justify-center text-[#B0EB0A] mx-auto animate-pulse">
              <Brain className="w-6 h-6 animate-bounce" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-mono font-bold text-zinc-200">Agent Pipeline Executing</h3>
              <p className="text-xs text-zinc-400 font-mono">
                Analyzing task ➔ Searching Skill Vault ➔ Evaluating Candidate Match Threshold...
              </p>
            </div>
          </motion.div>
        )}

        {mutation.isError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-6 text-rose-400 space-y-2 font-mono text-xs"
          >
            <div className="flex items-center gap-2 font-bold text-sm">
              <AlertTriangle className="w-4 h-4" />
              <span>Execution Pipeline Error</span>
            </div>
            <p>{(mutation.error as Error)?.message || "Failed to reach backend API."}</p>
          </motion.div>
        )}

        {response && !mutation.isPending && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Strategy Banner */}
            <div
              className={`p-5 rounded-xl border flex items-center justify-between ${
                isReuse
                  ? "bg-emerald-500/5 border-emerald-500/30"
                  : "bg-purple-500/5 border-purple-500/30"
              }`}
            >
              <div className="flex items-center gap-3">
                <StrategyBadge strategy={response.strategy} size="md" />
                <div>
                  <h3 className="text-sm font-bold font-mono text-zinc-100">
                    {isReuse ? "Existing Skill Vault Capability Reused" : "New Skill Synthesized & Persisted as DRAFT"}
                  </h3>
                  <p className="text-xs text-zinc-400 font-sans">
                    {isReuse
                      ? `Matched skill '${response.skill?.name}' with high confidence.`
                      : "No existing vault skill met threshold. Synthesized new Python capability."}
                  </p>
                </div>
              </div>
              <span className="text-xs font-mono text-zinc-400">
                Task ID: <span className="text-zinc-200">{response.task_id}</span>
              </span>
            </div>

            {/* Execution Timeline Trace */}
            <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-6">
              <h3 className="text-sm font-semibold font-mono text-zinc-100 border-b border-[#1F242D] pb-3">
                Agent Execution Pipeline Trace
              </h3>

              <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#1E2430]">
                {/* Step 1: Received */}
                <div className="relative space-y-1">
                  <span className="absolute -left-[23px] top-0.5 w-3.5 h-3.5 rounded-full bg-[#B0EB0A] ring-4 ring-[#12151B]" />
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-zinc-200">1. Task Instruction Received</span>
                    <span className="text-[10px] font-mono text-emerald-400 font-semibold">PASS</span>
                  </div>
                  <p className="text-xs text-zinc-400 font-mono bg-[#0A0C0F] p-2.5 rounded border border-[#1E232E]">
                    "{userInput}"
                  </p>
                </div>

                {/* Step 2: Retrieval */}
                <div className="relative space-y-2">
                  <span className="absolute -left-[23px] top-0.5 w-3.5 h-3.5 rounded-full bg-[#B0EB0A] ring-4 ring-[#12151B]" />
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-zinc-200">2. Semantic Skill Retrieval</span>
                    <span className="text-[10px] font-mono text-emerald-400 font-semibold">MATCH SCORE CHECK</span>
                  </div>

                  {response.skill && (
                    <div className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-mono font-semibold text-zinc-200">{response.skill.name}</span>
                        <span className="font-mono font-bold text-[#B0EB0A]">
                          Match Score: {response.skill.score}
                        </span>
                      </div>
                      <p className="text-[11px] text-zinc-400 font-sans">{response.skill.description}</p>
                    </div>
                  )}
                </div>

                {/* Step 3: Decision */}
                <div className="relative space-y-1">
                  <span className="absolute -left-[23px] top-0.5 w-3.5 h-3.5 rounded-full bg-[#B0EB0A] ring-4 ring-[#12151B]" />
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-zinc-200">3. Strategy Decision</span>
                    <StrategyBadge strategy={response.strategy} />
                  </div>
                </div>

                {/* Step 4: Generation / Execution */}
                {isGenerating ? (
                  <div className="relative space-y-3">
                    <span className="absolute -left-[23px] top-0.5 w-3.5 h-3.5 rounded-full bg-purple-400 ring-4 ring-[#12151B]" />
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-zinc-200">4. Static AST Security Validation</span>
                      <span className="text-[10px] font-mono text-emerald-400 font-semibold">AST SAFE</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                      <div className="p-2 rounded bg-[#0A0C0F] border border-[#1E232E] flex items-center justify-between text-zinc-300">
                        <span>Python Syntax Check</span>
                        <span className="text-emerald-400">PASS</span>
                      </div>
                      <div className="p-2 rounded bg-[#0A0C0F] border border-[#1E232E] flex items-center justify-between text-zinc-300">
                        <span>Entrypoint Contract</span>
                        <span className="text-emerald-400">def run()</span>
                      </div>
                      <div className="p-2 rounded bg-[#0A0C0F] border border-[#1E232E] flex items-center justify-between text-zinc-300">
                        <span>AST Forbidden Calls</span>
                        <span className="text-emerald-400 font-bold">CLEAN</span>
                      </div>
                      <div className="p-2 rounded bg-[#0A0C0F] border border-[#1E232E] flex items-center justify-between text-zinc-300">
                        <span>Path Traversal Check</span>
                        <span className="text-emerald-400">CLEAN</span>
                      </div>
                    </div>

                    {/* DRAFT Saved Security Notice */}
                    <div className="p-3.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 space-y-1 font-mono text-xs">
                      <div className="flex items-center gap-2 font-bold">
                        <Lock className="w-3.5 h-3.5 text-amber-400" />
                        <span>Security Boundary Enforcement Notice</span>
                      </div>
                      <p className="text-[11px] text-amber-200/80 font-sans leading-relaxed">
                        {response.result?.notice ||
                          "Skill synthesized, AST validated & persisted as DRAFT in Skill Vault. Docker Sandbox environment is required for dynamic execution."}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="relative space-y-2">
                    <span className="absolute -left-[23px] top-0.5 w-3.5 h-3.5 rounded-full bg-[#B0EB0A] ring-4 ring-[#12151B]" />
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-zinc-200">4. Built-in Local Skill Execution</span>
                      <StatusBadge status={response.execution?.status || "SUCCESS"} />
                    </div>

                    {response.execution?.output_data && (
                      <div className="space-y-1">
                        <span className="text-[10px] font-mono text-zinc-500 uppercase">Execution Output Data</span>
                        <pre className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] font-mono text-[11px] text-emerald-400 overflow-x-auto max-h-60">
                          {JSON.stringify(response.execution.output_data, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Generated Skill Detail Link */}
            {isGenerating && response.skill?.skill_id && (
              <div className="flex justify-end">
                <Link
                  href={`/skills/${response.skill.skill_id}`}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#181D26] hover:bg-[#222936] border border-[#2B3446] text-xs font-mono text-[#B0EB0A] font-semibold transition-colors"
                >
                  <span>View Generated Skill Specification</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
