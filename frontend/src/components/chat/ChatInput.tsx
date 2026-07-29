"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Send, Users, Wrench, Zap, Search, Paperclip, X, Square } from "lucide-react";
import { cn } from "@/lib/utils";
import { useChatStore } from "@/lib/store";
import type { ChatMode } from "@/lib/types";

interface ModeOption {
  id: ChatMode;
  label: string;
  emoji: string;
  desc: string;
  Icon: React.FC<{ className?: string }>;
}

const MODES: ModeOption[] = [
  { id: "engineer", label: "工程师", emoji: "💻", desc: "单智能体快速构建", Icon: Wrench },
  { id: "team", label: "团队", emoji: "👥", desc: "多智能体协作", Icon: Users },
  { id: "race", label: "竞速", emoji: "⚡", desc: "双策略竞争", Icon: Zap },
  { id: "research", label: "研究", emoji: "🔬", desc: "深度主题分析", Icon: Search },
];

interface AttachedFile {
  name: string;
  content: string;
  type: string;
  size: number;
}

interface ChatInputProps {
  onSend: (content: string, fileContexts?: AttachedFile[]) => void;
  onStop?: () => void;
  disabled?: boolean;
  prefillText?: string;
  onPrefillConsumed?: () => void;
}

export function ChatInput({ onSend, onStop, disabled, prefillText, onPrefillConsumed }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [showModes, setShowModes] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const modeDropdownRef = useRef<HTMLDivElement>(null);
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

  useEffect(() => {
    if (prefillText) {
      setValue(prefillText);
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
      onPrefillConsumed?.();
    }
  }, [prefillText, onPrefillConsumed]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (modeDropdownRef.current && !modeDropdownRef.current.contains(e.target as Node)) {
        setShowModes(false);
      }
    }
    if (showModes) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [showModes]);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled || isStreaming) return;
    onSend(trimmed, attachedFiles.length > 0 ? attachedFiles : undefined);
    setValue("");
    setAttachedFiles([]);
    setShowModes(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, disabled, isStreaming, onSend, attachedFiles]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleFileAttach = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    Array.from(files).forEach((file) => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        const content = ev.target?.result as string;
        setAttachedFiles((prev) => [...prev, {
          name: file.name,
          content: content.slice(0, 50000),
          type: file.type || "text/plain",
          size: file.size,
        }]);
      };
      if (file.type.startsWith("image/")) {
        reader.readAsDataURL(file);
      } else {
        reader.readAsText(file);
      }
    });
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, []);

  const removeFile = useCallback((name: string) => {
    setAttachedFiles((prev) => prev.filter((f) => f.name !== name));
  }, []);

  const activeMode = MODES.find((m) => m.id === currentMode) ?? MODES[0];

  return (
    <div className="border-t border-atoms-border bg-atoms-card/80 backdrop-blur-sm p-3">
      <div className="flex items-center gap-1.5 mb-2 overflow-x-auto scrollbar-none">
        {MODES.map((m) => {
          const MIcon = m.Icon;
          const isActive = currentMode === m.id;
          return (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              className={cn(
                "flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-all whitespace-nowrap",
                isActive
                  ? "bg-atoms-accent/15 text-atoms-accent-hover border border-atoms-accent/25 shadow-sm shadow-atoms-accent/10"
                  : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5 border border-transparent"
              )}
            >
              <span className="text-sm">{m.emoji}</span>
              <MIcon className="h-3 w-3" />
              <span>{m.label}</span>
            </button>
          );
        })}
      </div>

      {attachedFiles.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-2">
          {attachedFiles.map((f) => (
            <div key={f.name} className="flex items-center gap-1.5 rounded-lg bg-atoms-accent/8 border border-atoms-accent/15 px-2.5 py-1 text-xs text-atoms-accent-hover">
              <Paperclip className="h-3 w-3" />
              <span className="truncate max-w-[120px]">{f.name}</span>
              <span className="text-zinc-500">{(f.size / 1024).toFixed(0)}KB</span>
              <button onClick={() => removeFile(f.name)} className="text-zinc-500 hover:text-zinc-200 transition-colors">
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-end gap-2 rounded-2xl border border-atoms-border bg-atoms-dark px-3 py-2 transition-all focus-within:border-atoms-accent/30 focus-within:shadow-sm focus-within:shadow-atoms-accent/5">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleFileAttach}
          accept=".html,.css,.js,.ts,.json,.md,.txt,.py,.svg,.png,.jpg,.jpeg,.gif"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || isStreaming}
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors disabled:opacity-30"
          title="添加附件"
        >
          <Paperclip className="h-4 w-4" />
        </button>

        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`描述你想构建的产品（${activeMode.emoji} ${activeMode.label}模式）...`}
          rows={1}
          disabled={disabled || isStreaming}
          className="flex-1 resize-none bg-transparent text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none disabled:opacity-30 leading-relaxed"
        />

        {isStreaming && onStop ? (
          <button
            onClick={onStop}
            className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all border border-red-500/30"
            title="停止生成"
          >
            <Square className="h-3.5 w-3.5" />
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!value.trim() || disabled || isStreaming}
            className={cn(
              "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg transition-all",
              value.trim() && !isStreaming
                ? "bg-atoms-accent text-white hover:bg-atoms-accent-hover shadow-sm shadow-atoms-accent/20"
                : "bg-zinc-800/50 text-zinc-600"
            )}
          >
            <Send className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
