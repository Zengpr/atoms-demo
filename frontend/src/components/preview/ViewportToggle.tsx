"use client";

import { Monitor, Tablet, Smartphone } from "lucide-react";
import { cn } from "@/lib/utils";

type Viewport = "desktop" | "tablet" | "mobile";

interface ViewportToggleProps {
  value: Viewport;
  onChange: (v: Viewport) => void;
}

const OPTIONS: { value: Viewport; icon: typeof Monitor; label: string }[] = [
  { value: "desktop", icon: Monitor, label: "Desktop" },
  { value: "tablet", icon: Tablet, label: "Tablet" },
  { value: "mobile", icon: Smartphone, label: "Mobile" },
];

export function ViewportToggle({ value, onChange }: ViewportToggleProps) {
  return (
    <div className="flex items-center gap-1 rounded-lg bg-atoms-dark p-1">
      {OPTIONS.map(({ value: v, icon: Icon, label }) => (
        <button
          key={v}
          onClick={() => onChange(v)}
          title={label}
          className={cn(
            "rounded-md p-1.5 transition-colors",
            value === v
              ? "bg-atoms-accent/20 text-atoms-accent-hover"
              : "text-zinc-500 hover:text-zinc-300"
          )}
        >
          <Icon className="h-4 w-4" />
        </button>
      ))}
    </div>
  );
}
