"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";

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
  History,
  RotateCcw,
  ExternalLink,
  CheckCircle,
  FolderTree,
  Download,
  Bug,
} from "lucide-react";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { PreviewPanel } from "@/components/preview/PreviewPanel";
import { CodeEditor } from "@/components/editor/CodeEditor";
import { WorkflowPanel } from "@/components/editor/WorkflowPanel";
import { FileTree } from "@/components/editor/FileTree";
import { useProjectStore, useChatStore, usePreviewStore, useAuthStore } from "@/lib/store";
import { Badge } from "@/components/ui/Badge";
import type { Project, ChatMode, CodeVersion } from "@/lib/types";
import { projectApi, previewApi } from "@/lib/api";

type RightTab = "files" | "code" | "workflow" | "versions" | "settings";

export default function WorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;

  const { selectProject } = useProjectStore();
  const { messages, clearMessages, loadHistory, currentMode, setMode } = useChatStore();
  const { setPreviewHtml } = usePreviewStore();
  const { previewHtml } = usePreviewStore();

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
  const [deployUrl, setDeployUrl] = useState("");
  const [deployMsg, setDeployMsg] = useState("");
  const [versions, setVersions] = useState<CodeVersion[]>([]);
  const [restoring, setRestoring] = useState("");
  const { token } = useAuthStore();

  useEffect(() => {
    async function load() {
      try {
        const p = await projectApi.get(projectId);
        setProject(p);
        setEditName(p.name);
        setEditDesc(p.description ?? "");
        setEditMode(p.mode);
        setMode(p.mode);
        selectProject(p);
        await loadHistory(projectId);
        try {
          const { code } = await projectApi.getLatestCode(projectId);
          if (code) setPreviewHtml(code);
        } catch {}
        try {
          const v = await projectApi.getVersions(projectId);
          setVersions(v);
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

  const refreshVersions = useCallback(async () => {
    try {
      const v = await projectApi.getVersions(projectId);
      setVersions(v);
    } catch {}
  }, [projectId]);

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
    setDeployUrl("");
    try {
      const result = await projectApi.deploy(projectId);
      const fullUrl = previewApi.getPublicUrl(result.page_id);
      setDeployUrl(fullUrl);
      setDeployMsg("Deployed!");
    } catch {
      setDeployMsg("Deploy failed — generate code first");
      setTimeout(() => setDeployMsg(""), 3000);
    } finally {
      setDeploying(false);
    }
  };

  const handleRestore = async (versionId: string, versionNum: number) => {
    setRestoring(versionId);
    try {
      await projectApi.restoreVersion(projectId, versionId);
      const { code } = await projectApi.getLatestCode(projectId);
      if (code) setPreviewHtml(code);
      await refreshVersions();
      setDeployMsg(`Restored to v${versionNum}`);
      setTimeout(() => setDeployMsg(""), 3000);
    } catch {
      setDeployMsg("Restore failed");
      setTimeout(() => setDeployMsg(""), 3000);
    } finally {
      setRestoring("");
    }
  };

  const handleDownload = () => {
    if (!previewHtml) return;
    const blob = new Blob([previewHtml], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${project?.name ?? "app"}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleIssueReport = () => {
    const textarea = document.querySelector<HTMLTextAreaElement>("textarea");
    if (textarea) {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
      nativeInputValueSetter?.call(textarea, "I found an issue — please review the current preview and fix any layout, functionality, or style bugs.");
      textarea.dispatchEvent(new Event("input", { bubbles: true }));
      textarea.focus();
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
                    <Badge>{currentMode === "team" ? "Team" : currentMode === "engineer" ? "Engineer" : currentMode === "race" ? "Race" : currentMode === "research" ? "Research" : currentMode}</Badge>
                    {project?.status && <Badge variant={project.status === "completed" ? "success" : project.status === "building" ? "warning" : "default"}>{project.status === "completed" ? "Completed" : project.status === "building" ? "Building" : "Draft"}</Badge>}
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
        <div className="flex items-center justify-between gap-2 border-b border-atoms-border bg-atoms-card px-3 py-1.5">
          <div className="flex items-center gap-2">
            {deployUrl && (
              <a
                href={deployUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 transition-colors"
              >
                <CheckCircle className="h-3.5 w-3.5" />
                Live
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
            {previewHtml && (
              <button
                onClick={handleDownload}
                className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-white/5 transition-colors"
                title="Download project files"
              >
                <Download className="h-3.5 w-3.5" />
              </button>
            )}
            {previewHtml && (
              <button
                onClick={handleIssueReport}
                className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-zinc-400 hover:text-amber-400 hover:bg-amber-500/10 transition-colors"
                title="Report an issue / Fix bug"
              >
                <Bug className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
          <button
            onClick={handleDeploy}
            disabled={deploying}
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium bg-atoms-accent/20 text-atoms-accent-hover hover:bg-atoms-accent/30 transition-colors disabled:opacity-50"
          >
            <Rocket className="h-3.5 w-3.5" />
            {deploying ? "Deploying..." : "Deploy"}
          </button>
        </div>
        {deployMsg && !deployUrl && (
          <div className="bg-atoms-accent/10 px-3 py-1 text-xs text-atoms-accent text-center">
            {deployMsg}
          </div>
        )}
        <PreviewPanel onDeploy={handleDeploy} deploying={deploying} deployMsg={deployMsg} />
      </div>

      {/* Right Panel - Editor/Workflow/Versions/Settings */}
      <div
        className={`flex flex-col border-l border-atoms-border transition-all duration-300 ${
          rightOpen ? "w-[30%] min-w-[320px]" : "w-12 min-w-[48px]"
        }`}
      >
        {rightOpen ? (
          <>
            <div className="flex items-center justify-between border-b border-atoms-border px-2 py-1">
              <div className="flex items-center gap-0.5 overflow-x-auto scrollbar-none">
                {(
                  [
                    { id: "files" as const, icon: FolderTree, label: "Files" },
                    { id: "code" as const, icon: Code2, label: "Code" },
                    { id: "workflow" as const, icon: Workflow, label: "Workflow" },
                    { id: "versions" as const, icon: History, label: "Versions" },
                    { id: "settings" as const, icon: Settings, label: "Settings" },
                  ] as const
                ).map(({ id, icon: Icon, label }) => (
                  <button
                    key={id}
                    onClick={() => { setRightTab(id); if (id === "versions") refreshVersions(); }}
                    className={`flex items-center gap-1 rounded-lg px-2 py-1.5 text-xs font-medium transition-colors whitespace-nowrap ${
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
              {rightTab === "files" && <FileTree />}
              {rightTab === "code" && <CodeEditor />}
              {rightTab === "workflow" && <WorkflowPanel messages={messages} />}
              {rightTab === "versions" && (
                <div className="p-4 space-y-3 overflow-y-auto h-full">
                  <h3 className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
                    <History className="h-4 w-4" />
                    Version History
                  </h3>
                  {versions.length === 0 ? (
                    <p className="text-xs text-zinc-500 py-8 text-center">
                      No versions yet. Generate code to create your first version.
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {versions.map((v, i) => (
                        <div
                          key={v.id}
                          className={`rounded-lg border border-atoms-border bg-atoms-card p-3 ${
                            i === 0 ? "border-atoms-accent/30" : ""
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-zinc-200">
                                v{v.version}
                              </span>
                              {i === 0 && (
                                <Badge variant="success">latest</Badge>
                              )}
                            </div>
                            <span className="text-xs text-zinc-500">
                              {v.codeFull ? `${(v.codeFull.length / 1024).toFixed(1)}KB` : "—"}
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-zinc-500">
                              {v.createdAt ? new Date(v.createdAt).toLocaleString() : ""}
                            </span>
                            {i !== 0 && (
                              <button
                                onClick={() => handleRestore(v.id, v.version)}
                                disabled={restoring === v.id}
                                className="flex items-center gap-1 rounded px-2 py-1 text-xs text-atoms-accent hover:bg-atoms-accent/10 transition-colors disabled:opacity-50"
                              >
                                <RotateCcw className="h-3 w-3" />
                                {restoring === v.id ? "Restoring..." : "Restore"}
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              {rightTab === "settings" && (
                <div className="p-4 space-y-4 overflow-y-auto h-full">
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
                        <option value="review">review</option>
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
