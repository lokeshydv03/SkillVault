"use client";

import { usePathname } from "next/navigation";
import { Search } from "lucide-react";

export default function Header() {
  const pathname = usePathname();

  const getTitle = () => {
    if (pathname.startsWith("/playground")) return "Agent Playground";
    if (pathname.startsWith("/skills")) return "Skill Vault Memory";
    if (pathname.startsWith("/executions")) return "Execution History";
    if (pathname.startsWith("/activity")) return "Activity Observability";
    if (pathname.startsWith("/settings")) return "System Status & Settings";
    return "Dashboard Overview";
  };

  return (
    <header className="h-16 border-b border-[#1F242D] bg-[#0B0D10]/80 backdrop-blur-md sticky top-0 z-20 px-8 flex items-center justify-between">
      <h2 className="text-sm font-semibold text-zinc-100 tracking-wide">
        {getTitle()}
      </h2>

      <div className="flex items-center gap-4">
        {/* Command Palette Trigger */}
        <button
          onClick={() => {
            const event = new KeyboardEvent("keydown", {
              key: "k",
              metaKey: true,
              bubbles: true,
            });
            window.dispatchEvent(event);
          }}
          className="flex items-center gap-3 px-3 py-1.5 rounded-lg bg-[#141820] border border-[#222834] text-xs text-zinc-400 hover:text-zinc-200 hover:border-[#2D3545] transition-colors"
        >
          <Search className="w-3.5 h-3.5" />
          <span>Quick search...</span>
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-[#1E232E] text-zinc-400 rounded border border-[#2B3242]">
            ⌘K
          </kbd>
        </button>

        {/* System Pill */}
        <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#131720] border border-[#1E2430] text-[11px] font-mono text-zinc-400">
          <span className="w-1.5 h-1.5 rounded-full bg-[#B0EB0A]" />
          <span>Self-Evolving AI</span>
        </div>
      </div>
    </header>
  );
}
