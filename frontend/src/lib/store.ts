import { create } from "zustand";
import type { User, Project, Message, CreateProjectData, ChatMode } from "./types";
import { authApi, projectApi, chatApi } from "./api";

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    username: string,
    password: string
  ) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: async (email, password) => {
    const res = await authApi.login(email, password);
    localStorage.setItem("atoms_token", res.accessToken);
    set({ user: res.user, token: res.accessToken, isAuthenticated: true });
  },

  register: async (email, username, password) => {
    const res = await authApi.register(email, username, password);
    localStorage.setItem("atoms_token", res.accessToken);
    set({ user: res.user, token: res.accessToken, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem("atoms_token");
    set({ user: null, token: null, isAuthenticated: false });
  },

  loadUser: async () => {
    const token = localStorage.getItem("atoms_token");
    if (!token || token === "null" || token === "undefined") {
      localStorage.removeItem("atoms_token");
      set({ user: null, token: null, isAuthenticated: false });
      return;
    }
    try {
      const user = await authApi.getMe();
      set({ user, token, isAuthenticated: true });
    } catch {
      localStorage.removeItem("atoms_token");
      set({ user: null, token: null, isAuthenticated: false });
    }
  },
}));

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  loadProjects: () => Promise<void>;
  createProject: (data: CreateProjectData) => Promise<Project>;
  selectProject: (project: Project | null) => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  currentProject: null,

  loadProjects: async () => {
    const projects = await projectApi.list();
    set({ projects });
  },

  createProject: async (data) => {
    const project = await projectApi.create(data);
    set((s) => ({ projects: [project, ...s.projects] }));
    return project;
  },

  selectProject: (project) => {
    set({ currentProject: project });
  },
}));

interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  currentMode: ChatMode;
  addMessage: (message: Message) => void;
  updateLastAgentMessage: (msgId: string, chunk: string) => void;
  setStreaming: (streaming: boolean) => void;
  setMode: (mode: ChatMode) => void;
  clearMessages: () => void;
  loadHistory: (projectId: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  currentMode: "engineer",

  addMessage: (message) =>
    set((s) => ({ messages: [...s.messages, message] })),

  updateLastAgentMessage: (msgId, chunk) =>
    set((s) => ({
      messages: s.messages.map((m) => {
        if (m.id !== msgId) return m;
        const prev = (m.metadata?.streamText as string) ?? "";
        return {
          ...m,
          metadata: { ...m.metadata, streamText: prev + chunk },
        };
      }),
    })),

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  setMode: (mode) => set({ currentMode: mode }),

  clearMessages: () => set({ messages: [] }),

  loadHistory: async (projectId) => {
    const messages = await chatApi.getHistory(projectId);
    set({ messages });
  },
}));

interface ConsoleError {
  message: string;
  line?: number;
  source?: string;
}

interface PreviewState {
  previewHtml: string;
  previewUrl: string;
  consoleErrors: ConsoleError[];
  setPreviewHtml: (html: string) => void;
  setPreviewUrl: (url: string) => void;
  addConsoleError: (err: ConsoleError) => void;
  clearConsoleErrors: () => void;
}

export const usePreviewStore = create<PreviewState>((set) => ({
  previewHtml: "",
  previewUrl: "",
  consoleErrors: [],

  setPreviewHtml: (html) => set({ previewHtml: html, consoleErrors: [] }),
  setPreviewUrl: (url) => set({ previewUrl: url }),
  addConsoleError: (err) =>
    set((s) => ({ consoleErrors: [...s.consoleErrors.slice(-19), err] })),
  clearConsoleErrors: () => set({ consoleErrors: [] }),
}));
