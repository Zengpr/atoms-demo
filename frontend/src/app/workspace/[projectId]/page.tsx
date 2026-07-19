"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Sparkles,
  ArrowLeft,
  Code2,
  Workflow,
  Settings,
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  Trash2,
  Save,
  Rocket,
} from "lucide-react";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { PreviewPanel } from "@/components/preview/PreviewPanel";
import { CodeEditor } from "@/components/editor/CodeEditor";
import { WorkflowPanel } from "@/components/editor/WorkflowPanel";
import { useProjectStore, useChatStore, usePreviewStore, useAuthStore } from "@/lib/store";
import { Badge } from "@/components/ui/Badge";
import type { Project, ChatMode } from "@/lib/types";
import { projectApi } from "@/lib/api";

type RightTab = "code" | "workflow" | "settings";

export default function WorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;

  const { selectProject, currentProject } = useProjectStore();
  const { messages, clearMessages, loadHistory, currentMode } = useChatStore();
  const { setPreviewHtml } = usePreviewStore();

  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);
  const [rightTab, setRightTab] = useState<RightTab>("code");
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");
  const [editMode, setEditMode] = useState<ChatMode>("engineer");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deploying, setDeploying] = useState(false);
  const [deployMsg, setDeployMsg] = useState("");
  const { token } = useAuthStore();

  useEffect(() => {
    async function load() {
      try {
        const p = await projectApi.get(projectId);
        setProject(p);
        setEditName(p.name);
        setEditDesc(p.description ?? "");
        setEditMode(p.mode);
        selectProject(p);
        await loadHistory(projectId);
        try {
          const { code } = await projectApi.getLatestCode(projectId);
          if (code) setPreviewHtml(code);
        } catch {}
      } catch (e: unknown) {
        const errMsg = e instanceof Error ? e.message : "Failed to load project";
        if (errMsg.includes("Invalid token") || errMsg.includes("Not authenticated") || errMsg.includes("401")) {
          setLoadError("Session expired. Please sign in again.");
          setTimeout(() => router.push("/login"), 2000);
        } else {
          setLoadError(errMsg);
        }
      } finally {
        setLoading(false);
      }
    }
    load();
    return () => clearMessages();
  }, [projectId, selectProject, loadHistory, clearMessages, router, setPreviewHtml]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await projectApi.update(projectId, {
        name: editName,
        description: editDesc,
        mode: editMode,
      });
      setProject(updated);
      selectProject(updated);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this project? This action cannot be undone.")) return;
    setDeleting(true);
    try {
      await projectApi.delete(projectId);
      router.push("/dashboard");
    } finally {
      setDeleting(false);
    }
  };

  const handleDeploy = async () => {
    setDeploying(true);
    setDeployMsg("");
    try {
      await fetch(`/api/preview/${projectId}/deploy`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      setDeployMsg("Deployed!");
      setTimeout(() => setDeployMsg(""), 3000);
    } catch {
      setDeployMsg("Deploy failed");
      setTimeout(() => setDeployMsg(""), 3000);
    } finally {
      setDeploying(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-atoms-dark">
        <div className="flex items-center gap-3 text-zinc-400">
          <Sparkles className="h-5 w-5 text-atoms-accent animate-spin" />
          Loading workspace...
        </div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="flex h-screen items-center justify-center bg-atoms-dark">
        <div className="text-center">
          <p className="text-red-400 mb-4">{loadError}</p>
          <button onClick={() => router.push("/dashboard")} className="rounded-lg bg-atoms-accent px-4 py-2 text-sm text-white">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-atoms-dark">
      {/* Left Panel - Chat */}
      <div
        className={`flex flex-col border-r border-atoms-border transition-all duration-300 ${
          leftOpen ? "w-[30%] min-w-[320px]" : "w-12 min-w-[48px]"
        }`}
      >
        {leftOpen ? (
          <>
            <div className="flex items-center justify-between border-b border-atoms-border px-4 py-3">
              <div className="flex items-center gap-2 min-w-0">
                <button
                  onClick={() => router.push("/dashboard")}
                  className="flex-shrink-0 rounded-lg p-1 text-zinc-500 hover:text-zinc-200 transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                </button>
                <div className="min-w-0">
                  <h2 className="text-sm font-semibold text-zinc-200 truncate">
                    {project?.name}
                  </h2>
                  <div className="flex items-center gap-2">
                    <Badge>{currentMode}</Badge>
                    {project?.status && <Badge variant={project.status === "completed" ? "success" : project.status === "building" ? "warning" : "default"}>{project.status}</Badge>}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setLeftOpen(false)}
                className="flex-shrink-0 rounded-lg p-1 text-zinc-500 hover:text-zinc-200 transition-colors"
              >
                <PanelLeftClose className="h-4 w-4" />
              </button>
            </div>
            <ChatPanel projectId={projectId} />
          </>
        ) : (
          <button
            onClick={() => setLeftOpen(true)}
            className="flex h-full items-center justify-center text-zinc-500 hover:text-zinc-200 transition-colors"
          >
            <PanelLeftOpen className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Center Panel - Preview */}
      <div className="flex-1 min-w-0 flex flex-col">
        <div className="flex items-center justify-end gap-2 border-b border-atoms-border bg-atoms-card px-3 py-1.5">
          <button
            onClick={handleDeploy}
            disabled={deploying}
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium bg-atoms-accent/20 text-atoms-accent-hover hover:bg-atoms-accent/30 transition-colors disabled:opacity-50"
          >
            <Rocket className="h-3.5 w-3.5" />
            {deploying ? "Deploying..." : "Deploy"}
          </button>
          {deployMsg && (
            <span className="text-xs text-atoms-accent">{deployMsg}</span>
          )}
        </div>
        <PreviewPanel projectId={projectId} onDeploy={handleDeploy} deploying={deploying} deployMsg={deployMsg} />
      </div>

      {/* Right Panel - Editor/Workflow/Settings */}
      <div
        className={`flex flex-col border-l border-atoms-border transition-all duration-300 ${
          rightOpen ? "w-[30%] min-w-[320px]" : "w-12 min-w-[48px]"
        }`}
      >
        {rightOpen ? (
          <>
            <div className="flex items-center justify-between border-b border-atoms-border px-2 py-1">
              <div className="flex items-center gap-1">
                {(
                  [
                    { id: "code" as const, icon: Code2, label: "Code" },
                    { id: "workflow" as const, icon: Workflow, label: "Workflow" },
                    { id: "settings" as const, icon: Settings, label: "Settings" },
                  ] as const
                ).map(({ id, icon: Icon, label }) => (
                  <button
                    key={id}
                    onClick={() => setRightTab(id)}
                    className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-colors ${
                      rightTab === id
                        ? "bg-atoms-accent/20 text-atoms-accent-hover"
                        : "text-zinc-500 hover:text-zinc-200 hover:bg-white/5"
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {label}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setRightOpen(false)}
                className="rounded-lg p-1 text-zinc-500 hover:text-zinc-200 transition-colors"
              >
                <PanelRightClose className="h-4 w-4" />
              </button>
            </div>

            <div className="flex-1 min-h-0">
              {rightTab === "code" && <CodeEditor />}
              {rightTab === "workflow" && <WorkflowPanel messages={messages} />}
              {rightTab === "settings" && (
                <div className="p-4 space-y-4">
                  <h3 className="text-sm font-semibold text-zinc-200">
                    Project Settings
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-zinc-500 block mb-1">
                        Name
                      </label>
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="w-full rounded-lg border border-atoms-border bg-atoms-card px-3 py-1.5 text-sm text-zinc-200 focus:border-atoms-accent focus:outline-none transition-colors"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 block mb-1">
                        Description
                      </label>
                      <textarea
                        value={editDesc}
                        onChange={(e) => setEditDesc(e.target.value)}
                        rows={3}
                        className="w-full rounded-lg border border-atoms-border bg-atoms-card px-3 py-1.5 text-sm text-zinc-200 focus:border-atoms-accent focus:outline-none transition-colors resize-none"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 block mb-1">
                        Mode
                      </label>
                      <select
                        value={editMode}
                        onChange={(e) => setEditMode(e.target.value as ChatMode)}
                        className="w-full rounded-lg border border-atoms-border bg-atoms-card px-3 py-1.5 text-sm text-zinc-200 focus:border-atoms-accent focus:outline-none transition-colors"
                      >
                        <option value="engineer">engineer</option>
                        <option value="team">team</option>
                        <option value="race">race</option>
                        <option value="research">research</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 block mb-1">
                        Status
                      </label>
                      <Badge
                        variant={
                          project?.status === "completed"
                            ? "success"
                            : project?.status === "building"
                              ? "warning"
                              : "default"
                        }
                      >
                        {project?.status ?? "draft"}
                      </Badge>
                    </div>
                  </div>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex items-center gap-2 rounded-lg bg-atoms-accent px-4 py-2 text-sm font-medium text-white hover:bg-atoms-accent-hover transition-colors disabled:opacity-50"
                  >
                    <Save className="h-4 w-4" />
                    {saving ? "Saving..." : "Save"}
                  </button>
                  <hr className="border-atoms-border" />
                  <button
                    onClick={handleDelete}
                    disabled={deleting}
                    className="flex items-center gap-2 rounded-lg bg-red-600/20 px-4 py-2 text-sm font-medium text-red-400 hover:bg-red-600/30 transition-colors disabled:opacity-50"
                  >
                    <Trash2 className="h-4 w-4" />
                    {deleting ? "Deleting..." : "Delete Project"}
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <button
            onClick={() => setRightOpen(true)}
            className="flex h-full items-center justify-center text-zinc-500 hover:text-zinc-200 transition-colors"
          >
            <PanelRightOpen className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
