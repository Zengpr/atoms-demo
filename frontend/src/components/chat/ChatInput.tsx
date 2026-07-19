"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Send, Users, Wrench, Zap, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { useChatStore } from "@/lib/store";
import type { ChatMode } from "@/lib/types";

interface ModeOption {
  id: ChatMode;
  label: string;
  desc: string;
  Icon: React.FC<{ className?: string }>;
}

const MODES: ModeOption[] = [
  { id: "engineer", label: "Engineer", desc: "Single agent, fast output", Icon: Wrench },
  { id: "team", label: "Team", desc: "Multi-agent SOP pipeline", Icon: Users },
  { id: "race", label: "Race", desc: "Same model, diff prompts", Icon: Zap },
  { id: "research", label: "Research", desc: "Deep topic research", Icon: Search },
];

interface ChatInputProps {
  onSend: (content: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [showModes, setShowModes] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { currentMode, setMode, isStreaming } = useChatStore();

  const adjustHeight = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled || isStreaming) return;
    onSend(trimmed);
    setValue("");
    setShowModes(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, disabled, isStreaming, onSend]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const activeMode = MODES.find((m) => m.id === currentMode) ?? MODES[0];
  const ActiveIcon = activeMode.Icon;

  return (
    <div className="border-t border-atoms-border bg-atoms-card p-3">
      <div className="flex items-end gap-2 rounded-xl border border-atoms-border bg-atoms-dark p-2">
        <div className="relative flex-shrink-0">
          <button
            onClick={() => setShowModes(!showModes)}
            className="flex h-8 items-center gap-1 rounded-lg bg-atoms-accent/20 px-2 text-xs font-medium text-atoms-accent-hover transition-colors"
          >
            <ActiveIcon className="h-3.5 w-3.5" />
            {activeMode.label}
          </button>
          {showModes && (
            <div className="absolute bottom-full left-0 mb-2 w-44 rounded-lg border border-atoms-border bg-atoms-card p-1 shadow-xl z-50">
              {MODES.map((m) => {
                const MIcon = m.Icon;
                return (
                  <button
                    key={m.id}
                    onClick={() => {
                      setMode(m.id);
                      setShowModes(false);
                    }}
                    className={cn(
                      "flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs font-medium transition-colors",
                      currentMode === m.id
                        ? "bg-atoms-accent/20 text-atoms-accent-hover"
                        : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                    )}
                  >
                    <MIcon className="h-3.5 w-3.5" />
                    <div className="text-left">
                      <div>{m.label}</div>
                      <div className="text-[10px] text-zinc-500">{m.desc}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Describe what you want to build (${activeMode.label} mode)...`}
          rows={1}
          disabled={disabled || isStreaming}
          className="flex-1 resize-none bg-transparent text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none disabled:opacity-50"
        />

        <button
          onClick={handleSend}
          disabled={!value.trim() || disabled || isStreaming}
          className={cn(
            "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg transition-colors",
            value.trim() && !isStreaming
              ? "bg-atoms-accent text-white hover:bg-atoms-accent-hover"
              : "bg-zinc-800 text-zinc-500"
          )}
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
