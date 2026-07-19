"use client";

import { useState } from "react";
import { Monitor, Tablet, Smartphone, RotateCw, ExternalLink, Rocket } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePreviewStore } from "@/lib/store";
import { Skeleton } from "@/components/ui/Skeleton";

type Viewport = "desktop" | "tablet" | "mobile";

const VIEWPORT_WIDTHS: Record<Viewport, string> = {
  desktop: "100%",
  tablet: "768px",
  mobile: "375px",
};

interface PreviewPanelProps {
  projectId: string;
  onDeploy?: () => void;
  deploying?: boolean;
  deployMsg?: string;
}

export function PreviewPanel({ projectId, onDeploy, deploying, deployMsg }: PreviewPanelProps) {
  const { previewHtml } = usePreviewStore();
  const [viewport, setViewport] = useState<Viewport>("desktop");
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => setRefreshKey((k) => k + 1);
  const handleOpenNew = () => {
    const win = window.open("", "_blank");
    if (win && previewHtml) {
      win.document.write(previewHtml);
      win.document.close();
    }
  };

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
                className="rounded-lg p-1.5 text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors disabled:opacity-50"
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

      <div className="flex-1 bg-zinc-900 p-4 overflow-auto flex justify-center">
        {!previewHtml ? (
          <div className="w-full h-full flex flex-col items-center justify-center gap-4">
            <Skeleton className="w-3/4 h-8" />
            <Skeleton className="w-1/2 h-6" />
            <Skeleton className="w-2/3 h-32" />
            <Skeleton className="w-1/3 h-6" />
            <Skeleton className="w-1/2 h-20" />
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
              key={refreshKey}
              srcDoc={previewHtml}
              className="h-full w-full border-0"
              sandbox="allow-scripts allow-same-origin"
              title="Preview"
            />
          </div>
        )}
      </div>
    </div>
  );
}
