"use client";

import { useRef, useEffect, useCallback, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useChatStore, usePreviewStore } from "@/lib/store";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";
import { streamChat } from "@/lib/api";
import type { Message, ApprovalRequest } from "@/lib/types";
import { AGENTS, WORKFLOW_STEPS, getAgentColor, getAgentByName } from "@/lib/agents";
import Image from "next/image";
import { CheckCircle2, Loader2, ChevronDown, ChevronRight } from "lucide-react";

interface ChatPanelProps {
  projectId: string;
}

function getAgentEmoji(name: string): string {
  const agent = AGENTS.find((a) => a.name === name);
  return agent?.avatarEmoji ?? "\u{1F916}";
}

function getAgentRole(name: string): string {
  const agent = AGENTS.find((a) => a.name === name);
  return agent?.role ?? "";
}

type StepStatus = "pending" | "active" | "done";

function WorkflowTracker({ currentStep, totalSteps, activeAgent, stepStatuses }: {
  currentStep: number;
  totalSteps: number;
  activeAgent: string;
  stepStatuses: Record<string, StepStatus>;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-3 mb-2 glass-card p-3"
    >
      <div className="flex items-center gap-2 mb-2.5">
        <span className="text-xs font-medium text-zinc-300">团队工作流</span>
        <span className="text-[10px] text-zinc-600 bg-white/5 px-1.5 py-0.5 rounded">步骤 {currentStep}/{totalSteps}</span>
      </div>
      <div className="flex items-center gap-0.5">
        {WORKFLOW_STEPS.map((step, i) => {
          const status = stepStatuses[step.key] ?? "pending";
          const agentInfo = getAgentByName(step.agent);
          const agentColor = getAgentColor(step.agent);
          return (
            <div key={step.key} className="flex items-center gap-0.5 flex-1">
              <div className="flex flex-col items-center flex-1">
                <div className="relative">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs transition-all duration-300 ${
                      status === "done"
                        ? "bg-emerald-500/15 ring-1 ring-emerald-500/30"
                        : status === "active"
                          ? "ring-2 animate-pulse-glow"
                          : "bg-white/5"
                    }`}
                    style={status === "active" ? { ringColor: `${agentColor}60`, backgroundColor: `${agentColor}10` } : {}}
                  >
                    {status === "done" ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    ) : agentInfo?.avatarUrl ? (
                      <Image src={agentInfo.avatarUrl} alt={step.agent} width={20} height={20} className="rounded-full" unoptimized />
                    ) : (
                      <span className="text-[10px]">{step.icon}</span>
                    )}
                  </div>
                  {status === "active" && (
                    <div className="absolute -bottom-1 left-1/2 -translate-x-1/2">
                      <Loader2 className="h-3 w-3 animate-spin" style={{ color: agentColor }} />
                    </div>
                  )}
                </div>
                <span className={`text-[9px] mt-1 truncate ${
                  status === "done" ? "text-emerald-400" : status === "active" ? "text-zinc-200" : "text-zinc-600"
                }`}>
                  {step.label}
                </span>
              </div>
              {i < WORKFLOW_STEPS.length - 1 && (
                <div className={`h-px flex-1 min-w-[8px] ${
                  status === "done" ? "bg-emerald-500/30" : "bg-white/8"
                }`} />
              )}
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}

function WorkingIndicator({ agentName }: { agentName: string }) {
  const agent = getAgentByName(agentName);
  const agentColor = getAgentColor(agentName);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="working-indicator py-2"
    >
      {agent?.avatarUrl ? (
        <Image src={agent.avatarUrl} alt={agentName} width={16} height={16} className="rounded-full" unoptimized />
      ) : (
        <div className="h-4 w-4 rounded-full" style={{ backgroundColor: `${agentColor}30` }} />
      )}
      <Loader2 className="h-3.5 w-3.5 animate-spin" style={{ color: agentColor }} />
      <span>{agentName} 正在工作中...</span>
    </motion.div>
  );
}

export function ChatPanel({ projectId }: ChatPanelProps) {
  const { messages, isStreaming, addMessage, updateLastAgentMessage, setStreaming, currentMode, setMode } =
    useChatStore();
  const { setPreviewHtml, consoleErrors, clearConsoleErrors } = usePreviewStore();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [pendingApproval, setPendingApproval] = useState<ApprovalRequest | null>(null);
  const approvalResolveRef = useRef<(() => void) | null>(null);
  const [workflowTracker, setWorkflowTracker] = useState<{
    currentStep: number;
    totalSteps: number;
    activeAgent: string;
    stepStatuses: Record<string, StepStatus>;
  } | null>(null);
  const [workingAgent, setWorkingAgent] = useState<string>("Mike");

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = useCallback(
    async (content: string, fileContexts?: { name: string; content: string; type: string; size: number }[]) => {
      const userMsg: Message = {
        id: crypto.randomUUID(),
        conversationId: projectId,
        role: "user",
        content: fileContexts && fileContexts.length > 0 ? `${content}\n\n📎 Attached: ${fileContexts.map(f => f.name).join(", ")}` : content,
        createdAt: new Date().toISOString(),
      };
      addMessage(userMsg);
      setStreaming(true);
      setPendingApproval(null);
      setWorkflowTracker(null);

      const errorMessages = consoleErrors.map(
        (e) => `${e.message}${e.line ? ` (line ${e.line})` : ""}`
      );
      clearConsoleErrors();

      let receivedComplete = false;
      let lastThinkingId: string | null = null;
      const stepStatuses: Record<string, StepStatus> = {};
      let stepIdx = 0;
      const isTeamMode = currentMode === "team";

      if (isTeamMode) {
        stepStatuses["plan"] = "active";
        setWorkflowTracker({ currentStep: 0, totalSteps: 0, activeAgent: "Mike", stepStatuses });
      }

      try {
        for await (const sse of streamChat(projectId, content, currentMode, errorMessages, fileContexts)) {
          const agentName = (sse.data.agent as string) ?? "System";
          const emoji = getAgentEmoji(agentName);
          const role = getAgentRole(agentName);
          const agentKey = (sse.data.agent_key as string) ?? "";

          setWorkingAgent(agentName);

          if (sse.event === "agent_thinking") {
            const id = crypto.randomUUID();
            lastThinkingId = id;
            const hideStream = currentMode === "team";
            addMessage({
              id,
              conversationId: projectId,
              role: "agent",
              agentName,
              content: "",
              metadata: {
                thinking: true,
                emoji,
                role,
                message: `${agentName} is thinking...`,
                streamText: "",
                hideStream,
              },
              createdAt: new Date().toISOString(),
            });
          } else if (sse.event === "agent_stream") {
            const chunk = (sse.data.chunk as string) ?? "";
            if (lastThinkingId) {
              updateLastAgentMessage(lastThinkingId, chunk);
            }
          } else if (sse.event === "agent_action") {
            const msgs = useChatStore.getState().messages;
            const thinkingMsg = msgs.find(m => m.id === lastThinkingId);
            if (thinkingMsg) {
              const isSuppressed = thinkingMsg.metadata?.hideStream === true;
              if (isSuppressed && thinkingMsg.id) {
                useChatStore.setState((s) => ({
                  messages: s.messages.filter((m) => m.id !== thinkingMsg.id),
                }));
              } else {
                const streamText = (thinkingMsg.metadata?.streamText as string) ?? "";
                if (streamText.trim()) {
                  addMessage({
                    id: crypto.randomUUID(),
                    conversationId: projectId,
                    role: "agent",
                    agentName,
                    content: streamText,
                    metadata: { emoji, role },
                    createdAt: new Date().toISOString(),
                  });
                }
              }
            }
            lastThinkingId = null;
            const prd = sse.data.prd;
            const architecture = sse.data.architecture;
            const plan = sse.data.plan;
            let richContent = "";
            let completedStepKey = "";

            if (prd) {
              completedStepKey = "prd";
              try {
                const p = typeof prd === "string" ? JSON.parse(prd) : prd;
                const prdData = p?.prd ?? p;
                const features = prdData?.features ?? [];
                const featList = features.slice(0, 8).map((f: Record<string, unknown>) => {
                  const name = f.name ?? f;
                  const desc = f.description ?? "";
                  const priority = f.priority ?? "";
                  return `• **${name}**${desc ? ` — ${desc}` : ""}${priority ? ` [${priority}]` : ""}`;
                }).join("\n");
                const overview = prdData?.overview ?? prdData?.title ?? "";
                const stories = (prdData?.user_stories ?? []).slice(0, 4).map((s: string) => `• ${s}`).join("\n");
                richContent = `📋 **PRD — ${prdData?.title ?? ""}**\n\n${overview ? `**概述**: ${overview}\n\n` : ""}**功能列表**:\n${featList}${stories ? `\n\n**用户故事**:\n${stories}` : ""}`;
              } catch { /* ignore */ }
            } else if (architecture) {
              completedStepKey = "architecture";
              try {
                const a = typeof architecture === "string" ? JSON.parse(architecture) : architecture;
                const archData = a?.architecture ?? a;
                const components = archData?.component_structure ?? archData?.components ?? [];
                const compList = components.slice(0, 8).map((c: Record<string, unknown>) => {
                  const name = c.name ?? c;
                  const desc = c.description ?? "";
                  return `• **${name}**${desc ? ` — ${desc}` : ""}`;
                }).join("\n");
                const techStack = archData?.tech_stack;
                const techInfo = techStack ? Object.entries(techStack).map(([k, v]) => `• ${k}: ${v}`).join("\n") : "";
                const designSystem = archData?.design_system;
                const colors = designSystem?.colors;
                const colorInfo = colors ? Object.entries(colors).map(([k, v]) => `• ${k}: ${v}`).join("\n") : "";
                richContent = `🏗️ **架构设计**\n\n${techInfo ? `**技术栈**:\n${techInfo}\n\n` : ""}**组件结构**:\n${compList}${colorInfo ? `\n\n**配色方案**:\n${colorInfo}` : ""}`;
              } catch { /* ignore */ }
            } else if (plan) {
              completedStepKey = "plan";
              try {
                const p = typeof plan === "string" ? JSON.parse(plan) : plan;
                const planSummary = p?.plan ?? p?.summary ?? "";
                const steps = p?.steps ?? [];
                const stepList = steps.map((s: Record<string, unknown>, i: number) => `${i + 1}. ${s.agent ?? "agent"}\uFF1A${s.task ?? ""}`).join("\n");
                richContent = planSummary ? `${planSummary}\n\n${stepList}` : stepList;
                if (isTeamMode) {
                  stepStatuses["plan"] = "done";
                  setWorkflowTracker(prev => prev ? { ...prev, totalSteps: steps.length, stepStatuses: { ...stepStatuses } } : null);
                }
              } catch { /* ignore */ }
            }

            if (completedStepKey && isTeamMode) {
              stepStatuses[completedStepKey] = "done";
              stepIdx++;
            }

            if (richContent) {
              addMessage({
                id: crypto.randomUUID(),
                conversationId: projectId,
                role: "agent",
                agentName,
                content: richContent,
                metadata: {
                  action: true,
                  emoji,
                  role,
                  plan: sse.data.plan,
                  prd: sse.data.prd,
                  architecture: sse.data.architecture,
                  steps: sse.data.steps,
                  duration_ms: sse.data.duration_ms,
                },
                createdAt: new Date().toISOString(),
              });
            }
          } else if (sse.event === "approval_request") {
            lastThinkingId = null;
          } else if (sse.event === "code_generated") {
            const code = (sse.data.code as string) ?? "";
            if (code) {
              stepStatuses["code"] = "done";
              setPreviewHtml(code);
              if (isTeamMode) {
                setWorkflowTracker(prev => prev ? { ...prev, stepStatuses: { ...stepStatuses } } : null);
              }
            }
          } else if (sse.event === "message_complete") {
            lastThinkingId = null;
            receivedComplete = true;
            setPendingApproval(null);
            if (isTeamMode) {
              Object.keys(stepStatuses).forEach(k => { stepStatuses[k] = "done"; });
              setWorkflowTracker(prev => prev ? { ...prev, stepStatuses: { ...stepStatuses } } : null);
            }
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
            content: "流式响应意外中断，请重试。",
            metadata: { error: true },
            createdAt: new Date().toISOString(),
          });
        }
      } catch {
        addMessage({
          id: crypto.randomUUID(),
          conversationId: projectId,
          role: "assistant",
          content: "抱歉，发生了错误，请重试。",
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
        {workflowTracker && isStreaming && (
          <WorkflowTracker {...workflowTracker} />
        )}
        {isStreaming && !pendingApproval && (
          <WorkingIndicator agentName={workingAgent} />
        )}
        {pendingApproval && isStreaming && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="task-card mx-4 my-2"
          >
            <div className="flex items-center gap-3 mb-3">
              {getAgentByName(pendingApproval.agentName)?.avatarUrl ? (
                <Image
                  src={getAgentByName(pendingApproval.agentName)!.avatarUrl}
                  alt={pendingApproval.agentName}
                  width={36}
                  height={36}
                  className="agent-avatar-img"
                  style={{ borderColor: `${getAgentColor(pendingApproval.agentName)}40` }}
                  unoptimized
                />
              ) : (
                <div
                  className="w-9 h-9 rounded-full flex items-center justify-center text-base agent-avatar-img"
                  style={{ backgroundColor: `${getAgentColor(pendingApproval.agentName)}20`, borderColor: `${getAgentColor(pendingApproval.agentName)}40` }}
                >
                  {pendingApproval.emoji}
                </div>
              )}
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-zinc-200">{pendingApproval.agent}</span>
                  <span className="text-[10px] text-zinc-500 bg-white/5 px-1.5 py-0.5 rounded">{getAgentRole(pendingApproval.agentName)}</span>
                </div>
                <span className="text-[11px] text-zinc-500">步骤 {pendingApproval.step}/{pendingApproval.totalSteps}</span>
              </div>
            </div>
            <p className="text-sm text-zinc-300 mb-3 pl-12">{pendingApproval.message}</p>
            {pendingApproval.task && (
              <div className="pl-12 mb-3 rounded-lg bg-white/3 px-3 py-2 border border-white/6">
                <p className="text-xs text-zinc-400">
                  <span className="text-zinc-500">下一步：</span>
                  {pendingApproval.task.slice(0, 120)}{pendingApproval.task.length > 120 ? "..." : ""}
                </p>
              </div>
            )}
            <div className="flex gap-2 pl-12">
              <button
                onClick={handleApprovalContinue}
                className="rounded-lg bg-atoms-accent px-5 py-2 text-sm font-medium text-white hover:bg-atoms-accent-hover transition-all hover:shadow-lg hover:shadow-atoms-accent/20"
              >
                  继续
              </button>
            </div>
          </motion.div>
        )}
        {messages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-full text-center px-8">
            <div className="flex items-center -space-x-2 mb-5">
              {AGENTS.slice(0, 5).map((a) => (
                <div
                  key={a.name}
                  className="relative"
                  style={{ zIndex: 5 - AGENTS.indexOf(a) }}
                >
                  <Image
                    src={a.avatarUrl}
                    alt={a.name}
                    width={40}
                    height={40}
                    className="agent-avatar-img"
                    style={{ borderColor: `${a.color}50`, borderWidth: 2 }}
                    unoptimized
                  />
                </div>
              ))}
            </div>
            <h3 className="text-lg font-semibold text-zinc-200 mb-1.5">
              AI 团队就绪
            </h3>
            <p className="text-sm text-zinc-500 max-w-xs mb-5 leading-relaxed">
              描述你想构建什么。Mike协调团队，Emma编写PRD，Bob设计架构，Alex实现代码。
            </p>
            <div className="grid grid-cols-2 gap-2 w-full max-w-sm">
              {[
                { emoji: "\u{1F3AE}", text: "Super Mario-style platformer game" },
                { emoji: "\u{1F4CA}", text: "Data dashboard with charts and stats" },
                { emoji: "\u{1F6D2}", text: "E-commerce product showcase page" },
                { emoji: "\u{1F3A8}", text: "Creative portfolio website" },
              ].map(({ emoji, text }) => (
                <button
                  key={text}
                  onClick={() => handleSend(text)}
                  className="rounded-xl border border-atoms-border bg-atoms-card px-3 py-2.5 text-left text-xs text-zinc-400 transition-all hover:bg-white/5 hover:text-zinc-200 hover:border-white/15 flex items-start gap-1.5 group"
                >
                  <span className="flex-shrink-0 group-hover:scale-110 transition-transform">{emoji}</span>
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
