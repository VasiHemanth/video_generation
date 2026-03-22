import type {
  GenerateVideoRequest,
  GenerateVideoResponse,
  ProjectDetail,
  ProjectLaunchResponse,
  ProjectProgressEvent,
  ProjectSummary,
} from "./types";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

export const apiBaseUrl = stripTrailingSlash(
  import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL,
);

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as {detail?: string};
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      // Keep the original HTTP status text when the error body is not JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export async function listThemes(): Promise<string[]> {
  const payload = await fetchJson<{themes: string[]}>("/api/themes");
  return payload.themes;
}

export async function listProjects(): Promise<ProjectSummary[]> {
  return fetchJson<ProjectSummary[]>("/api/projects");
}

export async function getProject(projectId: string): Promise<ProjectDetail> {
  return fetchJson<ProjectDetail>(`/api/projects/${projectId}`);
}

export async function generateVideo(
  payload: GenerateVideoRequest,
): Promise<GenerateVideoResponse> {
  return fetchJson<GenerateVideoResponse>("/api/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function launchProject(
  payload: GenerateVideoRequest,
): Promise<ProjectLaunchResponse> {
  return fetchJson<ProjectLaunchResponse>("/api/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function projectWebSocketUrl(projectId: string): string {
  const url = new URL(`/ws/projects/${projectId}`, apiBaseUrl);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
}

export function mediaUrl(
  kind: "renders" | "ir",
  sourcePath?: string | null,
): string | null {
  if (!sourcePath) {
    return null;
  }

  const filename = sourcePath.split(/[/\\]/).pop();
  if (!filename) {
    return null;
  }
  return `${apiBaseUrl}/media/${kind}/${encodeURIComponent(filename)}`;
}

export function parseProgressEvent(value: string): ProjectProgressEvent {
  return JSON.parse(value) as ProjectProgressEvent;
}
