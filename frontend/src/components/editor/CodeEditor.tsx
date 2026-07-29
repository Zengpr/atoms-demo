"use client";

import { useCallback, useRef } from "react";
import Editor from "@monaco-editor/react";
import { usePreviewStore } from "@/lib/store";

interface CodeEditorProps {
  language?: string;
  readOnly?: boolean;
}

export function CodeEditor({
  language = "html",
  readOnly = false,
}: CodeEditorProps) {
  const { previewHtml, setPreviewHtml } = usePreviewStore();
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleChange = useCallback((value: string | undefined) => {
    if (!value) return;
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      setPreviewHtml(value);
    }, 800);
  }, [setPreviewHtml]);

  return (
    <div className="h-full w-full">
      <Editor
        height="100%"
        language={language}
        value={previewHtml || "<!-- 等待生成代码... -->"}
        onChange={handleChange}
        theme="vs-dark"
        options={{
          readOnly,
          minimap: { enabled: false },
          lineNumbers: "on",
          fontSize: 13,
          fontFamily: "var(--font-geist-mono), Consolas, monospace",
          scrollBeyondLastLine: false,
          wordWrap: "on",
          automaticLayout: true,
          padding: { top: 12 },
          renderLineHighlight: "gutter",
          smoothScrolling: true,
          contextmenu: true,
        }}
      />
    </div>
  );
}
