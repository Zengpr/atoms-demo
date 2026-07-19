"use client";

import { useRef, useEffect, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useChatStore, usePreviewStore } from "@/lib/store";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";
import { streamChat } from "@/lib/api";
import type { Message } from "@/lib/types";
import { AGENTS } from "@/lib/agents";

interface ChatPanelProps {
  projectId: string;
}

function getAgentEmoji(name: string): string {
  const agent = AGENTS.find((a) => a.name === name);
  return agent?.avatarEmoji ?? "🤖";
}

export function ChatPanel({ projectId }: ChatPanelProps) {
  const { messages, isStreaming, addMessage, updateLastAgentMessage, setStreaming, currentMode } =
    useChatStore();
  const { setPreviewHtml } = usePreviewStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = useCallback(
    async (content: string) => {
      const userMsg: Message = {
        id: crypto.randomUUID(),
        conversationId: projectId,
        role: "user",
        content,
        createdAt: new Date().toISOString(),
      };
      addMessage(userMsg);
      setStreaming(true);

      let receivedComplete = false;
      let lastThinkingId: string | null = null;

      try {
        for await (const sse of streamChat(projectId, content, currentMode)) {
          const agentName = (sse.data.agent as string) ?? "System";
          const emoji = getAgentEmoji(agentName);

          if (sse.event === "agent_thinking") {
            const id = crypto.randomUUID();
            lastThinkingId = id;
            addMessage({
              id,
              conversationId: projectId,
              role: "agent",
              agentName,
              content: "",
              metadata: {
                thinking: true,
                emoji,
                message: sse.data.message ?? `${emoji} ${agentName} is thinking...`,
                streamText: "",
              },
              createdAt: new Date().toISOString(),
            });
          } else if (sse.event === "agent_stream") {
            const chunk = (sse.data.chunk as string) ?? "";
            if (lastThinkingId) {
              updateLastAgentMessage(lastThinkingId, chunk);
            }
          } else if (sse.event === "agent_action") {
            lastThinkingId = null;
            addMessage({
              id: crypto.randomUUID(),
              conversationId: projectId,
              role: "agent",
              agentName,
              content: (sse.data.action as string) ?? "Working...",
              metadata: {
                action: true,
                emoji,
                plan: sse.data.plan,
                prd: sse.data.prd,
                architecture: sse.data.architecture,
                duration_ms: sse.data.duration_ms,
              },
              createdAt: new Date().toISOString(),
            });
          } else if (sse.event === "code_generated") {
            const code = (sse.data.code as string) ?? "";
            if (code) {
              setPreviewHtml(code);
            }
          } else if (sse.event === "message_complete") {
            lastThinkingId = null;
            receivedComplete = true;
            const message = (sse.data.message as string) ?? "";
            const completeAgentName = (sse.data.agent as string) ?? "System";
            addMessage({
              id: crypto.randomUUID(),
              conversationId: projectId,
              role: "assistant",
              agentName: completeAgentName,
              content: message,
              metadata: {
                emoji: getAgentEmoji(completeAgentName),
                duration_ms: sse.data.duration_ms,
                agents_used: sse.data.agents_used,
                codeGenerated: true,
              },
              createdAt: new Date().toISOString(),
            });
          }
        }
        if (!receivedComplete) {
          addMessage({
            id: crypto.randomUUID(),
            conversationId: projectId,
            role: "assistant",
            content: "Stream ended unexpectedly. Please try again.",
            metadata: { error: true },
            createdAt: new Date().toISOString(),
          });
        }
      } catch {
        addMessage({
          id: crypto.randomUUID(),
          conversationId: projectId,
          role: "assistant",
          content: "Sorry, an error occurred. Please try again.",
          metadata: { error: true },
          createdAt: new Date().toISOString(),
        });
      } finally {
        setStreaming(false);
      }
    },
    [projectId, addMessage, updateLastAgentMessage, setStreaming, setPreviewHtml, currentMode]
  );

  return (
    <div className="flex h-full flex-col">
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-1 py-2 scrollbar-thin"
      >
        <AnimatePresence mode="popLayout">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} onSuggestionClick={handleSend} />
          ))}
        </AnimatePresence>
        {isStreaming && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 px-4 py-2"
          >
            <div className="flex gap-1">
              <span className="h-2 w-2 rounded-full bg-atoms-accent animate-bounce [animation-delay:0ms]" />
              <span className="h-2 w-2 rounded-full bg-atoms-accent animate-bounce [animation-delay:150ms]" />
              <span className="h-2 w-2 rounded-full bg-atoms-accent animate-bounce [animation-delay:300ms]" />
            </div>
            <span className="text-xs text-zinc-500">
              Agents are working...
            </span>
          </motion.div>
        )}
        {messages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-full text-center px-8">
            <div className="text-4xl mb-4">{"\u{1F916}"}</div>
            <h3 className="text-lg font-semibold text-zinc-300 mb-2">
              Start Building
            </h3>
            <p className="text-sm text-zinc-500 max-w-xs mb-4">
              Describe what you want to build and our AI agents will generate
              the code for you. You can iterate and refine through conversation.
            </p>
            <div className="grid grid-cols-2 gap-2 w-full max-w-sm">
              {[
                { emoji: "\u{1F3E0}", text: "Landing page for my startup" },
                { emoji: "\u{1F4CA}", text: "Dashboard with charts and stats" },
                { emoji: "\u{1F6D2}", text: "E-commerce product catalog" },
                { emoji: "\u{1F3A8}", text: "Creative portfolio website" },
                { emoji: "\u{1F522}", text: "Counter app with dark mode" },
                { emoji: "\u{1F4DD}", text: "Todo list with categories" },
              ].map(({ emoji, text }) => (
                <button
                  key={text}
                  onClick={() => handleSend(text)}
                  className="rounded-lg border border-atoms-border bg-atoms-card px-3 py-2 text-left text-xs text-zinc-400 transition-colors hover:bg-white/5 hover:text-zinc-200 flex items-start gap-1.5"
                >
                  <span className="flex-shrink-0">{emoji}</span>
                  <span>{text}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
      <ChatInput onSend={handleSend} />
    </div>
  );
}
