/**
 * CanvasEditor.tsx — WYSIWYG Layout Canvas for the Project IR.
 *
 * Renders a scaled viewport matching the IR dimensions. Each element
 * in the active scene is rendered as a positioned, draggable div.
 * On drag-end the new position is written back to the IR via PATCH.
 */

import {useCallback, useEffect, useRef, useState} from "react";
import {apiBaseUrl} from "../api";

/* ── Types (mirrored from ProjectIR, kept local to avoid cross-package) ── */

interface Position {
  x: number | string;
  y: number | string;
}
interface Size {
  width: number | string;
  height: number | string;
}

interface CanvasElement {
  id: string;
  type: string;
  props: Record<string, unknown>;
  position: Position;
  size?: Size | null;
  anchor?: string | null;
  layer: number;
  opacity?: number;
  scale?: number;
  rotation?: number;
}

interface Background {
  type: string;
  colors: string[];
  angle?: number | null;
}

interface CanvasScene {
  id: string;
  role: string;
  title?: string | null;
  duration: number;
  background: Background;
  elements: CanvasElement[];
}

interface ThemeColors {
  bg_primary: string;
  bg_secondary: string;
  fg_primary: string;
  fg_secondary: string;
  accent_1: string;
  accent_2: string;
  accent_3: string;
  gradient_start: string;
  gradient_end: string;
  surface: string;
  border: string;
  [key: string]: string;
}

export interface CanvasEditorProps {
  projectId: string;
  scenes: CanvasScene[];
  irWidth: number;
  irHeight: number;
  themeColors: ThemeColors;
  onMutationComplete?: () => void;
}

/* ── Helpers ─────────────────────────────────────────────────────────── */

function resolvePercent(val: number | string, container: number): number {
  if (typeof val === "number") return val;
  if (val.endsWith("%")) return (parseFloat(val) / 100) * container;
  return parseFloat(val) || 0;
}

function toIrValue(px: number, container: number): string {
  const pct = (px / container) * 100;
  return `${Math.round(pct * 10) / 10}%`;
}

function resolveColor(token: string, colors: ThemeColors): string {
  return colors[token] ?? token;
}

function buildBackground(bg: Background, colors: ThemeColors): string {
  if (bg.type === "gradient" && bg.colors.length >= 2) {
    const resolved = bg.colors.map((c) => resolveColor(c, colors));
    const angle = bg.angle ?? 135;
    return `linear-gradient(${angle}deg, ${resolved.join(", ")})`;
  }
  return resolveColor(bg.colors[0] ?? "bg_primary", colors);
}

/* ── Drag state ──────────────────────────────────────────────────────── */

interface DragState {
  elementId: string;
  startMouseX: number;
  startMouseY: number;
  startElX: number;
  startElY: number;
}

/* ── Component ───────────────────────────────────────────────────────── */

export function CanvasEditor({
  projectId,
  scenes,
  irWidth,
  irHeight,
  themeColors,
  onMutationComplete,
}: CanvasEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeSceneIdx, setActiveSceneIdx] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [drag, setDrag] = useState<DragState | null>(null);
  const [elementPositions, setElementPositions] = useState<
    Record<string, {x: number; y: number}>
  >({});
  const [saving, setSaving] = useState(false);
  const [viewportScale, setViewportScale] = useState(1);

  const scene = scenes[activeSceneIdx];

  // Recalculate viewport scale whenever the container or IR dims change.
  useEffect(() => {
    if (!containerRef.current) return;
    const obs = new ResizeObserver(([entry]) => {
      const cw = entry.contentRect.width;
      // Leave a small margin for the selection outlines
      const scale = Math.min((cw - 4) / irWidth, 1);
      setViewportScale(scale);
    });
    obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, [irWidth]);

  // Reset element positions when scene changes.
  useEffect(() => {
    if (!scene) return;
    const positions: Record<string, {x: number; y: number}> = {};
    for (const el of scene.elements) {
      positions[el.id] = {
        x: resolvePercent(el.position.x, irWidth),
        y: resolvePercent(el.position.y, irHeight),
      };
    }
    setElementPositions(positions);
    setSelectedId(null);
  }, [activeSceneIdx, scene, irWidth, irHeight]);

  /* ── Pointer handlers ────────────────────────────────────────────── */

  const handlePointerDown = useCallback(
    (e: React.PointerEvent, elementId: string) => {
      e.stopPropagation();
      e.preventDefault();
      (e.target as HTMLElement).setPointerCapture(e.pointerId);
      setSelectedId(elementId);

      const pos = elementPositions[elementId];
      if (!pos) return;

      setDrag({
        elementId,
        startMouseX: e.clientX,
        startMouseY: e.clientY,
        startElX: pos.x,
        startElY: pos.y,
      });
    },
    [elementPositions],
  );

  const handlePointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (!drag) return;
      const dx = (e.clientX - drag.startMouseX) / viewportScale;
      const dy = (e.clientY - drag.startMouseY) / viewportScale;
      setElementPositions((prev) => ({
        ...prev,
        [drag.elementId]: {
          x: Math.max(0, Math.min(irWidth, drag.startElX + dx)),
          y: Math.max(0, Math.min(irHeight, drag.startElY + dy)),
        },
      }));
    },
    [drag, viewportScale, irWidth, irHeight],
  );

  const handlePointerUp = useCallback(async () => {
    if (!drag) return;
    const pos = elementPositions[drag.elementId];
    setDrag(null);
    if (!pos || !scene) return;

    // Patch the IR with the new position for this element.
    setSaving(true);
    try {
      await fetch(`${apiBaseUrl}/api/projects/${projectId}/ir`, {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ops: [
            {
              op: "set_element_position",
              scene_id: scene.id,
              element_id: drag.elementId,
              x: toIrValue(pos.x, irWidth),
              y: toIrValue(pos.y, irHeight),
            },
          ],
        }),
      });
      onMutationComplete?.();
    } catch {
      // Revert on failure would go here
    } finally {
      setSaving(false);
    }
  }, [drag, elementPositions, scene, projectId, irWidth, irHeight, onMutationComplete]);

  const handleCanvasClick = useCallback(() => {
    setSelectedId(null);
  }, []);

  if (!scene) return null;

  /* ── Element size heuristics (matching Remotion's ElementRenderer) ──── */
  function elementSize(el: CanvasElement): {w: number; h: number} {
    if (el.size) {
      return {
        w: resolvePercent(el.size.width, irWidth),
        h: resolvePercent(el.size.height, irHeight),
      };
    }
    // Fallback defaults matching ElementRenderer
    switch (el.type) {
      case "device":
        return {w: 400, h: el.props.variant === "phone" ? 800 : 250};
      case "shape":
        return {w: 200, h: 200};
      case "progress":
        return {w: 600, h: 24};
      case "text":
        return {w: 500, h: 80};
      case "counter":
        return {w: 300, h: 80};
      default:
        return {w: 200, h: 80};
    }
  }

  /* ── Anchor transform offset ────────────────────────────────────── */
  function anchorOffset(anchor: string | null | undefined): {dx: number; dy: number} {
    switch (anchor) {
      case "top-left":
        return {dx: 0, dy: 0};
      case "top-right":
        return {dx: -1, dy: 0};
      case "bottom-left":
        return {dx: 0, dy: -1};
      case "bottom-right":
        return {dx: -1, dy: -1};
      case "top-center":
        return {dx: -0.5, dy: 0};
      case "bottom-center":
        return {dx: -0.5, dy: -1};
      case "center-left":
        return {dx: 0, dy: -0.5};
      case "center-right":
        return {dx: -1, dy: -0.5};
      case "center":
      default:
        return {dx: -0.5, dy: -0.5};
    }
  }

  /* ── Element type label / icon (small badge) ───────────────────── */
  function elementLabel(el: CanvasElement): string {
    switch (el.type) {
      case "text":
        return `T "${String(el.props.content ?? "").slice(0, 20)}"`;
      case "shape":
        return `◆ ${String(el.props.shape ?? "rect")}`;
      case "counter":
        return `# counter`;
      case "progress":
        return `▬ progress`;
      case "device":
        return `📱 ${String(el.props.variant ?? "browser")}`;
      case "group":
        return `⊞ group`;
      case "svg-icon":
        return `◎ ${String(el.props.icon ?? "icon")}`;
      case "svg-path":
        return `✎ path`;
      case "particle-field":
        return `✦ particles`;
      case "divider":
        return `— divider`;
      default:
        return el.type;
    }
  }

  /* ── Rendering ─────────────────────────────────────────────────── */

  const sortedElements = [...scene.elements].sort((a, b) => a.layer - b.layer);
  const vpWidth = irWidth * viewportScale;
  const vpHeight = irHeight * viewportScale;

  return (
    <section className="panel canvas-editor-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Layout Canvas</p>
          <h3>Drag elements to reposition</h3>
        </div>
        <div className="canvas-scene-selector">
          {scenes.map((s, i) => (
            <button
              key={s.id}
              type="button"
              className={`scene-tab ${i === activeSceneIdx ? "active" : ""}`}
              onClick={() => setActiveSceneIdx(i)}
            >
              {s.title ?? s.role}
            </button>
          ))}
        </div>
      </div>

      {saving && <div className="canvas-saving-indicator">Saving…</div>}

      <div className="canvas-container" ref={containerRef}>
        <div
          className="canvas-viewport"
          style={{
            width: vpWidth,
            height: vpHeight,
            background: buildBackground(scene.background, themeColors),
            position: "relative",
            overflow: "hidden",
            borderRadius: "8px",
            boxShadow: "0 4px 24px rgba(0,0,0,0.35)",
            cursor: drag ? "grabbing" : "default",
          }}
          onPointerMove={handlePointerMove}
          onPointerUp={() => void handlePointerUp()}
          onClick={handleCanvasClick}
        >
          {sortedElements.map((el) => {
            const pos = elementPositions[el.id];
            if (!pos) return null;
            const {w, h} = elementSize(el);
            const anchor = anchorOffset(el.anchor);
            const isSelected = selectedId === el.id;
            const scale = el.scale ?? 1;

            const left = (pos.x + anchor.dx * w) * viewportScale;
            const top = (pos.y + anchor.dy * h) * viewportScale;
            const width = w * viewportScale * scale;
            const height = h * viewportScale * scale;

            return (
              <div
                key={el.id}
                className={`canvas-element ${isSelected ? "selected" : ""}`}
                style={{
                  position: "absolute",
                  left,
                  top,
                  width,
                  height,
                  opacity: el.opacity ?? 1,
                  transform: `rotate(${el.rotation ?? 0}deg)`,
                  cursor: drag?.elementId === el.id ? "grabbing" : "grab",
                  zIndex: el.layer,
                }}
                onPointerDown={(e) => handlePointerDown(e, el.id)}
              >
                {/* Element type-specific visual preview */}
                <div className="canvas-element-inner">
                  {el.type === "text" && (
                    <div
                      className="canvas-text-preview"
                      style={{
                        color: resolveColor(
                          String(el.props.color ?? "fg_primary"),
                          themeColors,
                        ),
                        fontSize: `${Math.max(10, 14 * viewportScale)}px`,
                        fontWeight: 600,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        padding: "4px",
                      }}
                    >
                      {String(el.props.content ?? "")}
                    </div>
                  )}
                  {el.type === "shape" && (
                    <div
                      className="canvas-shape-preview"
                      style={{
                        width: "100%",
                        height: "100%",
                        background: resolveColor(
                          String(el.props.fill ?? "accent_1"),
                          themeColors,
                        ),
                        borderRadius:
                          el.props.shape === "circle"
                            ? "999px"
                            : `${Number(el.props.corner_radius ?? 12)}px`,
                        opacity: 0.8,
                      }}
                    />
                  )}
                  {el.type !== "text" && el.type !== "shape" && (
                    <div className="canvas-generic-preview">
                      <span>{elementLabel(el)}</span>
                    </div>
                  )}
                </div>

                {/* Selection outline + label */}
                {isSelected && (
                  <>
                    <div className="canvas-selection-outline" />
                    <div className="canvas-element-label">
                      {elementLabel(el)}
                    </div>
                    {/* Resize handles */}
                    <div className="canvas-handle canvas-handle-tl" />
                    <div className="canvas-handle canvas-handle-tr" />
                    <div className="canvas-handle canvas-handle-bl" />
                    <div className="canvas-handle canvas-handle-br" />
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected element info strip */}
      {selectedId && scene.elements.find((e) => e.id === selectedId) && (
        <div className="canvas-info-strip">
          {(() => {
            const el = scene.elements.find((e) => e.id === selectedId)!;
            const pos = elementPositions[selectedId];
            return (
              <>
                <span className="canvas-info-label">{elementLabel(el)}</span>
                <span className="canvas-info-coord">
                  x: {pos ? Math.round(pos.x) : "—"}px
                </span>
                <span className="canvas-info-coord">
                  y: {pos ? Math.round(pos.y) : "—"}px
                </span>
                <span className="canvas-info-coord">
                  layer: {el.layer}
                </span>
                <span className="canvas-info-coord">
                  opacity: {el.opacity ?? 1}
                </span>
              </>
            );
          })()}
        </div>
      )}
    </section>
  );
}
