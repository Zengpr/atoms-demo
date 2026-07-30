"use client";

import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import type { Message } from "@/lib/types";
import { getAgentByName, getAgentColor } from "@/lib/agents";
import { format } from "date-fns";
import Image from "next/image";
import { ChevronDown, ChevronRight, FileCode, FileText, Play, CheckCircle2, XCircle, Clock } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
  onSuggestionClick?: (text: string) => void;
}

const ITERATION_SUGGESTIONS = [
  "修复发现的问题",
  "调整样式和布局",
  "添加新功能",
];

interface ActionItemProps {
  label: string;
  secondary?: string;
  status: "running" | "success" | "failed" | "pending";
  icon?: "file-read" | "file-write" | "terminal" | "preview" | "deploy" | "search" | "task";
}

function ActionItemIcon({ type }: { type: string }) {
  switch (type) {
    case "file-read":
    case "file-write":
      return <FileCode className="h-3.5 w-3.5" />;
    case "terminal":
      return <Play className="h-3.5 w-3.5" />;
    case "preview":
    case "deploy":
      return <CheckCircle2 className="h-3.5 w-3.5" />;
    case "search":
      return <FileText className="h-3.5 w-3.5" />;
    case "task":
      return <Clock className="h-3.5 w-3.5" />;
    default:
      return <FileCode className="h-3.5 w-3.5" />;
  }
}

function ActionItem({ label, secondary, status, icon }: ActionItemProps) {
  return (
    <div className="action-item-card">
      <span className={cn(
        "flex-shrink-0",
        status === "running" && "text-zinc-500 animate-pulse-glow",
        status === "success" && "text-emerald-400",
        status === "failed" && "text-red-400",
        status === "pending" && "text-zinc-600"
      )}>
        {status === "success" ? <CheckCircle2 className="h-3.5 w-3.5" /> :
         status === "failed" ? <XCircle className="h-3.5 w-3.5" /> :
         status === "running" ? <div className="h-3.5 w-3.5 rounded-full border-2 border-zinc-500 border-t-transparent animate-spin" /> :
         <ActionItemIcon type={icon ?? "file-read"} />}
      </span>
      <span className={cn(
        "truncate",
        status === "running" && "text-zinc-400",
        status === "success" && "text-zinc-300",
        status === "failed" && "text-red-300",
        status === "pending" && "text-zinc-600"
      )}>
        {label}
      </span>
      {secondary && (
        <span className="text-zinc-600 truncate text-xs">{secondary}</span>
      )}
    </div>
  );
}

function AgentAvatar({ name, size = 28 }: { name: string; size?: number }) {
  const agent = getAgentByName(name);
  const agentColor = getAgentColor(name);

  if (agent?.avatarUrl) {
    return (
      <div className="relative">
        <div
          className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-30 transition-opacity blur-sm"
          style={{ backgroundColor: agentColor }}
        />
        <Image
          src={agent.avatarUrl}
          alt={agent.name}
          width={size}
          height={size}
          className="agent-avatar-img"
          style={{ borderColor: `${agentColor}50`, borderWidth: 2 }}
          unoptimized
        />
      </div>
    );
  }

  return (
    <div
      className="flex-shrink-0 rounded-full flex items-center justify-center text-sm agent-avatar-img"
      style={{
        width: size,
        height: size,
        backgroundColor: `${agentColor}20`,
        borderColor: `${agentColor}50`,
        boxShadow: `0 0 8px ${agentColor}15`,
      }}
    >
      {agent?.avatarEmoji ?? "\u{1F916}"}
    </div>
  );
}

export function MessageBubble({ message, onSuggestionClick }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const agent = message.agentName ? getAgentByName(message.agentName) : null;
  const agentColor = message.agentName ? getAgentColor(message.agentName) : "#6366F1";
  const role = (message.metadata?.role as string) ?? agent?.role ?? "";
  const [thinkExpanded, setThinkExpanded] = useState(false);

  const thinkingData = useMemo(() => {
    if (message.metadata?.thinking) {
      const msg = message.metadata.message as string | undefined;
      return msg ?? (message.metadata.thinking as string);
    }
    return null;
  }, [message.metadata]);

  const streamText = useMemo(() => {
    if (message.metadata?.streamText) {
      return message.metadata.streamText as string;
    }
    return null;
  }, [message.metadata]);

  const isAction = useMemo(() => {
    return message.metadata?.action === true;
  }, [message.metadata]);

  const isApproval = useMemo(() => {
    return message.metadata?.approval === true;
  }, [message.metadata]);

  const showIterationHints = useMemo(() => {
    return message.metadata?.codeGenerated === true && message.role === "assistant";
  }, [message.metadata, message.role]);

  const actionItems = useMemo(() => {
    if (!isAction || !message.metadata) return [];
    const items: ActionItemProps[] = [];
    const prd = message.metadata.prd;
    const architecture = message.metadata.architecture;
    const plan = message.metadata.plan;

    if (plan) {
      try {
        const p = typeof plan === "string" ? JSON.parse(plan) : plan;
        const steps = p?.steps ?? [];
        steps.forEach((s: Record<string, unknown>) => {
          items.push({
            label: `${s.agent ?? "Agent"}: ${s.task ?? ""}`,
            status: "success",
            icon: "task",
          });
        });
      } catch { /* ignore */ }
    }
    if (prd) {
      try {
        const p = typeof prd === "string" ? JSON.parse(prd) : prd;
        const features = p?.prd?.features ?? p?.features ?? [];
        features.slice(0, 4).forEach((f: Record<string, unknown>) => {
          items.push({
            label: `Write: ${(f.name ?? f) as string}`,
            status: "success",
            icon: "file-write",
          });
        });
      } catch { /* ignore */ }
    }
    if (architecture) {
      try {
        const a = typeof architecture === "string" ? JSON.parse(architecture) : architecture;
        const components = a?.components ?? a?.architecture?.components ?? [];
        components.slice(0, 4).forEach((c: Record<string, unknown>) => {
          items.push({
            label: `Design: ${(c.name ?? c) as string}`,
            status: "success",
            icon: "file-read",
          });
        });
      } catch { /* ignore */ }
    }
    return items;
  }, [isAction, message.metadata]);

  if (isApproval) {
    return null;
  }

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.15 }}
        className="flex justify-end px-4 py-1.5"
      >
        <div className="max-w-[75%] rounded-2xl rounded-br-sm bg-gradient-to-br from-atoms-accent to-atoms-accent-hover px-4 py-2.5 shadow-lg shadow-atoms-accent/10">
          <p className="text-sm text-white leading-relaxed whitespace-pre-wrap">{message.content}</p>
          <p className="text-[10px] text-white/40 text-right mt-1">{format(new Date(message.createdAt), "HH:mm")}</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.15 }}
      className="message-group-enter px-4 py-1 group"
    >
      {message.agentName && (
        <div className="flex items-center gap-2 h-8 mb-1">
          <AgentAvatar name={message.agentName} size={22} />
          <span className="text-xs font-semibold tracking-wide" style={{ color: agentColor }}>
            {agent?.name ?? message.agentName}
          </span>
          <div className="h-3 w-px bg-white/10" />
          <span className="text-[11px] text-zinc-500">{role}</span>
          <span className="text-[10px] text-zinc-600 ml-auto opacity-0 group-hover:opacity-100 transition-opacity">
            {format(new Date(message.createdAt), "HH:mm")}
          </span>
        </div>
      )}

      <div className="pl-8">
        {thinkingData && !streamText && (
          <div className="think-merge-container mb-2">
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <div className="flex gap-0.5">
                <span className="h-1.5 w-1.5 rounded-full animate-bounce [animation-delay:0ms]" style={{ backgroundColor: agentColor }} />
                <span className="h-1.5 w-1.5 rounded-full animate-bounce [animation-delay:150ms]" style={{ backgroundColor: agentColor }} />
                <span className="h-1.5 w-1.5 rounded-full animate-bounce [animation-delay:300ms]" style={{ backgroundColor: agentColor }} />
              </div>
              <span>{thinkingData}</span>
            </div>
          </div>
        )}

        {streamText && (
          <div className="think-merge-container mb-2">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-1.5">
                <span className="text-[11px] text-zinc-500 font-medium">思考中</span>
                <span className="h-1 w-1 rounded-full bg-atoms-accent animate-pulse-glow" />
              </div>
              <button
                onClick={() => setThinkExpanded(!thinkExpanded)}
                className="flex items-center gap-0.5 text-[10px] text-zinc-500 hover:text-zinc-300 transition-colors rounded px-1.5 py-0.5 hover:bg-white/5"
              >
                {thinkExpanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                {thinkExpanded ? "收起" : "查看详情"}
              </button>
            </div>
            <AnimatePresence>
              {thinkExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="text-sm text-zinc-300 leading-relaxed mb-1 whitespace-pre-wrap">
                    {streamText.length > 2000 ? streamText.slice(0, 2000) + "..." : streamText}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <span className="inline-block w-1.5 h-4 animate-pulse rounded-sm" style={{ backgroundColor: agentColor, opacity: 0.6 }} />
          </div>
        )}

        {isAction && actionItems.length > 0 && (
          <div className="think-merge-container mb-2">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-1.5">
                <span className="text-[11px] font-semibold text-zinc-200">{message.content.split("\n")[0]}</span>
              </div>
              <button
                onClick={() => setThinkExpanded(!thinkExpanded)}
                className="flex items-center gap-0.5 text-[10px] text-zinc-500 hover:text-zinc-300 transition-colors rounded px-1.5 py-0.5 hover:bg-white/5"
              >
                {thinkExpanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                {thinkExpanded ? "收起" : `查看详情（${actionItems.length}）`}
              </button>
            </div>
            <AnimatePresence>
              {!thinkExpanded ? (
                <div className="space-y-0.5">
                  {actionItems.slice(0, 3).map((item, i) => (
                    <ActionItem key={i} {...item} />
                  ))}
                  {actionItems.length > 3 && (
                    <div className="text-[11px] text-zinc-500 pl-4">+{actionItems.length - 3} 项更多...</div>
                  )}
                </div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="space-y-0.5">
                    {actionItems.map((item, i) => (
                      <ActionItem key={i} {...item} />
                    ))}
                  </div>
                  {message.content && (
                    <div className="mt-2.5 p-3 rounded-lg bg-white/3 border border-white/6 text-xs text-zinc-300 leading-relaxed whitespace-pre-line max-h-72 overflow-y-auto scrollbar-thin">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {isAction && actionItems.length === 0 && message.content && (
          <div className="rounded-xl px-3.5 py-2.5 text-sm text-zinc-200 leading-relaxed whitespace-pre-line border-l-2 backdrop-blur-sm" style={{ borderColor: `${agentColor}60`, backgroundColor: `${agentColor}08` }}>
            {message.content}
          </div>
        )}

        {!isAction && !thinkingData && !streamText && message.content && (
          <div className="prose prose-sm prose-invert prose-zinc max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {showIterationHints && onSuggestionClick && (
          <div className="mt-3 pt-2.5 border-t border-white/5">
            <div className="text-[10px] text-zinc-500 mb-1.5 font-medium">继续迭代：</div>
            <div className="flex flex-wrap gap-1.5">
              {ITERATION_SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => onSuggestionClick(s)}
                  className="rounded-lg border border-white/8 bg-white/3 px-2.5 py-1 text-[11px] text-zinc-400 transition-all hover:bg-atoms-accent/10 hover:text-atoms-accent-hover hover:border-atoms-accent/20"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
