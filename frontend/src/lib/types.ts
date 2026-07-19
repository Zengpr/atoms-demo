export type ChatMode = "engineer" | "team" | "race" | "research";

export interface User {
  id: string;
  email: string;
  username: string;
  avatarUrl: string | null;
  credits: number;
  createdAt: string;
}

export interface Project {
  id: string;
  userId: string;
  name: string;
  description: string | null;
  mode: ChatMode;
  status: "draft" | "building" | "completed";
  thumbnail: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface Message {
  id: string;
  conversationId: string;
  role: "user" | "assistant" | "agent";
  agentName?: string;
  content: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
}

export interface CodeVersion {
  id: string;
  projectId: string;
  version: number;
  codeHtml: string;
  codeCss: string;
  codeJs: string;
  codeFull: string;
  createdAt: string;
}

export interface AgentInfo {
  name: string;
  role: string;
  description: string;
  avatarEmoji: string;
}

export interface SSEEvent {
  type: "agent_thinking" | "agent_action" | "code_generated" | "message_complete";
  data: Record<string, unknown>;
}

export interface CreateProjectData {
  name: string;
  description: string;
  mode: ChatMode;
  template?: string;
}
