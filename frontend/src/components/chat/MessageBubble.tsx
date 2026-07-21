"use client";

import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { Message } from "@/lib/types";
import { getAgentByName } from "@/lib/agents";
import { format } from "date-fns";

interface MessageBubbleProps {
  message: Message;
  onSuggestionClick?: (text: string) => void;
}

const ITERATION_SUGGESTIONS = [
  "Change the color scheme to warm tones",
  "Add a dark mode toggle",
  "Make the layout more compact",
  "Add animations and transitions",
  "Include a contact form",
];

export function MessageBubble({ message, onSuggestionClick }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const agent = message.agentName ? getAgentByName(message.agentName) : null;

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

  const showIterationHints = useMemo(() => {
    return message.metadata?.codeGenerated === true && message.role === "assistant";
  }, [message.metadata, message.role]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn("flex gap-3 px-4 py-2", isUser ? "flex-row-reverse" : "flex-row")}
    >
      {!isUser && (
        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-atoms-border flex items-center justify-center text-sm">
          {agent?.avatarEmoji ?? "\u{1F916}"}
        </div>
      )}

      <div
        className={cn(
          "max-w-[80%] rounded-xl px-4 py-3",
          isUser
            ? "bg-atoms-accent text-white"
            : "bg-atoms-card border border-atoms-border"
        )}
      >
        {!isUser && message.agentName && (
          <div className="mb-1.5 flex items-center gap-1.5">
            <span className="text-xs font-medium text-atoms-accent-hover">
              {agent?.name ?? message.agentName}
            </span>
            {agent?.role && (
              <span className="text-xs text-zinc-500">{agent.role}</span>
            )}
          </div>
        )}

        {thinkingData && !streamText && (
          <div className="mb-2 flex items-center gap-2 text-xs text-zinc-400">
            <div className="flex gap-0.5">
              <span className="h-1.5 w-1.5 rounded-full bg-atoms-accent animate-bounce [animation-delay:0ms]" />
              <span className="h-1.5 w-1.5 rounded-full bg-atoms-accent animate-bounce [animation-delay:150ms]" />
              <span className="h-1.5 w-1.5 rounded-full bg-atoms-accent animate-bounce [animation-delay:300ms]" />
            </div>
            {thinkingData}
          </div>
        )}

        {streamText && (
          <div className="mb-2 text-sm text-zinc-300 leading-relaxed">
            {streamText}
            <span className="inline-block w-1.5 h-4 bg-atoms-accent animate-pulse ml-0.5 align-middle" />
          </div>
        )}

        {isAction && message.content && (
          <div className="mb-2 rounded-lg bg-atoms-accent/10 border border-atoms-accent/20 px-3 py-2 text-xs text-atoms-accent-hover">
            {message.content}
          </div>
        )}

        <div
          className={cn(
            "prose prose-sm max-w-none",
            isUser
              ? "prose-invert"
              : "prose-invert prose-zinc"
          )}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>

        {showIterationHints && onSuggestionClick && (
          <div className="mt-3 pt-2 border-t border-white/10">
            <div className="text-[10px] text-zinc-500 mb-1.5">Try refining:</div>
            <div className="flex flex-wrap gap-1.5">
              {ITERATION_SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => onSuggestionClick(s)}
                  className="rounded-md border border-white/10 bg-white/5 px-2 py-1 text-[11px] text-zinc-400 transition-colors hover:bg-atoms-accent/20 hover:text-atoms-accent-hover hover:border-atoms-accent/30"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        <div
          className={cn(
            "mt-1.5 text-[10px]",
            isUser ? "text-white/50 text-right" : "text-zinc-600"
          )}
        >
          {format(new Date(message.createdAt), "HH:mm")}
        </div>
      </div>
    </motion.div>
  );
}
