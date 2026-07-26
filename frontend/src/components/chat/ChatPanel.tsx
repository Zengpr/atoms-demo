"use client";

import { useRef, useEffect, useCallback, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useChatStore, usePreviewStore } from "@/lib/store";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";
import { streamChat } from "@/lib/api";
import type { Message, ApprovalRequest } from "@/lib/types";
import { AGENTS } from "@/lib/agents";

interface ChatPanelProps {
  projectId: string;
}

function getAgentEmoji(name: string): string {
  const agent = AGENTS.find((a) => a.name === name);
  return agent?.avatarEmoji ?? "🤖";
}

export function ChatPanel({ projectId }: ChatPanelProps) {
  const { messages, isStreaming, addMessage, updateLastAgentMessage, setStreaming, currentMode, setMode } =
    useChatStore();
  const { setPreviewHtml, consoleErrors, clearConsoleErrors } = usePreviewStore();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [pendingApproval, setPendingApproval] = useState<ApprovalRequest | null>(null);
  const approvalResolveRef = useRef<(() => void) | null>(null);

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
      setPendingApproval(null);

      const errorMessages = consoleErrors.map(
        (e) => `${e.message}${e.line ? ` (line ${e.line})` : ""}`
      );
      clearConsoleErrors();

      let receivedComplete = false;
      let lastThinkingId: string | null = null;

      try {
        for await (const sse of streamChat(projectId, content, currentMode, errorMessages)) {
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
            const prd = sse.data.prd;
            const architecture = sse.data.architecture;
            const plan = sse.data.plan;
            let richContent = (sse.data.action as string) ?? "Working...";
            if (prd) {
              try {
                const p = typeof prd === "string" ? JSON.parse(prd) : prd;
                const features = p?.prd?.features ?? p?.features ?? [];
                const featList = features.slice(0, 5).map((f: Record<string, unknown>) => `  • ${f.name ?? f}`).join("\n");
                richContent = `📋 PRD — ${p?.prd?.title ?? p?.title ?? ""}\n${featList}`;
              } catch { /* ignore */ }
            } else if (architecture) {
              try {
                const a = typeof architecture === "string" ? JSON.parse(architecture) : architecture;
                const components = a?.components ?? a?.architecture?.components ?? [];
                const compList = components.slice(0, 5).map((c: Record<string, unknown>) => `  • ${c.name ?? c}`).join("\n");
                richContent = `🏗️ Architecture — ${a?.architecture?.pattern ?? a?.pattern ?? ""}\n${compList}`;
              } catch { /* ignore */ }
            } else if (plan) {
              try {
                const p = typeof plan === "string" ? JSON.parse(plan) : plan;
                const stepList = (p?.steps ?? []).map((s: Record<string, unknown>, i: number) => `  ${i+1}. ${s.agent ?? "agent"}: ${s.task ?? ""}`).join("\n");
                richContent = `📝 Team Plan\n${stepList}`;
              } catch { /* ignore */ }
            }
            addMessage({
              id: crypto.randomUUID(),
              conversationId: projectId,
              role: "agent",
              agentName,
              content: richContent,
              metadata: {
                action: true,
                emoji,
                plan: sse.data.plan,
                prd: sse.data.prd,
                architecture: sse.data.architecture,
                steps: sse.data.steps,
                duration_ms: sse.data.duration_ms,
              },
              createdAt: new Date().toISOString(),
            });
          } else if (sse.event === "approval_request") {
            lastThinkingId = null;
            const approval: ApprovalRequest = {
              agent: (sse.data.agent as string) ?? "System",
              emoji: (sse.data.emoji as string) ?? "👨‍💼",
              step: (sse.data.step as number) ?? 0,
              totalSteps: (sse.data.total_steps as number) ?? 0,
              agentName: (sse.data.agent_name as string) ?? "Agent",
              agentKey: (sse.data.agent_key as string) ?? "",
              task: (sse.data.task as string) ?? "",
              message: (sse.data.message as string) ?? "Continue?",
            };
            setPendingApproval(approval);
            addMessage({
              id: crypto.randomUUID(),
              conversationId: projectId,
              role: "agent",
              agentName: approval.agent,
              content: approval.message,
              metadata: {
                approval: true,
                emoji: approval.emoji,
                step: approval.step,
                totalSteps: approval.totalSteps,
                agentName: approval.agentName,
              },
              createdAt: new Date().toISOString(),
            });
            await new Promise<void>((resolve) => {
              approvalResolveRef.current = resolve;
            });
          } else if (sse.event === "code_generated") {
            const code = (sse.data.code as string) ?? "";
            if (code) {
              setPreviewHtml(code);
            }
          } else if (sse.event === "message_complete") {
            lastThinkingId = null;
            receivedComplete = true;
            setPendingApproval(null);
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
        setPendingApproval(null);
        approvalResolveRef.current = null;
      }
    },
    [projectId, addMessage, updateLastAgentMessage, setStreaming, setPreviewHtml, currentMode, clearConsoleErrors, consoleErrors]
  );

  const handleApprovalContinue = useCallback(() => {
    setPendingApproval(null);
    if (approvalResolveRef.current) {
      approvalResolveRef.current();
      approvalResolveRef.current = null;
    }
  }, []);

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
        {isStreaming && !pendingApproval && (
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
        {pendingApproval && isStreaming && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mx-4 my-2 rounded-xl border border-atoms-accent/30 bg-atoms-accent/5 p-3"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">{pendingApproval.emoji}</span>
              <span className="text-sm font-medium text-zinc-200">
                {pendingApproval.agent} — Step {pendingApproval.step}/{pendingApproval.totalSteps}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mb-3">{pendingApproval.message}</p>
            <div className="flex gap-2">
              <button
                onClick={handleApprovalContinue}
                className="flex-1 rounded-lg bg-atoms-accent px-3 py-1.5 text-xs font-medium text-white hover:bg-atoms-accent-hover transition-colors"
              >
                Continue
              </button>
            </div>
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
