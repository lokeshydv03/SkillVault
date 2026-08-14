"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  LayoutDashboard,
  Terminal,
  Brain,
  History,
  Activity,
  Settings,
  ArrowRight,
} from "lucide-react";

export default function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const router = RouterHook();

  function RouterHook() {
    return useRouter();
  }

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === "Escape") {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  if (!isOpen) return null;

  const actions = [
    { name: "Go to Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Open Agent Playground", href: "/playground", icon: Terminal },
    { name: "Search Skills Vault", href: "/skills", icon: Brain },
    { name: "View Execution Logs", href: "/executions", icon: History },
    { name: "View Activity Observability", href: "/activity", icon: Activity },
    { name: "System Settings & Status", href: "/settings", icon: Settings },
  ];

  const filtered = actions.filter((a) =>
    a.name.toLowerCase().includes(query.toLowerCase())
  );

  const navigate = (href: string) => {
    router.push(href);
    setIsOpen(false);
    setQuery("");
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-start justify-center pt-24 px-4 animate-in fade-in duration-150">
      <div className="w-full max-w-xl bg-[#12151B] border border-[#262C38] rounded-xl shadow-2xl overflow-hidden text-zinc-200">
        {/* Input */}
        <div className="flex items-center px-4 border-b border-[#1E232E] py-3.5 gap-3">
          <Search className="w-4 h-4 text-zinc-400" />
          <input
            type="text"
            placeholder="Type a command or search (e.g. Playground, Skills)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="flex-1 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none"
          />
          <kbd className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-[#1C212B] border border-[#2B3242] text-zinc-400 rounded">
            ESC
          </kbd>
        </div>

        {/* Action List */}
        <div className="p-2 max-h-80 overflow-y-auto space-y-1">
          {filtered.length === 0 ? (
            <div className="p-4 text-center text-xs text-zinc-500 font-mono">
              No matching command found.
            </div>
          ) : (
            filtered.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.href}
                  onClick={() => navigate(item.href)}
                  className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs hover:bg-[#1B202A] text-zinc-300 hover:text-[#B0EB0A] transition-colors group text-left"
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 text-zinc-400 group-hover:text-[#B0EB0A]" />
                    <span className="font-medium">{item.name}</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-zinc-600 group-hover:text-[#B0EB0A] transition-transform group-hover:translate-x-0.5" />
                </button>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
