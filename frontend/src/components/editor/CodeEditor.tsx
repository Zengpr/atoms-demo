"use client";


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

  return (
    <div className="h-full w-full">
      <Editor
        height="100%"
        language={language}
        value={previewHtml || "<!-- Waiting for generated code... -->"}
        onChange={(value) => { if (value) setPreviewHtml(value); }}
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
