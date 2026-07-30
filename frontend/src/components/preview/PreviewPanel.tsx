"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import { Monitor, Tablet, Smartphone, RotateCw, ExternalLink, Rocket, FolderTree, Eye, AlertTriangle, X, Code2, Layers } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePreviewStore } from "@/lib/store";
import { motion } from "framer-motion";

type Viewport = "desktop" | "tablet" | "mobile";
type RightView = "preview" | "files";

const VIEWPORT_CONFIG: Record<Viewport, { width: string; label: string }> = {
  desktop: { width: "100%", label: "桌面端" },
  tablet: { width: "768px", label: "平板" },
  mobile: { width: "375px", label: "移动端" },
};

interface VirtualFile {
  name: string;
  language: string;
  content: string;
  icon: string;
}

function extractFiles(html: string): VirtualFile[] {
  const files: VirtualFile[] = [];
  let cssContent = "";
  const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  let match;
  while ((match = styleRegex.exec(html)) !== null) {
    cssContent += match[1].trim() + "\n";
  }
  let jsContent = "";
  const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
  while ((match = scriptRegex.exec(html)) !== null) {
    const attrs = match[0].slice(0, match[0].indexOf(">"));
    if (!attrs.includes("src=")) {
      jsContent += match[1].trim() + "\n";
    }
  }
  const htmlOnly = html
    .replace(styleRegex, '<link rel="stylesheet" href="style.css">')
    .replace(scriptRegex, '<script src="script.js"></script>');
  files.push({ name: "index.html", language: "html", content: htmlOnly.trim(), icon: "\u{1F7E7}" });
  if (cssContent) files.push({ name: "style.css", language: "css", content: cssContent.trim(), icon: "\u{1F7E6}" });
  if (jsContent) files.push({ name: "script.js", language: "javascript", content: jsContent.trim(), icon: "\u{1F7E8}" });
  return files;
}

interface PreviewPanelProps {
  onDeploy?: () => void;
  deploying?: boolean;
  deployMsg?: string;
}

export function PreviewPanel({ }: PreviewPanelProps) {
  const { previewHtml, consoleErrors, addConsoleError, clearConsoleErrors } = usePreviewStore();
  const [viewport, setViewport] = useState<Viewport>("desktop");
  const [refreshKey, setRefreshKey] = useState(0);
  const [rightView, setRightView] = useState<RightView>("preview");
  const [selectedFile, setSelectedFile] = useState<string>("index.html");
  const [showConsole, setShowConsole] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const files = useMemo(() => previewHtml ? extractFiles(previewHtml) : [], [previewHtml]);
  const currentFile = files.find((f) => f.name === selectedFile);

  const handleRefresh = () => {
    setRefreshKey((k) => k + 1);
    clearConsoleErrors();
  };

  const handleOpenNew = () => {
    const win = window.open("", "_blank");
    if (win && previewHtml) {
      win.document.write(previewHtml);
      win.document.close();
    }
  };

  useEffect(() => {
    const handler = (e: MessageEvent) => {
      if (e.data && e.data.type === "iframe-error") {
        addConsoleError({
          message: e.data.message || "Unknown error",
          line: e.data.line,
          source: e.data.source,
        });
      }
    };
    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, [addConsoleError]);

  const iframeSrcDoc = useMemo(() => {
    if (!previewHtml) return undefined;
    const errorCatch = `<script>
window.onerror=function(msg,src,line,col,err){
  window.parent.postMessage({type:'iframe-error',message:String(msg),source:src||'',line:line||0},'*');
};
window.addEventListener('unhandledrejection',function(e){
  window.parent.postMessage({type:'iframe-error',message:'Unhandled: '+String(e.reason),'':'',line:0},'*');
});
</script>`;
    return previewHtml.replace("<head>", "<head>" + errorCatch);
  }, [previewHtml]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-atoms-border bg-atoms-card/50 px-3 py-1.5">
        <div className="flex items-center gap-0.5 rounded-lg bg-atoms-dark/60 p-0.5">
          {(["desktop", "tablet", "mobile"] as const).map((v) => {
            const icons = { desktop: Monitor, tablet: Tablet, mobile: Smartphone };
            const Icon = icons[v];
            return (
              <button
                key={v}
                onClick={() => setViewport(v)}
                className={cn(
                  "rounded-md px-2 py-1 text-[11px] font-medium transition-all flex items-center gap-1",
                  viewport === v
                    ? "bg-atoms-accent/20 text-atoms-accent-hover shadow-sm"
                    : "text-zinc-500 hover:text-zinc-300"
                )}
              >
                <Icon className="h-3.5 w-3.5" />
                {VIEWPORT_CONFIG[v].label}
              </button>
            );
          })}
        </div>
        <div className="flex items-center gap-1">
          {consoleErrors.length > 0 && (
            <button
              onClick={() => setShowConsole(!showConsole)}
              className={cn(
                "rounded-lg p-1.5 transition-colors relative",
                showConsole
                  ? "bg-red-500/20 text-red-400"
                  : "text-red-400 hover:bg-red-500/10"
              )}
              title={`${consoleErrors.length} 个控制台错误`}
            >
              <AlertTriangle className="h-4 w-4" />
              <span className="absolute -top-1 -right-1 h-3.5 w-3.5 rounded-full bg-red-500 text-[9px] text-white flex items-center justify-center font-bold">
                {consoleErrors.length}
              </span>
            </button>
          )}
          <button
            onClick={() => setRightView("files")}
            className={cn(
              "rounded-lg p-1.5 transition-colors",
              rightView === "files"
                ? "bg-atoms-accent/20 text-atoms-accent-hover"
                : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
            )}
            title="项目文件"
          >
            <FolderTree className="h-4 w-4" />
          </button>
          <button
            onClick={() => setRightView("preview")}
            className={cn(
              "rounded-lg p-1.5 transition-colors",
              rightView === "preview"
                ? "bg-atoms-accent/20 text-atoms-accent-hover"
                : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
            )}
            title="预览"
          >
            <Eye className="h-4 w-4" />
          </button>
          <div className="h-4 w-px bg-atoms-border mx-0.5" />
          <button
            onClick={handleRefresh}
            className="rounded-lg p-1.5 text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors"
            title="刷新预览"
          >
            <RotateCw className="h-4 w-4" />
          </button>
          <button
            onClick={handleOpenNew}
            className="rounded-lg p-1.5 text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors"
            title="在新标签页中打开"
          >
            <ExternalLink className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 min-h-0 flex">
        {rightView === "files" && files.length > 0 && (
          <div className="w-52 flex-shrink-0 border-r border-atoms-border bg-atoms-card overflow-y-auto">
            <div className="px-3 py-2 text-[10px] font-semibold text-zinc-500 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="h-3 w-3" />
              项目文件
            </div>
            {files.map((file) => (
              <button
                key={file.name}
                onClick={() => setSelectedFile(file.name)}
                className={cn(
                  "w-full flex items-center gap-2 px-3 py-1.5 text-xs transition-colors text-left",
                  selectedFile === file.name
                    ? "bg-atoms-accent/10 text-atoms-accent-hover"
                    : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                )}
              >
                <Code2 className="h-3.5 w-3.5 flex-shrink-0 text-zinc-600" />
                <span className="truncate">{file.name}</span>
              </button>
            ))}
          </div>
        )}

        <div className="flex-1 min-w-0 flex flex-col">
          <div className="flex-1 min-h-0">
            {rightView === "preview" ? (
              <div className="h-full bg-zinc-900/50 p-4 overflow-auto flex justify-center items-start">
                {!previewHtml ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="w-full h-full flex flex-col items-center justify-center gap-3"
                  >
                    <div className="relative mb-2">
                      <div className="w-20 h-20 rounded-2xl bg-atoms-card border border-atoms-border flex items-center justify-center">
                        <Code2 className="h-8 w-8 text-zinc-700" />
                      </div>
                      <div className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full bg-atoms-accent/20 border border-atoms-accent/30 flex items-center justify-center">
                        <Eye className="h-3 w-3 text-atoms-accent-hover" />
                      </div>
                    </div>
                    <p className="text-sm text-zinc-500 font-medium">等待代码生成</p>
                    <p className="text-xs text-zinc-600 max-w-[200px] text-center leading-relaxed">
                      在左侧描述你想构建的产品，代码生成后将在此处预览
                    </p>
                  </motion.div>
                ) : (
                  <div
                    className="h-full bg-white rounded-lg overflow-hidden shadow-2xl shadow-black/30 transition-all duration-300 ring-1 ring-white/5"
                    style={{ width: VIEWPORT_CONFIG[viewport].width }}
                  >
                    <iframe
                      ref={iframeRef}
                      key={refreshKey}
                      srcDoc={iframeSrcDoc}
                      className="h-full w-full border-0"
                      sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals"
                      title="Preview"
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="h-full bg-zinc-950 overflow-auto">
                {!currentFile ? (
                  <div className="flex items-center justify-center h-full text-sm text-zinc-600">
                    请选择文件查看
                  </div>
                ) : (
                  <div className="relative">
                    <div className="sticky top-0 z-10 flex items-center gap-2 border-b border-atoms-border bg-zinc-900/80 backdrop-blur px-4 py-1.5">
                      <Code2 className="h-3.5 w-3.5 text-zinc-500" />
                      <span className="text-xs font-medium text-zinc-300">{currentFile.name}</span>
                      <span className="text-[10px] text-zinc-600 ml-auto">{currentFile.content.split("\n").length} 行</span>
                    </div>
                    <pre className="p-4 text-[13px] leading-relaxed font-mono text-zinc-300 overflow-x-auto">
                      <code>{currentFile.content}</code>
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>

          {showConsole && consoleErrors.length > 0 && (
            <div className="border-t border-red-500/30 bg-zinc-950 max-h-40 overflow-y-auto">
              <div className="flex items-center justify-between px-3 py-1.5 bg-red-500/10 border-b border-red-500/20">
                <span className="text-xs font-medium text-red-400">
                  控制台错误 ({consoleErrors.length})
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => clearConsoleErrors()}
                    className="text-xs text-zinc-500 hover:text-zinc-300 px-1"
                  >
                    清除
                  </button>
                  <button
                    onClick={() => setShowConsole(false)}
                    className="text-zinc-500 hover:text-zinc-300"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
              {consoleErrors.map((err, i) => (
                <div key={i} className="px-3 py-1.5 text-xs border-b border-atoms-border/50">
                  <span className="text-red-400">{err.message}</span>
                  {err.line ? (
                    <span className="text-zinc-600 ml-2">行 {err.line}</span>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
