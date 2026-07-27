"use client";

import { useState, useMemo } from "react";
import { ChevronRight, ChevronDown, FileCode2, FileText, Folder, FolderOpen, Copy, Check } from "lucide-react";
import { usePreviewStore } from "@/lib/store";

interface FileEntry {
  name: string;
  type: "file";
  lang: string;
  content: string;
  size: number;
}

interface FolderEntry {
  name: string;
  type: "folder";
  children: TreeNode[];
  open?: boolean;
}

type TreeNode = FileEntry | FolderEntry;

function parseHtmlToTree(html: string): TreeNode[] {
  if (!html) return [];
  const nodes: TreeNode[] = [];

  let cssContent = "";
  const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  let match;
  while ((match = styleRegex.exec(html)) !== null) {
    cssContent += match[1].trim() + "\n";
  }

  let jsContent = "";
  const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
  while ((match = scriptRegex.exec(html)) !== null) {
    jsContent += match[1].trim() + "\n";
  }

  let bodyContent = "";
  const bodyRegex = /<body[^>]*>([\s\S]*?)<\/body>/i;
  const bodyMatch = bodyRegex.exec(html);
  if (bodyMatch) {
    bodyContent = bodyMatch[1].replace(/<script[\s\S]*?<\/script>/gi, "").replace(/<style[\s\S]*?<\/style>/gi, "").trim();
  }

  const srcFiles: FileEntry[] = [];

  if (cssContent.trim()) {
    srcFiles.push({ name: "style.css", type: "file", lang: "css", content: cssContent.trim(), size: cssContent.trim().length });
  }
  if (bodyContent.trim()) {
    srcFiles.push({ name: "index.html", type: "file", lang: "html", content: bodyContent.trim(), size: bodyContent.trim().length });
  }
  if (jsContent.trim()) {
    srcFiles.push({ name: "app.js", type: "file", lang: "javascript", content: jsContent.trim(), size: jsContent.trim().length });
  }

  if (srcFiles.length > 0) {
    nodes.push({ name: "src", type: "folder", children: srcFiles, open: true });
  }

  nodes.push({ name: "index.html", type: "file", lang: "html", content: html, size: html.length });

  return nodes;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  return `${(bytes / 1024).toFixed(1)}KB`;
}

function TreeNodeView({ node, depth, onSelect, selectedLang, selectedContent }: {
  node: TreeNode;
  depth: number;
  onSelect: (content: string, lang: string) => void;
  selectedLang: string;
  selectedContent: string;
}) {
  const [open, setOpen] = useState(node.type === "folder" ? (node.open ?? false) : false);
  const isSelected = node.type === "file" && node.content === selectedContent;

  if (node.type === "folder") {
    return (
      <div>
        <button
          onClick={() => setOpen(!open)}
          className="w-full flex items-center gap-1.5 px-2 py-1 text-xs text-zinc-300 hover:bg-white/5 rounded transition-colors"
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
        >
          {open ? <ChevronDown className="h-3 w-3 text-zinc-500" /> : <ChevronRight className="h-3 w-3 text-zinc-500" />}
          {open ? <FolderOpen className="h-3.5 w-3.5 text-amber-400" /> : <Folder className="h-3.5 w-3.5 text-amber-400" />}
          <span>{node.name}</span>
        </button>
        {open && node.children.map((child, i) => (
          <TreeNodeView
            key={`${child.name}-${i}`}
            node={child}
            depth={depth + 1}
            onSelect={onSelect}
            selectedLang={selectedLang}
            selectedContent={selectedContent}
          />
        ))}
      </div>
    );
  }

  const icon = node.lang === "css" ? "🎨" : node.lang === "javascript" ? "⚡" : "📄";

  return (
    <button
      onClick={() => onSelect(node.content, node.lang)}
      className={`w-full flex items-center gap-1.5 px-2 py-1 text-xs rounded transition-colors ${
        isSelected ? "bg-atoms-accent/20 text-atoms-accent-hover" : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
      }`}
      style={{ paddingLeft: `${depth * 12 + 8}px` }}
    >
      <span className="flex-shrink-0 text-[10px]">{icon}</span>
      <span className="truncate flex-1 text-left">{node.name}</span>
      <span className="text-[10px] text-zinc-600 flex-shrink-0">{formatSize(node.size)}</span>
    </button>
  );
}

export function FileTree({ onFileSelect }: { onFileSelect?: (content: string, lang: string) => void }) {
  const { previewHtml } = usePreviewStore();
  const [selectedContent, setSelectedContent] = useState("");
  const [selectedLang, setSelectedLang] = useState("");
  const [copied, setCopied] = useState(false);

  const tree = useMemo(() => parseHtmlToTree(previewHtml), [previewHtml]);

  const handleSelect = (content: string, lang: string) => {
    setSelectedContent(content);
    setSelectedLang(lang);
    onFileSelect?.(content, lang);
  };

  const handleCopy = async () => {
    if (!selectedContent) return;
    await navigator.clipboard.writeText(selectedContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!previewHtml) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-4">
        <div className="text-2xl mb-2">📁</div>
        <p className="text-xs text-zinc-500">File tree will appear after code generation</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 border-b border-atoms-border flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-400">Files</span>
        {selectedContent && (
          <button onClick={handleCopy} className="text-zinc-500 hover:text-zinc-200 transition-colors">
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          </button>
        )}
      </div>
      <div className="flex-1 overflow-y-auto py-1 scrollbar-thin">
        {tree.map((node, i) => (
          <TreeNodeView
            key={`${node.name}-${i}`}
            node={node}
            depth={0}
            onSelect={handleSelect}
            selectedLang={selectedLang}
            selectedContent={selectedContent}
          />
        ))}
      </div>
      {selectedContent && (
        <div className="border-t border-atoms-border max-h-[40%] overflow-auto">
          <pre className="p-2 text-[11px] text-zinc-400 font-mono whitespace-pre-wrap break-all leading-relaxed">
            {selectedContent.slice(0, 5000)}{selectedContent.length > 5000 ? "\n..." : ""}
          </pre>
        </div>
      )}
    </div>
  );
}
