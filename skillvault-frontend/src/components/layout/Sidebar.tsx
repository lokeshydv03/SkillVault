"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getSystemHealth } from "@/api/client";
import {
  LayoutDashboard,
  Terminal,
  Brain,
  History,
  Activity,
  Settings,
} from "lucide-react";
import { clsx } from "clsx";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Agent Playground", href: "/playground", icon: Terminal },
  { name: "Skills Vault", href: "/skills", icon: Brain },
  { name: "Executions", href: "/executions", icon: History },
  { name: "Activity", href: "/activity", icon: Activity },
];

export default function Sidebar() {
  const pathname = usePathname();

  const { data: health, isSuccess } = useQuery({
    queryKey: ["health"],
    queryFn: getSystemHealth,
    refetchInterval: 15000,
  });

  return (
    <aside className="w-64 bg-[#0F1115] border-r border-[#1F242D] flex flex-col h-screen sticky top-0 select-none z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#1F242D] flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-[#B0EB0A]/10 border border-[#B0EB0A]/30 flex items-center justify-center text-[#B0EB0A] shadow-[0_0_15px_rgba(176,235,10,0.15)] group-hover:scale-105 transition-transform">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-white tracking-wide text-base group-hover:text-[#B0EB0A] transition-colors">
              SkillVault
            </h1>
            <p className="text-[10px] text-zinc-500 font-mono tracking-wider">AI AGENT MEMORY v0.1.0</p>
          </div>
        </Link>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 mb-2 text-[10px] font-semibold text-zinc-500 uppercase tracking-wider font-mono">
          Core Platform
        </div>
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-md text-xs font-medium transition-all duration-150 group",
                isActive
                  ? "bg-[#181C23] text-[#B0EB0A] border-l-2 border-[#B0EB0A] font-semibold"
                  : "text-zinc-400 hover:text-zinc-100 hover:bg-[#141820]"
              )}
            >
              <Icon
                className={clsx(
                  "w-4 h-4 transition-colors",
                  isActive ? "text-[#B0EB0A]" : "text-zinc-400 group-hover:text-zinc-200"
                )}
              />
              <span>{item.name}</span>
            </Link>
          );
        })}

        <div className="pt-6 px-3 mb-2 text-[10px] font-semibold text-zinc-500 uppercase tracking-wider font-mono">
          System & Config
        </div>
        <Link
          href="/settings"
          className={clsx(
            "flex items-center gap-3 px-3 py-2.5 rounded-md text-xs font-medium transition-all duration-150 group",
            pathname === "/settings"
              ? "bg-[#181C23] text-[#B0EB0A] border-l-2 border-[#B0EB0A] font-semibold"
              : "text-zinc-400 hover:text-zinc-100 hover:bg-[#141820]"
          )}
        >
          <Settings className="w-4 h-4 text-zinc-400 group-hover:text-zinc-200" />
          <span>System Status</span>
        </Link>
      </nav>

      {/* Backend Status Indicator */}
      <div className="p-3 border-t border-[#1F242D] bg-[#0B0D10]">
        <div className="flex items-center justify-between px-3 py-2 rounded-md bg-[#13161C] border border-[#1E232E]">
          <div className="flex items-center gap-2">
            <span
              className={clsx(
                "w-2 h-2 rounded-full animate-pulse",
                isSuccess ? "bg-[#B0EB0A] shadow-[0_0_8px_#B0EB0A]" : "bg-amber-500"
              )}
            />
            <span className="text-[11px] font-mono font-medium text-zinc-300">
              {isSuccess ? "API Connected" : "Connecting..."}
            </span>
          </div>
          <span className="text-[10px] font-mono text-zinc-500">8000</span>
        </div>
      </div>
    </aside>
  );
}
