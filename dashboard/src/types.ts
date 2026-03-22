export type ProjectStatus =
  | "generating"
  | "generated"
  | "generated_with_warnings"
  | "rendered"
  | "failed";

export type VerificationStatus = "passed" | "passed_with_warnings" | "failed";

export interface AgentLogEntry {
  agent: string;
  status: string;
  message: string;
  timestamp: string;
}

export interface VerificationIssue {
  check: string;
  message: string;
  route_to?: string | null;
}

export interface VerificationResult {
  status: VerificationStatus;
  errors: VerificationIssue[];
  warnings: VerificationIssue[];
}

export interface PipelineSummary {
  scene_count: number;
  duration: number;
  theme_name: string;
  render_status: string;
  llm_configured: boolean;
}

export interface ProjectSummary {
  project_id: string;
  title: string;
  status: ProjectStatus | string;
  verification_status?: VerificationStatus | null;
  theme_name: string;
  duration: number;
  scene_count: number;
  render_requested: boolean;
  render_path?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectIR {
  version: string;
  meta: {
    id: string;
    title: string;
    description: string;
    duration: number;
    fps: number;
    width: number;
    height: number;
    aspect_ratio: string;
    created_at: string;
    status: string;
  };
  timeline: {
    scenes: Array<{
      id: string;
      role: string;
      title?: string | null;
      start_time: number;
      duration: number;
      background: {
        type: string;
        colors: string[];
      };
      elements: Array<{
        id: string;
        type: string;
        layer: number;
        props: Record<string, unknown>;
      }>;
    }>;
  };
}

export interface ProjectDetail extends ProjectSummary {
  brief: string;
  aspect_ratio: string;
  platform: string;
  ir_path?: string | null;
  ir?: ProjectIR | null;
  summary?: PipelineSummary | null;
  verification?: VerificationResult | null;
  logs: AgentLogEntry[];
}

export interface GenerateVideoRequest {
  brief: string;
  title?: string;
  theme_name: string;
  aspect_ratio: "16:9" | "9:16" | "1:1";
  duration: number;
  scene_count: number;
  platform: string;
  render_video: boolean;
}

export interface GenerateVideoResponse {
  project_id: string;
  ir_path: string;
  render_path?: string | null;
}

export interface ProjectLaunchResponse {
  project_id: string;
  status: "generating";
  detail_path: string;
  websocket_path: string;
}

export interface ProjectProgressEvent {
  event:
    | "project_created"
    | "stage_started"
    | "stage_completed"
    | "project_completed"
    | "project_failed";
  project_id: string;
  stage: string;
  status: string;
  message: string;
  progress: number;
  timestamp: string;
  render_path?: string | null;
  verification_status?: string | null;
}
