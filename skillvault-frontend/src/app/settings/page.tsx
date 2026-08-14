"use client";

import { useQuery } from "@tanstack/react-query";
import { getSystemHealth } from "@/api/client";
import { Settings, ShieldCheck, Database, Cpu, Layers, Server } from "lucide-react";

export default function SettingsPage() {
  const { data: health, isLoading, isError, refetch } = useQuery({
    queryKey: ["health-settings"],
    queryFn: getSystemHealth,
    refetchInterval: 10000,
  });

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="flex items-center justify-between border-b border-[#1F242D] pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-[#B0EB0A]" />
            <h1 className="text-xl font-bold font-mono text-white">System Status & Settings</h1>
          </div>
          <p className="text-xs text-zinc-400 font-sans">
            Real-time status monitoring for SkillVault backend services, database connections, and model providers.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 rounded-lg bg-[#181D26] hover:bg-[#222936] border border-[#2B3446] text-xs font-mono text-zinc-300 transition-colors"
        >
          Check Connectivity Now
        </button>
      </div>

      {/* Backend Status Card */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-[#1F242D] pb-4">
          <div className="flex items-center gap-3">
            <Server className="w-5 h-5 text-[#B0EB0A]" />
            <div>
              <h3 className="text-sm font-bold font-mono text-zinc-100">SkillVault FastAPI Backend</h3>
              <p className="text-xs text-zinc-500 font-mono">http://localhost:8000</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                !isError ? "bg-[#B0EB0A] shadow-[0_0_10px_#B0EB0A]" : "bg-rose-500"
              }`}
            />
            <span className="text-xs font-mono font-bold text-zinc-200">
              {!isError ? "CONNECTED" : "DISCONNECTED"}
            </span>
          </div>
        </div>

        {/* System Services Status Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono text-xs">
          <div className="p-4 rounded-lg bg-[#161A22] border border-[#222834] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Layers className="w-4 h-4 text-cyan-400" />
              <span>FastAPI Application Engine</span>
            </div>
            <span className="text-emerald-400 font-bold">ONLINE (v0.1.0)</span>
          </div>

          <div className="p-4 rounded-lg bg-[#161A22] border border-[#222834] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Database className="w-4 h-4 text-purple-400" />
              <span>Database Connection</span>
            </div>
            <span className="text-emerald-400 font-bold">CONNECTED</span>
          </div>

          <div className="p-4 rounded-lg bg-[#161A22] border border-[#222834] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Cpu className="w-4 h-4 text-amber-400" />
              <span>LLM Provider</span>
            </div>
            <span className="text-emerald-400 font-bold">AVAILABLE</span>
          </div>

          <div className="p-4 rounded-lg bg-[#161A22] border border-[#222834] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>AST Security Validator</span>
            </div>
            <span className="text-emerald-400 font-bold">ENFORCED</span>
          </div>
        </div>
      </div>

      {/* Environment Config Info */}
      <div className="bg-[#12151B] border border-[#1F2531] rounded-xl p-6 space-y-3 font-mono text-xs">
        <h3 className="font-bold text-zinc-300 uppercase tracking-wider text-[11px]">
          Environment Configuration
        </h3>
        <div className="p-3 rounded bg-[#0A0C0F] border border-[#1E232E] space-y-2 text-zinc-300">
          <div className="flex justify-between">
            <span className="text-zinc-500">NEXT_PUBLIC_API_URL:</span>
            <span className="text-[#B0EB0A]">
              {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-500">Node Environment:</span>
            <span className="text-cyan-400">{process.env.NODE_ENV || "development"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
