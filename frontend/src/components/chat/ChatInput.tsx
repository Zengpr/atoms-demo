"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Send, Users, Wrench, Zap, Search, Paperclip, X } from "lucide-react";
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
  { id: "team", label: "团队", desc: "多智能体协作", Icon: Users },
  { id: "engineer", label: "工程师", desc: "单智能体快速构建", Icon: Wrench },
  { id: "race", label: "竞速", desc: "双策略竞争", Icon: Zap },
  { id: "research", label: "研究", desc: "深度主题分析", Icon: Search },
];

interface AttachedFile {
  name: string;
  content: string;
  type: string;
  size: number;
}

interface ChatInputProps {
  onSend: (content: string, fileContexts?: AttachedFile[]) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [showModes, setShowModes] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
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
  const ActiveIcon = activeMode.Icon;

  return (
    <div className="border-t border-atoms-border bg-atoms-card/80 backdrop-blur-sm p-3">
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
        <div className="relative flex-shrink-0">
          <button
            onClick={() => setShowModes(!showModes)}
            className="flex h-8 items-center gap-1.5 rounded-lg bg-atoms-accent/10 border border-atoms-accent/20 px-2.5 text-xs font-medium text-atoms-accent-hover transition-all hover:bg-atoms-accent/15"
          >
            <ActiveIcon className="h-3.5 w-3.5" />
            {activeMode.label}
          </button>
          {showModes && (
            <div className="absolute bottom-full left-0 mb-2 w-48 rounded-xl border border-atoms-border bg-atoms-card p-1 shadow-2xl z-50">
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
                      "flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-xs transition-all",
                      currentMode === m.id
                        ? "bg-atoms-accent/10 text-atoms-accent-hover"
                        : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                    )}
                  >
                    <MIcon className="h-4 w-4 flex-shrink-0" />
                    <div className="text-left">
                      <div className="font-medium">{m.label}</div>
                      <div className="text-[10px] text-zinc-500 mt-0.5">{m.desc}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

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
          title="Attach file"
        >
          <Paperclip className="h-4 w-4" />
        </button>

        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`描述你想构建什么（${activeMode.label}模式）...`}
          rows={1}
          disabled={disabled || isStreaming}
          className="flex-1 resize-none bg-transparent text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none disabled:opacity-30 leading-relaxed"
        />

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
      </div>
    </div>
  );
}
