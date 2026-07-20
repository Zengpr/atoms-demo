import type { User, Project, Message, CreateProjectData, ChatMode } from "./types";

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "").replace(/[\uFEFF\u200B]/g, "").trim();
const SSE_BASE = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/[\uFEFF\u200B]/g, "").trim();

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("atoms_token");
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const body = await res.text();
    let message = res.statusText;
    try {
      const parsed = JSON.parse(body);
      message = parsed.detail || parsed.message || parsed.error || res.statusText;
    } catch {
      if (body) {
        message = body.length > 200 ? body.substring(0, 200) + "..." : body;
      }
    }
    if (res.status === 401) {
      localStorage.removeItem("atoms_token");
      message = "Invalid token";
    }
    if (res.status === 500) {
      message = "Server error. Please try again later.";
    }
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const authApi = {
  register(
    email: string,
    username: string,
    password: string
  ): Promise<{ accessToken: string; user: User }> {
    return apiFetch("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, username, password }),
    });
  },

  login(
    email: string,
    password: string
  ): Promise<{ accessToken: string; user: User }> {
    return apiFetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  getMe(): Promise<User> {
    return apiFetch("/api/auth/me");
  },
};

export const projectApi = {
  list(): Promise<Project[]> {
    return apiFetch("/api/projects");
  },

  create(data: CreateProjectData): Promise<Project> {
    return apiFetch("/api/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  get(id: string): Promise<Project> {
    return apiFetch(`/api/projects/${id}`);
  },

  update(
    id: string,
    data: Partial<CreateProjectData & { status: string }>
  ): Promise<Project> {
    return apiFetch(`/api/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  delete(id: string): Promise<void> {
    return apiFetch(`/api/projects/${id}`, { method: "DELETE" });
  },

  getVersions(id: string): Promise<import("./types").CodeVersion[]> {
    return apiFetch(`/api/projects/${id}/versions`);
  },

  getLatestCode(id: string): Promise<{ code: string | null }> {
    return apiFetch(`/api/projects/${id}/latest-code`);
  },
};

export interface SSEMessage {
  event: string;
  data: Record<string, unknown>;
}

export async function* streamChat(
  projectId: string,
  content: string,
  mode: ChatMode
): AsyncGenerator<SSEMessage> {
  const token = getToken();
  const res = await fetch(`${SSE_BASE}/api/chat/${projectId}/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ content, mode }),
  });

  if (!res.ok) {
    throw new ApiError(res.status, await res.text());
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    let currentEvent = "";
    let currentData = "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        currentData = line.slice(6);
      } else if (line === "" && currentEvent && currentData) {
        try {
          yield {
            event: currentEvent,
            data: JSON.parse(currentData),
          };
        } catch {
          // skip malformed
        }
        currentEvent = "";
        currentData = "";
      }
    }
  }
}

export const chatApi = {
  getHistory(projectId: string): Promise<Message[]> {
    return apiFetch(`/api/chat/${projectId}/history`);
  },
};

export const previewApi = {
  getPreviewUrl(projectId: string): string {
    return `${SSE_BASE}/api/preview/${projectId}/html`;
  },
};

export { ApiError };
