import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import QueryProvider from "@/components/providers/QueryProvider";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import CommandPalette from "@/components/layout/CommandPalette";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "SkillVault — Persistent AI Skill Memory & Self-Evolving Agent",
  description:
    "Self-evolving AI Agent capability memory infrastructure where agents discover, synthesize, AST-validate, and persist reusable Python capabilities.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable} dark h-full antialiased`}>
      <body className="bg-[#0B0D10] text-zinc-100 font-sans min-h-screen flex text-sm">
        <QueryProvider>
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0">
            <Header />
            <main className="flex-1 p-8 overflow-y-auto">{children}</main>
          </div>
          <CommandPalette />
        </QueryProvider>
      </body>
    </html>
  );
}
