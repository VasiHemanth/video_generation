import {
  type ChangeEvent,
  type FormEvent,
  startTransition,
  useDeferredValue,
  useEffect,
  useEffectEvent,
  useState,
} from "react";

import {
  apiBaseUrl,
  getProject,
  launchProject,
  listProjects,
  listThemes,
  mediaUrl,
  parseProgressEvent,
  projectWebSocketUrl,
} from "./api";
import type {
  GenerateVideoRequest,
  ProjectDetail,
  ProjectProgressEvent,
  ProjectSummary,
} from "./types";

type ActiveTab = "overview" | "logs" | "ir";
type SocketState = "idle" | "connecting" | "live" | "closed" | "error";

interface StageDefinition {
  id: string;
  label: string;
  summary: string;
}

interface StageCard extends StageDefinition {
  status: string;
  message: string;
  timestamp: string | null;
  progress: number;
}

const PIPELINE_STAGES: StageDefinition[] = [
  {id: "manager", label: "Manager", summary: "Brief parsing and project constraints"},
  {id: "scriptwriter", label: "Script", summary: "Narrative beats and storyboard scenes"},
  {id: "designer", label: "Design", summary: "Theme loading and layout planning"},
  {id: "motion", label: "Motion", summary: "Transitions, timings, and emphasis"},
  {id: "audio", label: "Audio", summary: "Phase 1 silent audio stub"},
  {id: "renderer", label: "Renderer", summary: "IR assembly and MP4 generation"},
  {id: "verifier", label: "Verifier", summary: "Artifact validation and output checks"},
];

const defaultForm: GenerateVideoRequest = {
  brief: "",
  title: "",
  theme_name: "default",
  aspect_ratio: "16:9",
  duration: 35,
  scene_count: 5,
  platform: "youtube",
  render_video: true,
};

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
}

function formatAgentName(value: string): string {
  return value.replace(/[_-]/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function statusTone(status?: string | null): string {
  switch (status) {
    case "rendered":
    case "passed":
    case "completed":
    case "success":
      return "mint";
    case "generated_with_warnings":
    case "passed_with_warnings":
    case "warning":
      return "amber";
    case "failed":
    case "error":
      return "rose";
    case "generating":
    case "running":
      return "cool";
    default:
      return "slate";
  }
}

function socketLabel(state: SocketState): string {
  switch (state) {
    case "connecting":
      return "connecting";
    case "live":
      return "live";
    case "closed":
      return "settled";
    case "error":
      return "socket error";
    default:
      return "idle";
  }
}

function mergeProgressEvent(
  current: ProjectProgressEvent[],
  next: ProjectProgressEvent,
): ProjectProgressEvent[] {
  const key = `${next.event}:${next.stage}:${next.timestamp}:${next.message}`;
  if (
    current.some(
      (event) =>
        `${event.event}:${event.stage}:${event.timestamp}:${event.message}` === key,
    )
  ) {
    return current;
  }
  return [...current, next].slice(-96);
}

function latestProgressEvent(events: ProjectProgressEvent[]): ProjectProgressEvent | null {
  if (events.length === 0) {
    return null;
  }
  return events[events.length - 1];
}

function buildStageCards(
  project: ProjectDetail | null,
  events: ProjectProgressEvent[],
): StageCard[] {
  const cards = PIPELINE_STAGES.map<StageCard>((stage) => ({
    ...stage,
    status: "pending",
    message: "Waiting for upstream stages.",
    timestamp: null,
    progress: 0,
  }));
  const cardById = new Map(cards.map((card) => [card.id, card]));

  for (const log of project?.logs ?? []) {
    const card = cardById.get(log.agent);
    if (!card) {
      continue;
    }
    card.status = log.status;
    card.message = log.message;
    card.timestamp = log.timestamp;
    card.progress = 1;
  }

  for (const event of events) {
    if (event.stage === "pipeline") {
      continue;
    }
    const card = cardById.get(event.stage);
    if (!card) {
      continue;
    }
    card.status = event.status;
    card.message = event.message;
    card.timestamp = event.timestamp;
    card.progress = event.event === "stage_started" ? Math.max(card.progress, 0.18) : event.progress;
  }

  if (project?.verification) {
    const verifier = cardById.get("verifier");
    if (verifier) {
      verifier.status = project.verification.status;
      verifier.progress = 1;
    }
  }

  return cards;
}

function pipelineProgressPercent(
  project: ProjectDetail | null,
  events: ProjectProgressEvent[],
  stageCards: StageCard[],
): number {
  const latest = latestProgressEvent(events);
  if (latest) {
    return Math.round(latest.progress * 100);
  }

  if (project?.status === "generating") {
    return 5;
  }

  const completedStages = stageCards.filter((stage) =>
    ["completed", "passed", "passed_with_warnings"].includes(stage.status),
  ).length;
  return Math.round((completedStages / PIPELINE_STAGES.length) * 100);
}

function App() {
  const [themes, setThemes] = useState<string[]>(["default"]);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<ProjectDetail | null>(null);
  const [progressEvents, setProgressEvents] = useState<ProjectProgressEvent[]>([]);
  const [socketState, setSocketState] = useState<SocketState>("idle");
  const [form, setForm] = useState<GenerateVideoRequest>(defaultForm);
  const [activeTab, setActiveTab] = useState<ActiveTab>("overview");
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [appError, setAppError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>("Ready");

  const deferredIrJson = useDeferredValue(
    selectedProject?.ir ? JSON.stringify(selectedProject.ir, null, 2) : "",
  );

  const refreshProjects = useEffectEvent(async () => {
    try {
      const items = await listProjects();
      setProjects(items);
      setAppError(null);

      if (items.length === 0) {
        setSelectedProjectId(null);
        return;
      }

      const hasCurrentSelection = items.some(
        (project) => project.project_id === selectedProjectId,
      );
      if (!selectedProjectId || !hasCurrentSelection) {
        startTransition(() => {
          setSelectedProjectId(items[0].project_id);
        });
      }
    } catch (error) {
      setAppError(error instanceof Error ? error.message : "Failed to load projects.");
    } finally {
      setLoadingProjects(false);
    }
  });

  const refreshThemes = useEffectEvent(async () => {
    try {
      const items = await listThemes();
      setThemes(items);
      setForm((current) => ({
        ...current,
        theme_name: items.includes(current.theme_name) ? current.theme_name : items[0] ?? "default",
      }));
    } catch (error) {
      setAppError(error instanceof Error ? error.message : "Failed to load themes.");
    }
  });

  const loadProjectDetail = useEffectEvent(async (projectId: string) => {
    setLoadingDetail(true);
    try {
      const detail = await getProject(projectId);
      setSelectedProject(detail);
      setDetailError(null);
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : "Failed to load project detail.");
    } finally {
      setLoadingDetail(false);
    }
  });

  useEffect(() => {
    void Promise.all([refreshThemes(), refreshProjects()]);
  }, [refreshProjects, refreshThemes]);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      void refreshProjects();
    }, 6000);
    return () => window.clearInterval(intervalId);
  }, [refreshProjects]);

  useEffect(() => {
    if (!selectedProjectId) {
      setSelectedProject(null);
      setProgressEvents([]);
      setSocketState("idle");
      return;
    }

    void loadProjectDetail(selectedProjectId);
  }, [loadProjectDetail, selectedProjectId]);

  useEffect(() => {
    if (!selectedProjectId) {
      return;
    }

    const intervalId = window.setInterval(() => {
      void loadProjectDetail(selectedProjectId);
    }, 4000);
    return () => window.clearInterval(intervalId);
  }, [loadProjectDetail, selectedProjectId]);

  useEffect(() => {
    if (!selectedProjectId) {
      return;
    }

    setProgressEvents([]);
    setSocketState("connecting");
    const socket = new WebSocket(projectWebSocketUrl(selectedProjectId));

    socket.onopen = () => {
      setSocketState("live");
    };

    socket.onmessage = (message) => {
      const event = parseProgressEvent(message.data);
      setProgressEvents((current) => mergeProgressEvent(current, event));
      setStatusMessage(event.message);

      if (event.event === "project_completed" || event.event === "project_failed") {
        setSocketState("closed");
        void refreshProjects();
        void loadProjectDetail(selectedProjectId);
        socket.close();
      }
    };

    socket.onerror = () => {
      setSocketState("error");
    };

    socket.onclose = () => {
      setSocketState((current) => (current === "error" ? "error" : "closed"));
    };

    return () => {
      socket.close();
    };
  }, [loadProjectDetail, refreshProjects, selectedProjectId]);

  function updateField<Key extends keyof GenerateVideoRequest>(
    key: Key,
    value: GenerateVideoRequest[Key],
  ) {
    setForm((current) => ({
      ...current,
      [key]: value,
    }));
  }

  function handleTextInput<Key extends keyof GenerateVideoRequest>(
    key: Key,
    parser?: (value: string) => GenerateVideoRequest[Key],
  ) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const nextValue = parser
        ? parser(event.target.value)
        : (event.target.value as GenerateVideoRequest[Key]);
      updateField(key, nextValue);
    };
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setAppError(null);
    setStatusMessage("Creating project and opening live pipeline...");
    try {
      const response = await launchProject({
        ...form,
        title: form.title?.trim() || undefined,
      });
      setStatusMessage(`Live run started: ${response.project_id}`);
      setSelectedProject(null);
      setProgressEvents([]);
      setActiveTab("overview");
      await refreshProjects();
      startTransition(() => {
        setSelectedProjectId(response.project_id);
      });
      void loadProjectDetail(response.project_id);
    } catch (error) {
      setAppError(error instanceof Error ? error.message : "Generation failed.");
      setStatusMessage("Generation failed");
    } finally {
      setSubmitting(false);
    }
  }

  const selectedProjectVideoUrl = selectedProject?.render_path
    ? `${mediaUrl("renders", selectedProject.render_path)}?v=${encodeURIComponent(
        selectedProject.updated_at,
      )}`
    : null;

  const stageCards = buildStageCards(selectedProject, progressEvents);
  const progressPercent = pipelineProgressPercent(selectedProject, progressEvents, stageCards);
  const liveActivity = [...progressEvents].slice(-7).reverse();
  const currentProgressEvent = latestProgressEvent(progressEvents);

  return (
    <main className="app-shell">
      <section className="studio-panel">
        <div className="hero-card panel">
          <p className="eyebrow">Phase 1 Dashboard</p>
          <h1>Track each brief from input to persisted render.</h1>
          <p className="hero-copy">
            The dashboard now launches projects in the background and attaches a live WebSocket
            feed to the stage graph while the existing polling views keep project records and
            artifacts in sync.
          </p>
          <div className="hero-meta">
            <span className={`status-pill ${statusTone(currentProgressEvent?.status ?? null)}`}>
              {statusMessage}
            </span>
            <span className="api-badge">API {apiBaseUrl}</span>
          </div>
        </div>

        <form className="panel form-panel" onSubmit={handleSubmit}>
          <div className="section-heading">
            <div>
              <p className="eyebrow">New Project</p>
              <h2>Generate a run</h2>
            </div>
            <button className="primary-button" type="submit" disabled={submitting}>
              {submitting ? "Launching..." : "Launch Live Run"}
            </button>
          </div>

          <label className="field">
            <span>Title</span>
            <input
              value={form.title ?? ""}
              onChange={handleTextInput("title")}
              placeholder="Optional title override"
            />
          </label>

          <label className="field">
            <span>Brief</span>
            <textarea
              value={form.brief}
              onChange={handleTextInput("brief")}
              placeholder="Describe the video outcome, audience, and the points the pipeline should emphasize."
              rows={7}
              required
            />
          </label>

          <div className="field-grid">
            <label className="field">
              <span>Theme</span>
              <select value={form.theme_name} onChange={handleTextInput("theme_name")}>
                {themes.map((theme) => (
                  <option key={theme} value={theme}>
                    {theme}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Platform</span>
              <select value={form.platform} onChange={handleTextInput("platform")}>
                <option value="youtube">YouTube</option>
                <option value="linkedin">LinkedIn</option>
                <option value="instagram">Instagram</option>
                <option value="tiktok">TikTok</option>
              </select>
            </label>
          </div>

          <div className="field-grid compact">
            <label className="field">
              <span>Duration</span>
              <input
                type="number"
                min={30}
                max={40}
                value={form.duration}
                onChange={handleTextInput("duration", (value) => Number(value))}
              />
            </label>

            <label className="field">
              <span>Scenes</span>
              <select
                value={String(form.scene_count)}
                onChange={handleTextInput("scene_count", (value) => Number(value))}
              >
                {[3, 4, 5, 6, 7, 8].map((count) => (
                  <option key={count} value={count}>
                    {count}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <fieldset className="segmented-field">
            <legend>Aspect Ratio</legend>
            <div className="segment-row">
              {(["16:9", "9:16", "1:1"] as const).map((ratio) => (
                <button
                  key={ratio}
                  className={ratio === form.aspect_ratio ? "segment active" : "segment"}
                  type="button"
                  onClick={() => updateField("aspect_ratio", ratio)}
                >
                  {ratio}
                </button>
              ))}
            </div>
          </fieldset>

          <label className="toggle-row">
            <input
              type="checkbox"
              checked={form.render_video}
              onChange={(event) => updateField("render_video", event.target.checked)}
            />
            <span>
              Render MP4 after IR generation
              <small>
                Projects now start in the background and the selected run streams stage updates
                over WebSocket while detail polling keeps persisted artifacts refreshed.
              </small>
            </span>
          </label>
        </form>

        <section className="panel list-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Project Runs</p>
              <h2>Recent history</h2>
            </div>
            <button className="ghost-button" type="button" onClick={() => void refreshProjects()}>
              Refresh
            </button>
          </div>

          {loadingProjects ? <p className="muted-copy">Loading projects...</p> : null}
          {appError ? <p className="error-copy">{appError}</p> : null}

          <div className="project-list">
            {projects.length === 0 ? (
              <div className="empty-state">
                <h3>No runs yet</h3>
                <p>Submit a brief to populate the timeline and inspect the generated artifacts.</p>
              </div>
            ) : null}

            {projects.map((project) => (
              <button
                key={project.project_id}
                className={
                  project.project_id === selectedProjectId
                    ? "project-card active"
                    : "project-card"
                }
                type="button"
                onClick={() => {
                  startTransition(() => {
                    setSelectedProjectId(project.project_id);
                  });
                }}
              >
                <div className="project-card-top">
                  <strong>{project.title}</strong>
                  <span className={`status-pill ${statusTone(project.status)}`}>
                    {project.status}
                  </span>
                </div>
                <p>{project.project_id}</p>
                <div className="project-card-meta">
                  <span>{project.theme_name}</span>
                  <span>{project.duration}s</span>
                  <span>{project.scene_count} scenes</span>
                  <span>{formatDate(project.updated_at)}</span>
                </div>
              </button>
            ))}
          </div>
        </section>
      </section>

      <section className="detail-panel">
        <div className="panel detail-header">
          <div>
            <p className="eyebrow">Selected Run</p>
            <h2>{selectedProject?.title ?? "Choose a project"}</h2>
            <p className="detail-copy">
              {selectedProject
                ? selectedProject.brief
                : "Select a project card to inspect the live stage graph, render output, verifier notes, logs, and raw IR."}
            </p>
          </div>
          {selectedProject ? (
            <div className="header-chips">
              <span className={`status-pill ${statusTone(selectedProject.status)}`}>
                {selectedProject.status}
              </span>
              <span className={`status-pill ${statusTone(socketState === "live" ? "running" : socketState)}`}>
                {socketLabel(socketState)}
              </span>
              <span
                className={`status-pill ${statusTone(selectedProject.verification?.status ?? null)}`}
              >
                {selectedProject.verification?.status ?? "pending verification"}
              </span>
            </div>
          ) : null}
        </div>

        {detailError ? <p className="error-copy">{detailError}</p> : null}
        {loadingDetail && selectedProject ? (
          <p className="muted-copy">Refreshing project detail...</p>
        ) : null}

        {selectedProject ? (
          <>
            <section className="panel pipeline-panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Live Pipeline</p>
                  <h3>Stage graph</h3>
                </div>
                <div className="pipeline-meta">
                  <span className={`status-pill ${statusTone(currentProgressEvent?.status ?? null)}`}>
                    {progressPercent}% complete
                  </span>
                  <span className={`status-pill ${statusTone(socketState === "live" ? "running" : socketState)}`}>
                    {socketLabel(socketState)}
                  </span>
                </div>
              </div>

              <div className="progress-meter" aria-hidden="true">
                <div className="progress-track">
                  <div className="progress-fill" style={{width: `${progressPercent}%`}} />
                </div>
                <span className="mini-note">
                  {currentProgressEvent?.message ?? "Waiting for stage updates."}
                </span>
              </div>

              <div className="pipeline-graph">
                {stageCards.map((stage, index) => (
                  <article key={stage.id} className={`stage-card ${statusTone(stage.status)}`}>
                    <div className="stage-head">
                      <span className="stage-index">{String(index + 1).padStart(2, "0")}</span>
                      <span className={`status-pill ${statusTone(stage.status)}`}>{stage.status}</span>
                    </div>
                    <h4>{stage.label}</h4>
                    <p className="stage-summary">{stage.summary}</p>
                    <p className="stage-message">{stage.message}</p>
                    <span className="mini-note">
                      {stage.timestamp ? formatDate(stage.timestamp) : "Waiting"}
                    </span>
                  </article>
                ))}
              </div>

              <div className="activity-list">
                {liveActivity.length === 0 ? (
                  <p className="muted-copy">
                    No live events have been received for this project yet.
                  </p>
                ) : null}
                {liveActivity.map((event) => (
                  <article
                    key={`${event.event}-${event.stage}-${event.timestamp}-${event.message}`}
                    className="activity-entry"
                  >
                    <div className="log-head">
                      <strong>
                        {event.stage === "pipeline"
                          ? "Pipeline"
                          : formatAgentName(event.stage)}
                      </strong>
                      <span>{formatDate(event.timestamp)}</span>
                    </div>
                    <p>{event.message}</p>
                    <span className={`status-pill ${statusTone(event.status)}`}>{event.status}</span>
                  </article>
                ))}
              </div>
            </section>

            <div className="detail-grid">
              <article className="panel video-panel">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">Render</p>
                    <h3>Output preview</h3>
                  </div>
                  <span className="mini-note">
                    Updated {formatDate(selectedProject.updated_at)}
                  </span>
                </div>

                {selectedProjectVideoUrl ? (
                  <div className="video-shell">
                    <video
                      className="video-player"
                      controls
                      preload="metadata"
                      src={selectedProjectVideoUrl}
                    />
                  </div>
                ) : (
                  <div className="video-placeholder">
                    <p>No rendered MP4 yet.</p>
                    <span>Enable render mode or wait for the current run to complete.</span>
                  </div>
                )}

                <div className="stat-grid">
                  <div className="stat-card">
                    <span>Duration</span>
                    <strong>{selectedProject.duration}s</strong>
                  </div>
                  <div className="stat-card">
                    <span>Scenes</span>
                    <strong>{selectedProject.scene_count}</strong>
                  </div>
                  <div className="stat-card">
                    <span>Aspect</span>
                    <strong>{selectedProject.aspect_ratio}</strong>
                  </div>
                  <div className="stat-card">
                    <span>Theme</span>
                    <strong>{selectedProject.theme_name}</strong>
                  </div>
                </div>
              </article>

              <aside className="panel side-panel">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">Verifier</p>
                    <h3>Checks</h3>
                  </div>
                </div>

                {selectedProject.verification ? (
                  <div className="verification-stack">
                    <div className={`status-banner ${statusTone(selectedProject.verification.status)}`}>
                      {selectedProject.verification.status}
                    </div>
                    {selectedProject.verification.errors.length > 0 ? (
                      <div className="issue-block">
                        <h4>Errors</h4>
                        {selectedProject.verification.errors.map((issue) => (
                          <p key={`${issue.check}-${issue.message}`}>
                            <strong>{issue.check}</strong>
                            {issue.message}
                          </p>
                        ))}
                      </div>
                    ) : null}
                    {selectedProject.verification.warnings.length > 0 ? (
                      <div className="issue-block">
                        <h4>Warnings</h4>
                        {selectedProject.verification.warnings.map((issue) => (
                          <p key={`${issue.check}-${issue.message}`}>
                            <strong>{issue.check}</strong>
                            {issue.message}
                          </p>
                        ))}
                      </div>
                    ) : (
                      <p className="muted-copy">No warnings captured on this run.</p>
                    )}
                  </div>
                ) : (
                  <p className="muted-copy">
                    Verification data will appear here once generation finishes.
                  </p>
                )}

                <div className="project-facts">
                  <div>
                    <span>Project ID</span>
                    <strong>{selectedProject.project_id}</strong>
                  </div>
                  <div>
                    <span>Platform</span>
                    <strong>{selectedProject.platform}</strong>
                  </div>
                  <div>
                    <span>LLM</span>
                    <strong>
                      {selectedProject.summary?.llm_configured ? "Configured" : "Deterministic"}
                    </strong>
                  </div>
                  <div>
                    <span>Artifacts</span>
                    <strong>{selectedProject.render_path ? "IR + MP4" : "IR only"}</strong>
                  </div>
                </div>
              </aside>
            </div>

            <section className="panel tab-panel">
              <div className="tab-strip">
                {(["overview", "logs", "ir"] as const).map((tab) => (
                  <button
                    key={tab}
                    className={tab === activeTab ? "tab-button active" : "tab-button"}
                    type="button"
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab === "ir" ? "IR Viewer" : tab[0].toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>

              {activeTab === "overview" ? (
                <div className="overview-grid">
                  <div className="overview-card">
                    <span>Summary</span>
                    <strong>{selectedProject.summary?.render_status ?? "pending"}</strong>
                    <p>
                      {selectedProject.summary
                        ? `${selectedProject.summary.scene_count} scenes across ${selectedProject.summary.duration}s using ${selectedProject.summary.theme_name}.`
                        : "The run has not persisted a summary yet."}
                    </p>
                  </div>
                  <div className="overview-card">
                    <span>Render Path</span>
                    <strong>{selectedProject.render_path ? "Available" : "Not rendered"}</strong>
                    <p>{selectedProject.render_path ?? "No MP4 was produced for this project."}</p>
                  </div>
                  <div className="overview-card">
                    <span>IR Path</span>
                    <strong>{selectedProject.ir_path ? "Persisted" : "Pending"}</strong>
                    <p>{selectedProject.ir_path ?? "The IR document has not been saved yet."}</p>
                  </div>
                  <div className="overview-card">
                    <span>Failure State</span>
                    <strong>{selectedProject.error_message ? "Needs attention" : "Clear"}</strong>
                    <p>{selectedProject.error_message ?? "No backend error recorded for this run."}</p>
                  </div>
                </div>
              ) : null}

              {activeTab === "logs" ? (
                <div className="log-list">
                  {selectedProject.logs.length === 0 ? (
                    <p className="muted-copy">Agent logs will populate after the pipeline persists.</p>
                  ) : null}
                  {selectedProject.logs.map((entry) => (
                    <article key={`${entry.agent}-${entry.timestamp}-${entry.message}`} className="log-entry">
                      <div className="log-head">
                        <strong>{formatAgentName(entry.agent)}</strong>
                        <span>{formatDate(entry.timestamp)}</span>
                      </div>
                      <p>{entry.message}</p>
                      <span className={`status-pill ${statusTone(entry.status)}`}>{entry.status}</span>
                    </article>
                  ))}
                </div>
              ) : null}

              {activeTab === "ir" ? (
                <div className="ir-panel">
                  <div className="ir-header">
                    <div>
                      <span className="eyebrow">Structured Output</span>
                      <h3>Video IR</h3>
                    </div>
                    {selectedProject.ir_path ? (
                      <a
                        className="ghost-button link-button"
                        href={mediaUrl("ir", selectedProject.ir_path) ?? "#"}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open JSON
                      </a>
                    ) : null}
                  </div>
                  <pre className="ir-viewer">
                    <code>{deferredIrJson || "No IR has been stored for this project yet."}</code>
                  </pre>
                </div>
              ) : null}
            </section>
          </>
        ) : (
          <section className="panel empty-detail">
            <h3>No project selected</h3>
            <p>Run the form on the left or pick an existing project to inspect the current pipeline output.</p>
          </section>
        )}
      </section>
    </main>
  );
}

export default App;
