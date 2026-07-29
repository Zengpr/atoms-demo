"use client";

import { Monitor, Tablet, Smartphone } from "lucide-react";
import { cn } from "@/lib/utils";

type Viewport = "desktop" | "tablet" | "mobile";

interface ViewportToggleProps {
  value: Viewport;
  onChange: (v: Viewport) => void;
}

const OPTIONS: { value: Viewport; icon: typeof Monitor; label: string }[] = [
  { value: "desktop", icon: Monitor, label: "桌面端" },
  { value: "tablet", icon: Tablet, label: "平板" },
  { value: "mobile", icon: Smartphone, label: "移动端" },
];

export function ViewportToggle({ value, onChange }: ViewportToggleProps) {
  return (
    <div className="flex items-center gap-0.5 rounded-lg bg-atoms-dark/60 p-0.5 border border-atoms-border/50">
      {OPTIONS.map(({ value: v, icon: Icon, label }) => (
        <button
          key={v}
          onClick={() => onChange(v)}
          title={label}
          className={cn(
            "rounded-md px-2 py-1.5 transition-all flex items-center gap-1",
            value === v
              ? "bg-atoms-accent/20 text-atoms-accent-hover shadow-sm"
              : "text-zinc-500 hover:text-zinc-300"
          )}
        >
          <Icon className="h-3.5 w-3.5" />
          <span className="text-[11px] font-medium">{label}</span>
        </button>
      ))}
    </div>
  );
}
