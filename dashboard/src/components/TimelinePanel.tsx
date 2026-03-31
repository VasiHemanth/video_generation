/**
 * TimelinePanel.tsx — Scene timeline strip with drag-and-drop reordering.
 *
 * Renders a horizontal filmstrip of scenes. Each card is proportional to its
 * duration. Scenes can be dragged to reorder (mouse & touch). Selecting a
 * scene card opens an inline duration editor. The "Re-render" button triggers
 * POST /api/projects/{id}/re-render.
 */

import {useCallback, useEffect, useRef, useState} from "react";
import type {Scene} from "../types";
import {apiBaseUrl} from "../api";

interface TimelinePanelProps {
  projectId: string;
  scenes: Scene[];
  totalDuration: number;
  renderPath: string | null;
  onReorder?: (newOrder: Scene[]) => void;
  onRerenderRequested?: () => void;
}

const ROLE_COLORS: Record<string, string> = {
  intro:   "#5BA8A0",
  setup:   "#7B6BA4",
  demo:    "#E8913A",
  payoff:  "#4A90D9",
  feature: "#7B6BA4",
  solution:"#5BA8A0",
  cta:     "#E05C5C",
};

function roleColor(role: string): string {
  return ROLE_COLORS[role.toLowerCase()] ?? "#6B7280";
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

export function TimelinePanel({
  projectId,
  scenes,
  totalDuration,
  renderPath,
  onReorder,
  onRerenderRequested,
}: TimelinePanelProps) {
  const [orderedScenes, setOrderedScenes] = useState<Scene[]>(scenes);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [editDuration, setEditDuration] = useState<string>("");
  const [dragging, setDragging] = useState<number | null>(null);
  const [dragOver, setDragOver] = useState<number | null>(null);
  const [rerendering, setRerendering] = useState(false);
  const [rerenderStatus, setRerenderStatus] = useState<string | null>(null);
  const dragNode = useRef<number | null>(null);

  useEffect(() => {
    setOrderedScenes(scenes);
  }, [scenes]);

  // ── Drag handlers ───────────────────────────────────────────────────────
  const handleDragStart = useCallback((index: number) => {
    dragNode.current = index;
    setDragging(index);
  }, []);

  const handleDragEnter = useCallback((index: number) => {
    setDragOver(index);
  }, []);

  const handleDragEnd = useCallback(() => {
    const from = dragNode.current;
    const to = dragOver;
    if (from !== null && to !== null && from !== to) {
      const next = [...orderedScenes];
      const [removed] = next.splice(from, 1);
      next.splice(to, 0, removed);
      setOrderedScenes(next);
      onReorder?.(next);
    }
    dragNode.current = null;
    setDragging(null);
    setDragOver(null);
  }, [dragOver, orderedScenes, onReorder]);

  // ── Duration edit ────────────────────────────────────────────────────
  function startEdit(index: number) {
    setSelectedIndex(index);
    setEditDuration(String(orderedScenes[index].duration));
  }

  async function commitDurationEdit(index: number) {
    const parsed = parseFloat(editDuration);
    if (!Number.isFinite(parsed) || parsed < 1) return;

    const scene = orderedScenes[index];
    try {
      await fetch(`${apiBaseUrl}/api/projects/${projectId}/ir`, {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ops: [{op: "set_scene_duration", scene_id: scene.id, duration: parsed}],
        }),
      });
      const next = orderedScenes.map((s, i) =>
        i === index ? {...s, duration: parsed} : s
      );
      setOrderedScenes(next);
    } catch {
      // silently ignore; user can retry
    }
    setSelectedIndex(null);
  }

  // ── Re-render ────────────────────────────────────────────────────────
  async function triggerRerender() {
    setRerendering(true);
    setRerenderStatus("Queued…");
    try {
      const res = await fetch(`${apiBaseUrl}/api/projects/${projectId}/re-render`, {
        method: "POST",
      });
      if (res.ok) {
        setRerenderStatus("Rendering in background…");
        onRerenderRequested?.();
      } else {
        setRerenderStatus("Re-render failed.");
      }
    } catch {
      setRerenderStatus("Network error.");
    } finally {
      setRerendering(false);
    }
  }

  const containerWidth = 100; // percent units

  return (
    <section className="panel timeline-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Scene Timeline</p>
          <h3>Drag to reorder · Click to edit duration</h3>
        </div>
        <div style={{display: "flex", gap: 8, alignItems: "center"}}>
          {rerenderStatus && (
            <span className="mini-note" style={{color: "#5BA8A0"}}>{rerenderStatus}</span>
          )}
          <button
            className="primary-button"
            type="button"
            disabled={rerendering}
            onClick={() => void triggerRerender()}
          >
            {rerendering ? "Queueing…" : "⟳ Re-render"}
          </button>
        </div>
      </div>

      {/* Total duration rail */}
      <div className="timeline-duration-label">
        <span>{totalDuration.toFixed(1)}s total · {orderedScenes.length} scenes</span>
      </div>

      {/* Horizontal filmstrip */}
      <div className="timeline-strip" role="list">
        {orderedScenes.map((scene, index) => {
          const widthPct = (scene.duration / totalDuration) * containerWidth;
          const isDragging = dragging === index;
          const isOver = dragOver === index;
          const isSelected = selectedIndex === index;
          const color = roleColor(scene.role);

          return (
            <div
              key={scene.id}
              role="listitem"
              className={[
                "timeline-card",
                isDragging ? "dragging" : "",
                isOver ? "drag-over" : "",
                isSelected ? "selected" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              style={{
                width: `${clamp(widthPct, 5, 50)}%`,
                borderTop: `3px solid ${color}`,
              }}
              draggable
              onDragStart={() => handleDragStart(index)}
              onDragEnter={() => handleDragEnter(index)}
              onDragEnd={handleDragEnd}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => {
                if (isSelected) {
                  setSelectedIndex(null);
                } else {
                  startEdit(index);
                }
              }}
            >
              {/* Role pill */}
              <span
                className="timeline-role"
                style={{background: `${color}22`, color}}
              >
                {scene.role}
              </span>

              {/* Title */}
              <p className="timeline-title">
                {(scene.title ?? scene.id).substring(0, 36)}
              </p>

              {/* Duration badge / edit input */}
              {isSelected ? (
                <div
                  className="timeline-dur-edit"
                  onClick={(e) => e.stopPropagation()}
                >
                  <input
                    type="number"
                    min={1}
                    step={0.5}
                    value={editDuration}
                    onChange={(e) => setEditDuration(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") void commitDurationEdit(index);
                      if (e.key === "Escape") setSelectedIndex(null);
                    }}
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={() => void commitDurationEdit(index)}
                  >
                    ✓
                  </button>
                </div>
              ) : (
                <span className="timeline-dur">{scene.duration.toFixed(1)}s</span>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
