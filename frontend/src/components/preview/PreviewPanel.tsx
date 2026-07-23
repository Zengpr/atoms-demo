"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import { Monitor, Tablet, Smartphone, RotateCw, ExternalLink, Rocket, FolderTree, Eye, AlertTriangle, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePreviewStore } from "@/lib/store";
import { Skeleton } from "@/components/ui/Skeleton";

type Viewport = "desktop" | "tablet" | "mobile";
type RightView = "preview" | "files";

const VIEWPORT_WIDTHS: Record<Viewport, string> = {
  desktop: "100%",
  tablet: "768px",
  mobile: "375px",
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
  projectId: string;
  onDeploy?: () => void;
  deploying?: boolean;
  deployMsg?: string;
}

export function PreviewPanel({ projectId, onDeploy, deploying, deployMsg }: PreviewPanelProps) {
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
  }, []);

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
  }, [previewHtml, refreshKey]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-atoms-border bg-atoms-card px-3 py-2">
        <div className="flex items-center gap-1">
          {([["desktop", Monitor], ["tablet", Tablet], ["mobile", Smartphone]] as const).map(
            ([v, Icon]) => (
              <button
                key={v}
                onClick={() => setViewport(v)}
                className={cn(
                  "rounded-lg p-1.5 transition-colors",
                  viewport === v
                    ? "bg-atoms-accent/20 text-atoms-accent-hover"
                    : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
                )}
              >
                <Icon className="h-4 w-4" />
              </button>
            )
          )}
        </div>
        <div className="flex items-center gap-1">
          {consoleErrors.length > 0 && (
            <button
              onClick={() => setShowConsole(!showConsole)}
              className={cn(
                "rounded-lg p-1.5 transition-colors",
                showConsole
                  ? "bg-red-500/20 text-red-400"
                  : "text-red-400 hover:bg-red-500/10"
              )}
              title={`${consoleErrors.length} console errors`}
            >
              <AlertTriangle className="h-4 w-4" />
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
            title="Files"
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
            title="Preview"
          >
            <Eye className="h-4 w-4" />
          </button>
          <button
            onClick={handleRefresh}
            className="rounded-lg p-1.5 text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors"
          >
            <RotateCw className="h-4 w-4" />
          </button>
          <button
            onClick={handleOpenNew}
            className="rounded-lg p-1.5 text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors"
          >
            <ExternalLink className="h-4 w-4" />
          </button>
          {onDeploy && (
            <>
              <button
                onClick={onDeploy}
                disabled={deploying}
                className="rounded-lg p-1.5 text-zinc-500 hover:text-zinc-300 hover:bg-white/5 disabled:opacity-50"
                title="Deploy"
              >
                <Rocket className="h-4 w-4" />
              </button>
              {deployMsg && (
                <span className="text-xs text-atoms-accent">{deployMsg}</span>
              )}
            </>
          )}
        </div>
      </div>

      <div className="flex-1 min-h-0 flex">
        {rightView === "files" && files.length > 0 && (
          <div className="w-48 flex-shrink-0 border-r border-atoms-border bg-atoms-card overflow-y-auto">
            <div className="px-3 py-2 text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">
              Project Files
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
                <span className="flex-shrink-0 text-[10px]">{file.icon}</span>
                <span className="truncate">{file.name}</span>
              </button>
            ))}
          </div>
        )}

        <div className="flex-1 min-w-0 flex flex-col">
          <div className="flex-1 min-h-0">
            {rightView === "preview" ? (
              <div className="h-full bg-zinc-900 p-4 overflow-auto flex justify-center">
                {!previewHtml ? (
                  <div className="w-full h-full flex flex-col items-center justify-center gap-4">
                    <Skeleton className="w-3/4 h-8" />
                    <Skeleton className="w-1/2 h-6" />
                    <Skeleton className="w-2/3 h-32" />
                    <p className="text-sm text-zinc-600 mt-2">
                      Preview will appear here when code is generated
                    </p>
                  </div>
                ) : (
                  <div
                    className="h-full bg-white rounded-lg overflow-hidden shadow-2xl transition-all duration-300"
                    style={{ width: VIEWPORT_WIDTHS[viewport] }}
                  >
                    <iframe
                      ref={iframeRef}
                      key={refreshKey}
                      srcDoc={iframeSrcDoc}
                      className="h-full w-full border-0"
                      sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals allow-popups-without-user-activation"
                      title="Preview"
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="h-full bg-zinc-950 overflow-auto">
                {!currentFile ? (
                  <div className="flex items-center justify-center h-full text-sm text-zinc-600">
                    No file selected
                  </div>
                ) : (
                  <div className="relative">
                    <div className="sticky top-0 z-10 flex items-center gap-2 border-b border-atoms-border bg-zinc-900/80 backdrop-blur px-4 py-1.5">
                      <span className="text-xs font-medium text-zinc-300">{currentFile.name}</span>
                      <span className="text-[10px] text-zinc-600 ml-auto">{currentFile.content.split("\n").length} lines</span>
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
                  Console Errors ({consoleErrors.length})
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setConsoleErrors([])}
                    className="text-xs text-zinc-500 hover:text-zinc-300 px-1"
                  >
                    Clear
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
                    <span className="text-zinc-600 ml-2">line {err.line}</span>
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
