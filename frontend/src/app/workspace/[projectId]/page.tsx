"use client";

import { useEffect, useState, useCallback, useRef } from "react";
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
  MessageSquare,
  Eye,
  GripVertical,
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
import { cn } from "@/lib/utils";

type RightTab = "files" | "code" | "workflow" | "versions" | "settings";

const MODE_LABELS: Record<string, string> = {
  engineer: "💻 工程师",
  team: "👥 团队",
  race: "⚡ 竞速",
  research: "🔬 研究",
  review: "📝 评审",
};

const STATUS_MAP: Record<string, { label: string; variant: "success" | "warning" | "default" }> = {
  completed: { label: "已完成", variant: "success" },
  building: { label: "构建中", variant: "warning" },
  draft: { label: "草稿", variant: "default" },
};

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
  const [leftWidth, setLeftWidth] = useState(360);
  const [rightWidth, setRightWidth] = useState(360);
  const [isDraggingLeft, setIsDraggingLeft] = useState(false);
  const [isDraggingRight, setIsDraggingRight] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

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
        const errMsg = e instanceof Error ? e.message : "加载项目失败";
        if (errMsg.includes("Invalid token") || errMsg.includes("Not authenticated") || errMsg.includes("401")) {
          setLoadError("会话已过期，请重新登录");
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
    if (!confirm("确定要删除此项目吗？此操作不可撤销。")) return;
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
      setDeployMsg("部署成功！");
    } catch {
      setDeployMsg("部署失败 — 请先生成代码");
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
      setDeployMsg(`已恢复到 v${versionNum}`);
      setTimeout(() => setDeployMsg(""), 3000);
    } catch {
      setDeployMsg("恢复失败");
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
      nativeInputValueSetter?.call(textarea, "我发现了问题 — 请检查当前预览并修复布局、功能或样式方面的 bug。");
      textarea.dispatchEvent(new Event("input", { bubbles: true }));
      textarea.focus();
    }
  };

  const handleDragLeft = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDraggingLeft(true);
    const startX = e.clientX;
    const startWidth = leftWidth;
    const onMove = (ev: MouseEvent) => {
      const delta = ev.clientX - startX;
      setLeftWidth(Math.max(280, Math.min(600, startWidth + delta)));
    };
    const onUp = () => {
      setIsDraggingLeft(false);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }, [leftWidth]);

  const handleDragRight = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDraggingRight(true);
    const startX = e.clientX;
    const startWidth = rightWidth;
    const onMove = (ev: MouseEvent) => {
      const delta = startX - ev.clientX;
      setRightWidth(Math.max(280, Math.min(600, startWidth + delta)));
    };
    const onUp = () => {
      setIsDraggingRight(false);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }, [rightWidth]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-atoms-dark">
        <div className="flex flex-col items-center gap-3">
          <div className="relative">
            <Sparkles className="h-6 w-6 text-atoms-accent animate-spin" />
          </div>
          <span className="text-sm text-zinc-400">加载工作区...</span>
        </div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="flex h-screen items-center justify-center bg-atoms-dark">
        <div className="text-center">
          <p className="text-red-400 mb-4">{loadError}</p>
          <button onClick={() => router.push("/dashboard")} className="rounded-lg bg-atoms-accent px-4 py-2 text-sm text-white hover:bg-atoms-accent-hover transition-colors">
            返回仪表盘
          </button>
        </div>
      </div>
    );
  }

  const modeInfo = STATUS_MAP[project?.status ?? "draft"] ?? STATUS_MAP.draft;

  return (
    <div ref={containerRef} className="flex h-screen bg-atoms-dark overflow-hidden">
      {/* Left Panel - Chat */}
      <div
        className={cn(
          "flex flex-col border-r border-atoms-border transition-all duration-300 relative",
          leftOpen ? "" : "w-12 min-w-[48px]"
        )}
        style={leftOpen ? { width: leftWidth, minWidth: 280 } : undefined}
      >
        {leftOpen ? (
          <>
            <div className="flex items-center justify-between border-b border-atoms-border bg-atoms-card/50 px-3 py-2.5">
              <div className="flex items-center gap-2 min-w-0">
                <button
                  onClick={() => router.push("/dashboard")}
                  className="flex-shrink-0 rounded-lg p-1.5 text-zinc-500 hover:text-zinc-200 hover:bg-white/5 transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                </button>
                <div className="min-w-0">
                  <h2 className="text-sm font-semibold text-zinc-200 truncate">
                    {project?.name}
                  </h2>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <span className="text-[10px] text-zinc-400 bg-atoms-accent/10 px-1.5 py-0.5 rounded font-medium">
                      {MODE_LABELS[currentMode] ?? currentMode}
                    </span>
                    {project?.status && (
                      <Badge variant={modeInfo.variant}>{modeInfo.label}</Badge>
                    )}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setLeftOpen(false)}
                className="flex-shrink-0 rounded-lg p-1.5 text-zinc-500 hover:text-zinc-200 hover:bg-white/5 transition-colors"
                title="收起聊天面板"
              >
                <PanelLeftClose className="h-4 w-4" />
              </button>
            </div>
            <ChatPanel projectId={projectId} />
          </>
        ) : (
          <div className="flex flex-col items-center pt-3 gap-3">
            <button
              onClick={() => setLeftOpen(true)}
              className="rounded-lg p-1.5 text-zinc-500 hover:text-zinc-200 hover:bg-white/5 transition-colors"
              title="展开聊天面板"
            >
              <PanelLeftOpen className="h-4 w-4" />
            </button>
            <div className="w-6 h-6 rounded-full bg-atoms-accent/20 flex items-center justify-center">
              <MessageSquare className="h-3 w-3 text-atoms-accent-hover" />
            </div>
          </div>
        )}
      </div>

      {/* Left resize handle */}
      {leftOpen && (
        <div
          className={cn(
            "w-1 cursor-col-resize hover:bg-atoms-accent/30 active:bg-atoms-accent/50 transition-colors flex-shrink-0",
            isDraggingLeft && "bg-atoms-accent/40"
          )}
          onMouseDown={handleDragLeft}
        />
      )}

      {/* Center Panel - Preview */}
      <div className="flex-1 min-w-0 flex flex-col">
        <div className="flex items-center justify-between gap-2 border-b border-atoms-border bg-atoms-card/50 px-3 py-1.5">
          <div className="flex items-center gap-2">
            <Eye className="h-3.5 w-3.5 text-zinc-500" />
            <span className="text-xs font-medium text-zinc-400">预览</span>
            {deployUrl && (
              <a
                href={deployUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-[11px] font-medium bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 transition-colors border border-emerald-500/20"
              >
                <CheckCircle className="h-3 w-3" />
                已上线
                <ExternalLink className="h-2.5 w-2.5" />
              </a>
            )}
            {previewHtml && (
              <button
                onClick={handleDownload}
                className="flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium text-zinc-500 hover:text-zinc-200 hover:bg-white/5 transition-colors"
                title="下载项目文件"
              >
                <Download className="h-3 w-3" />
              </button>
            )}
            {previewHtml && (
              <button
                onClick={handleIssueReport}
                className="flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium text-zinc-500 hover:text-amber-400 hover:bg-amber-500/10 transition-colors"
                title="报告问题 / 修复 bug"
              >
                <Bug className="h-3 w-3" />
              </button>
            )}
          </div>
          <button
            onClick={handleDeploy}
            disabled={deploying}
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium bg-atoms-accent/15 text-atoms-accent-hover hover:bg-atoms-accent/25 transition-colors disabled:opacity-50 border border-atoms-accent/20"
          >
            <Rocket className="h-3.5 w-3.5" />
            {deploying ? "部署中..." : "部署"}
          </button>
        </div>
        {deployMsg && !deployUrl && (
          <div className="bg-atoms-accent/8 border-b border-atoms-accent/15 px-3 py-1 text-xs text-atoms-accent text-center">
            {deployMsg}
          </div>
        )}
        <PreviewPanel onDeploy={handleDeploy} deploying={deploying} deployMsg={deployMsg} />
      </div>

      {/* Right resize handle */}
      {rightOpen && (
        <div
          className={cn(
            "w-1 cursor-col-resize hover:bg-atoms-accent/30 active:bg-atoms-accent/50 transition-colors flex-shrink-0",
            isDraggingRight && "bg-atoms-accent/40"
          )}
          onMouseDown={handleDragRight}
        />
      )}

      {/* Right Panel - Editor/Workflow/Versions/Settings */}
      <div
        className={cn(
          "flex flex-col border-l border-atoms-border transition-all duration-300 relative",
          rightOpen ? "" : "w-12 min-w-[48px]"
        )}
        style={rightOpen ? { width: rightWidth, minWidth: 280 } : undefined}
      >
        {rightOpen ? (
          <>
            <div className="flex items-center justify-between border-b border-atoms-border bg-atoms-card/50 px-2 py-1">
              <div className="flex items-center gap-0.5 overflow-x-auto scrollbar-none">
                {(
                  [
                    { id: "files" as const, icon: FolderTree, label: "文件" },
                    { id: "code" as const, icon: Code2, label: "代码" },
                    { id: "workflow" as const, icon: Workflow, label: "工作流" },
                    { id: "versions" as const, icon: History, label: "版本" },
                    { id: "settings" as const, icon: Settings, label: "设置" },
                  ] as const
                ).map(({ id, icon: Icon, label }) => (
                  <button
                    key={id}
                    onClick={() => { setRightTab(id); if (id === "versions") refreshVersions(); }}
                    className={cn(
                      "flex items-center gap-1 rounded-lg px-2 py-1.5 text-xs font-medium transition-colors whitespace-nowrap",
                      rightTab === id
                        ? "bg-atoms-accent/15 text-atoms-accent-hover border border-atoms-accent/20"
                        : "text-zinc-500 hover:text-zinc-200 hover:bg-white/5 border border-transparent"
                    )}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {label}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setRightOpen(false)}
                className="rounded-lg p-1 text-zinc-500 hover:text-zinc-200 hover:bg-white/5 transition-colors ml-1 flex-shrink-0"
                title="收起右侧面板"
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
                    版本历史
                  </h3>
                  {versions.length === 0 ? (
                    <div className="flex flex-col items-center py-12 text-center">
                      <Code2 className="h-8 w-8 text-zinc-700 mb-3" />
                      <p className="text-xs text-zinc-500">
                        暂无版本。生成代码后将创建第一个版本。
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {versions.map((v, i) => (
                        <div
                          key={v.id}
                          className={`rounded-lg border border-atoms-border bg-atoms-card p-3 transition-colors ${
                            i === 0 ? "border-atoms-accent/30 bg-atoms-accent/3" : ""
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-zinc-200">
                                v{v.version}
                              </span>
                              {i === 0 && (
                                <Badge variant="success">最新</Badge>
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
                                {restoring === v.id ? "恢复中..." : "恢复"}
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
                    项目设置
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-zinc-500 block mb-1">
                        项目名称
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
                        项目描述
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
                        模式
                      </label>
                      <select
                        value={editMode}
                        onChange={(e) => setEditMode(e.target.value as ChatMode)}
                        className="w-full rounded-lg border border-atoms-border bg-atoms-card px-3 py-1.5 text-sm text-zinc-200 focus:border-atoms-accent focus:outline-none transition-colors"
                      >
                        <option value="engineer">💻 工程师</option>
                        <option value="team">👥 团队</option>
                        <option value="race">⚡ 竞速</option>
                        <option value="research">🔬 研究</option>
                        <option value="review">📝 评审</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 block mb-1">
                        状态
                      </label>
                      <Badge variant={modeInfo.variant}>
                        {modeInfo.label}
                      </Badge>
                    </div>
                  </div>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex items-center gap-2 rounded-lg bg-atoms-accent px-4 py-2 text-sm font-medium text-white hover:bg-atoms-accent-hover transition-colors disabled:opacity-50"
                  >
                    <Save className="h-4 w-4" />
                    {saving ? "保存中..." : "保存"}
                  </button>
                  <hr className="border-atoms-border" />
                  <button
                    onClick={handleDelete}
                    disabled={deleting}
                    className="flex items-center gap-2 rounded-lg bg-red-600/15 px-4 py-2 text-sm font-medium text-red-400 hover:bg-red-600/25 transition-colors disabled:opacity-50 border border-red-500/20"
                  >
                    <Trash2 className="h-4 w-4" />
                    {deleting ? "删除中..." : "删除项目"}
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center pt-3 gap-3">
            <button
              onClick={() => setRightOpen(true)}
              className="rounded-lg p-1.5 text-zinc-500 hover:text-zinc-200 hover:bg-white/5 transition-colors"
              title="展开右侧面板"
            >
              <PanelRightOpen className="h-4 w-4" />
            </button>
            <div className="w-6 h-6 rounded-full bg-atoms-accent/20 flex items-center justify-center">
              <Code2 className="h-3 w-3 text-atoms-accent-hover" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
