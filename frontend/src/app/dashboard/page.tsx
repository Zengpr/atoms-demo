"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Sparkles,
  Plus,
  LogOut,
  LayoutDashboard,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ProjectCard } from "@/components/dashboard/ProjectCard";
import { TemplateCard } from "@/components/dashboard/TemplateCard";
import { useAuthStore, useProjectStore } from "@/lib/store";
import type { CreateProjectData, ChatMode } from "@/lib/types";

const TEMPLATES = [
  {
    icon: "\u{1F3E0}",
    name: "Landing Page",
    description: "A beautiful, conversion-optimized landing page",
  },
  {
    icon: "\u{1F4CA}",
    name: "Dashboard",
    description: "Data dashboard with charts and metrics",
  },
  {
    icon: "\u{1F6D2}",
    name: "E-commerce",
    description: "Online store with product catalog and cart",
  },
  {
    icon: "\u{1F3A8}",
    name: "Portfolio",
    description: "Creative portfolio showcasing your work",
  },
];

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout, loadUser } = useAuthStore();
  const { projects, loadProjects, createProject } = useProjectStore();
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectMode, setNewProjectMode] = useState<ChatMode>("team");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser().finally(() => setLoading(false));
  }, [loadUser]);

  useEffect(() => {
    if (isAuthenticated) {
      loadProjects();
    }
  }, [isAuthenticated, loadProjects]);

  const handleCreateFromTemplate = async (templateName: string) => {
    const data: CreateProjectData = {
      name: templateName,
      description: `A ${templateName.toLowerCase()} built with Atoms AI`,
      mode: "team",
      template: templateName.toLowerCase().replace(/\s+/g, "-"),
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
      {/* Sidebar */}
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
            <div className="grid grid-cols-2 gap-2">
              {(["engineer", "team", "race", "research"] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setNewProjectMode(m)}
                  className={`rounded-lg py-1.5 text-xs font-medium transition-colors ${
                    newProjectMode === m
                      ? "bg-atoms-accent text-white"
                      : "bg-atoms-dark text-zinc-400 border border-atoms-border"
                  }`}
                >
                  {m === "engineer" ? "Engineer" : m === "team" ? "Team" : m === "race" ? "Race" : "Research"}
                </button>
              ))}
            </div>
            <Button type="submit" size="sm" className="w-full">
              Create
            </Button>
          </motion.form>
        )}

        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 scrollbar-thin">
          {projects.map((p) => (
            <button
              key={p.id}
              onClick={() => router.push(`/workspace/${p.id}`)}
              className="w-full rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-white/5 text-zinc-300"
            >
              <div className="truncate font-medium">{p.name}</div>
              <div className="text-xs text-zinc-500 flex items-center gap-2 mt-0.5">
                <span>{p.mode}</span>
                <span className="h-1 w-1 rounded-full bg-zinc-600" />
                <span>{p.status}</span>
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

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        {!currentProject ? (
          <div className="px-8 py-10">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center gap-3 mb-8">
                <LayoutDashboard className="h-8 w-8 text-atoms-accent" />
                <div>
                  <h1 className="text-2xl font-bold text-white">
                    Welcome back, {user?.username}
                  </h1>
                  <p className="text-zinc-400">
                    Start a new project or continue working on an existing one
                  </p>
                </div>
              </div>

              {/* Templates */}
              <div className="mb-10">
                <h2 className="text-lg font-semibold text-zinc-200 mb-4">
                  Start from a template
                </h2>
                <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                  {TEMPLATES.map((t) => (
                    <TemplateCard
                      key={t.name}
                      icon={t.icon}
                      name={t.name}
                      description={t.description}
                      onClick={() => handleCreateFromTemplate(t.name)}
                    />
                  ))}
                </div>
              </div>

              {/* Recent Projects */}
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
        ) : (
          <div className="flex h-full items-center justify-center">
            <p className="text-zinc-400">
              Select a project from the sidebar or create a new one
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
