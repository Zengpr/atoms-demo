"use client";

import { motion } from "framer-motion";
import { AGENTS, getAgentColor, getAgentByName } from "@/lib/agents";
import { cn } from "@/lib/utils";
import type { Message } from "@/lib/types";
import Image from "next/image";
import { CheckCircle2, Loader2, Circle } from "lucide-react";

interface WorkflowStep {
  agentName: string;
  action: string;
  output?: string;
  duration?: number;
  status: "pending" | "running" | "done";
}

interface WorkflowPanelProps {
  messages: Message[];
}

function extractSteps(messages: Message[]): WorkflowStep[] {
  const steps: WorkflowStep[] = [];
  for (const msg of messages) {
    if (!msg.agentName) continue;
    if (msg.role === "assistant") {
      steps.push({
        agentName: msg.agentName,
        action: msg.content.slice(0, 80),
        output: msg.content,
        status: "done",
      });
      continue;
    }
    if (msg.role !== "agent") continue;
    const actions = msg.metadata?.actions;
    if (actions && Array.isArray(actions)) {
      for (const action of actions as { label: string; status: string }[]) {
        steps.push({
          agentName: msg.agentName,
          action: action.label,
          status: (action.status === "done"
            ? "done"
            : action.status === "running"
              ? "running"
              : "pending") as WorkflowStep["status"],
        });
      }
    } else if (msg.metadata?.thinking === true) {
      steps.push({
        agentName: msg.agentName,
        action: (msg.metadata?.message as string ?? msg.content).slice(0, 80),
        status: "running",
      });
    } else if (msg.metadata?.action === true || msg.content) {
      steps.push({
        agentName: msg.agentName,
        action: msg.content.slice(0, 80),
        output: msg.content,
        status: "done",
      });
    }
  }
  return steps;
}

export function WorkflowPanel({ messages }: WorkflowPanelProps) {
  const steps = extractSteps(messages);

  return (
    <div className="h-full overflow-y-auto p-4 space-y-1 scrollbar-thin">
      {steps.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="text-3xl mb-3 opacity-30">{"\u{1F3D7}\u{FE0F}"}</div>
          <p className="text-sm text-zinc-500">
            Agent 工作流将在此显示
          </p>
        </div>
      ) : (
        <div className="relative">
          <div className="absolute left-[15px] top-4 bottom-0 w-px bg-atoms-border" />
          {steps.map((step, i) => {
            const agent = getAgentByName(step.agentName);
            const agentColor = getAgentColor(step.agentName);
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="relative flex items-start gap-3 pb-4"
              >
                <div className="relative z-10 flex-shrink-0">
                  {agent?.avatarUrl ? (
                    <Image
                      src={agent.avatarUrl}
                      alt={step.agentName}
                      width={32}
                      height={32}
                      className="agent-avatar-img"
                      style={{ borderColor: `${agentColor}30`, borderWidth: 1.5 }}
                      unoptimized
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full flex items-center justify-center bg-atoms-card border border-atoms-border text-sm">
                      {AGENTS.find(a => a.name === step.agentName)?.avatarEmoji ?? "\u{1F916}"}
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0 pt-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium" style={{ color: agentColor }}>
                      {step.agentName}
                    </span>
                    <span className="text-[10px] text-zinc-500 bg-white/5 px-1.5 py-0.5 rounded">
                      {agent?.role}
                    </span>
                    <span className="ml-auto flex-shrink-0">
                      {step.status === "done" ? (
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                      ) : step.status === "running" ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin text-amber-400" />
                      ) : (
                        <Circle className="h-3.5 w-3.5 text-zinc-600" />
                      )}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400 mt-0.5 line-clamp-2 leading-relaxed">
                    {step.action}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
