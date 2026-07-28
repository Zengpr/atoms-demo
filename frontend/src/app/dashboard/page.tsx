"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Sparkles,
  Plus,
  LogOut,
  Zap,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ProjectCard } from "@/components/dashboard/ProjectCard";
import { TemplateCard } from "@/components/dashboard/TemplateCard";
import { useAuthStore, useProjectStore } from "@/lib/store";
import { AGENTS, WORKFLOW_STEPS, getAgentColor, getAgentByName } from "@/lib/agents";
import type { CreateProjectData, ChatMode, Template } from "@/lib/types";
import { projectApi } from "@/lib/api";
import Image from "next/image";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout, loadUser } = useAuthStore();
  const { projects, loadProjects, createProject } = useProjectStore();
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectMode, setNewProjectMode] = useState<ChatMode>("team");
  const [loading, setLoading] = useState(true);
  const [templates, setTemplates] = useState<Template[]>([]);

  useEffect(() => {
    loadUser().finally(() => setLoading(false));
  }, [loadUser]);

  useEffect(() => {
    if (isAuthenticated) {
      loadProjects();
    }
  }, [isAuthenticated, loadProjects]);

  useEffect(() => {
    projectApi.getTemplates().then(setTemplates).catch(() => {});
  }, []);

  const handleCreateFromTemplate = async (template: Template) => {
    const data: CreateProjectData = {
      name: template.name,
      description: template.description,
      mode: template.mode as ChatMode,
      template: template.id,
    };
    const project = await createProject(data);
    router.push(`/workspace/${project.id}`);
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    const data: CreateProjectData = {
      name: newProjectName.trim(),
      description: "",
      mode: newProjectMode,
    };
    const project = await createProject(data);
    setShowNewProject(false);
    setNewProjectName("");
    router.push(`/workspace/${project.id}`);
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-2 text-zinc-400">
          <Sparkles className="h-5 w-5 text-atoms-accent animate-spin" />
          Loading...
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-zinc-400 mb-4">Please sign in to continue</p>
          <Button onClick={() => router.push("/login")}>Sign In</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      <aside className="w-64 flex-shrink-0 border-r border-atoms-border bg-atoms-card flex flex-col">
        <div className="flex items-center gap-2 px-4 py-5 border-b border-atoms-border">
          <Sparkles className="h-5 w-5 text-atoms-accent" />
          <span className="text-base font-bold text-white">Atoms Demo</span>
        </div>

        <div className="px-4 py-3">
          <Button
            onClick={() => setShowNewProject(!showNewProject)}
            className="w-full"
            size="sm"
          >
            <Plus className="h-4 w-4" />
            New Project
          </Button>
        </div>

        {showNewProject && (
          <motion.form
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            onSubmit={handleCreateProject}
            className="px-4 pb-3 space-y-2"
          >
            <input
              type="text"
              placeholder="Project name"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              className="w-full rounded-lg border border-atoms-border bg-atoms-dark px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-atoms-accent"
              autoFocus
            />
            <div className="grid grid-cols-2 gap-1.5">
              {(["engineer", "team", "race", "research"] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setNewProjectMode(m)}
                  className={`rounded-lg py-1.5 text-xs font-medium transition-all ${
                    newProjectMode === m
                      ? "bg-atoms-accent text-white shadow-sm shadow-atoms-accent/20"
                      : "bg-atoms-dark text-zinc-400 border border-atoms-border hover:border-white/20"
                  }`}
                >
                  {m === "team" ? "Team" : m === "engineer" ? "Engineer" : m === "race" ? "Race" : "Research"}
                </button>
              ))}
            </div>
            <Button type="submit" size="sm" className="w-full">
              Create
            </Button>
          </motion.form>
        )}

        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-0.5 scrollbar-thin">
          {projects.map((p) => (
            <button
              key={p.id}
              onClick={() => router.push(`/workspace/${p.id}`)}
              className="w-full rounded-lg px-3 py-2 text-left text-sm transition-all hover:bg-white/5 text-zinc-300 group"
            >
              <div className="truncate font-medium group-hover:text-white transition-colors">{p.name}</div>
              <div className="text-xs text-zinc-500 flex items-center gap-2 mt-0.5">
                <span className="text-[10px] bg-white/5 px-1.5 py-0.5 rounded">{p.mode === "team" ? "Team" : p.mode === "engineer" ? "Engineer" : p.mode}</span>
                <span className={`h-1.5 w-1.5 rounded-full ${p.status === "completed" ? "bg-emerald-500" : p.status === "building" ? "bg-amber-500" : "bg-zinc-600"}`} />
                <span>{p.status === "completed" ? "Completed" : p.status === "building" ? "Building" : "Draft"}</span>
              </div>
            </button>
          ))}
        </div>

        <div className="border-t border-atoms-border px-4 py-3">
          <div className="flex items-center gap-2 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-atoms-accent/20 text-atoms-accent text-xs font-bold">
              {user?.username?.charAt(0).toUpperCase() ?? "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-zinc-200 truncate">
                {user?.username}
              </p>
              <p className="text-xs text-zinc-500 truncate">{user?.email}</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" className="w-full" onClick={handleLogout}>
            <LogOut className="h-3.5 w-3.5" />
            Sign Out
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="px-8 py-10">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="mb-10">
              <h1 className="text-3xl font-bold text-white mb-2">
                Your AI Team
              </h1>
              <p className="text-zinc-400 max-w-xl leading-relaxed">
                8 specialized AI Agents working together. Describe what you want to build — they handle research, planning, construction, testing, and growth.
              </p>
            </div>

            <div className="grid grid-cols-4 gap-3 mb-10">
              {AGENTS.map((agent, i) => (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className="agent-card-atoms rounded-xl border border-atoms-border bg-atoms-card p-4 text-center cursor-pointer hover:bg-atoms-surface-hover"
                  style={{ "--hover-color": `${agent.color}40` } as React.CSSProperties}
                >
                  <div className="flex justify-center mb-3">
                    <Image
                      src={agent.avatarUrl}
                      alt={agent.name}
                      width={56}
                      height={56}
                      className="agent-avatar-img"
                      style={{ borderColor: `${agent.color}30`, borderWidth: 2 }}
                      unoptimized
                    />
                  </div>
                  <h3 className="text-sm font-semibold text-zinc-200 mb-1">{agent.name}</h3>
                  <span
                    className="inline-block text-[10px] px-2 py-0.5 rounded-full mb-2 font-medium"
                    style={{ backgroundColor: `${agent.color}15`, color: agent.color }}
                  >
                    {agent.role}
                  </span>
                  <p className="text-xs text-zinc-500 leading-relaxed">{agent.description}</p>
                </motion.div>
              ))}
            </div>

            <div className="mb-10 glass-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="h-4 w-4 text-atoms-accent" />
                <h2 className="text-sm font-semibold text-zinc-200">Team Workflow</h2>
              </div>
              <div className="flex items-center gap-1">
                {WORKFLOW_STEPS.map((step, i) => {
                  const agentInfo = getAgentByName(step.agent);
                  const agentColor = getAgentColor(step.agent);
                  return (
                    <div key={step.key} className="flex items-center gap-1">
                      <div className="flex flex-col items-center">
                        <div
                          className="w-10 h-10 rounded-full flex items-center justify-center transition-all"
                          style={{ backgroundColor: `${agentColor}10`, border: `1px solid ${agentColor}20` }}
                        >
                          {agentInfo?.avatarUrl ? (
                            <Image src={agentInfo.avatarUrl} alt={step.agent} width={24} height={24} className="rounded-full" unoptimized />
                          ) : (
                            <span className="text-xs">{step.icon}</span>
                          )}
                        </div>
                        <span className="text-[10px] text-zinc-400 mt-1 font-medium">{step.label}</span>
                        <span className="text-[9px] text-zinc-600">{step.agent}</span>
                      </div>
                      {i < WORKFLOW_STEPS.length - 1 && (
                        <ArrowRight className="h-3.5 w-3.5 text-zinc-700 flex-shrink-0" />
                      )}
                    </div>
                  );
                })}
              </div>
              <p className="text-xs text-zinc-500 mt-3">
                Agents auto-execute the pipeline \u2014 you stay in control with live visibility.
              </p>
            </div>

            {templates.length > 0 && (
              <div className="mb-10">
                <h2 className="text-lg font-semibold text-zinc-200 mb-4">
                  Start from Template
                </h2>
                <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                  {templates.map((t) => (
                    <TemplateCard
                      key={t.id}
                      icon={t.icon}
                      name={t.name}
                      description={t.description}
                      onClick={() => handleCreateFromTemplate(t)}
                    />
                  ))}
                </div>
              </div>
            )}

            {projects.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-zinc-200 mb-4">
                  Recent Projects
                </h2>
                <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                  {projects.map((p) => (
                    <ProjectCard key={p.id} project={p} />
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
