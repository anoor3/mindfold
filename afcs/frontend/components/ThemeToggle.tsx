"use client";

import { MoonStar, Sun } from "lucide-react";

import { useTheme } from "./theme-provider";

export function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button
      aria-label="Toggle theme"
      onClick={toggle}
      className="focus-ring rounded-full border border-[var(--border)] bg-[var(--card)] p-2 transition hover:scale-105 hover:shadow-lg"
    >
      {theme === "dark" ? <Sun className="h-5 w-5" /> : <MoonStar className="h-5 w-5" />}
    </button>
  );
}
