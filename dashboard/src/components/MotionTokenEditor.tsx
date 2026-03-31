/**
 * MotionTokenEditor.tsx — Visual playground for theme.motion parameters.
 *
 * Renders sliders/inputs for spring physics, durations, and easing presets.
 * Changes are applied via the IR mutation API.
 */

import {useCallback, useEffect, useState} from "react";
import {apiBaseUrl} from "../api";

interface SpringConfig {
  mass: number;
  damping: number;
  stiffness: number;
}

interface MotionConfig {
  duration_fast: number;
  duration_normal: number;
  duration_slow: number;
  duration_very_slow: number;
  easing_default: string;
  easing_enter: string;
  easing_exit: string;
  easing_bounce: string;
  easing_spring: SpringConfig;
  stagger_delay: number;
}

export interface MotionTokenEditorProps {
  projectId: string;
  motion: MotionConfig;
  onMutationComplete?: () => void;
}

const EASING_OPTIONS = [
  "ease-out-cubic",
  "ease-out-back",
  "ease-out-expo",
  "ease-in",
  "ease-in-out",
  "ease-in-cubic",
  "linear",
  "spring",
];

export function MotionTokenEditor({
  projectId,
  motion,
  onMutationComplete,
}: MotionTokenEditorProps) {
  const [local, setLocal] = useState<MotionConfig>(motion);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    setLocal(motion);
    setDirty(false);
  }, [motion]);

  const update = useCallback(
    <K extends keyof MotionConfig>(key: K, value: MotionConfig[K]) => {
      setLocal((prev) => ({...prev, [key]: value}));
      setDirty(true);
    },
    [],
  );

  const updateSpring = useCallback(
    (key: keyof SpringConfig, value: number) => {
      setLocal((prev) => ({
        ...prev,
        easing_spring: {...prev.easing_spring, [key]: value},
      }));
      setDirty(true);
    },
    [],
  );

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      // We need a "set_motion_config" op. Since our current IR mutation
      // engine doesn't have one, we use set_element_prop as a proxy
      // or just PATCH the raw motion field. For now, we build an array
      // of set_element_prop ops that target theme.motion keys.
      // Actually, the cleanest approach is to expose a new endpoint.
      // For now let's do a direct PATCH that the backend can handle.
      const res = await fetch(`${apiBaseUrl}/api/projects/${projectId}/ir`, {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ops: [
            {op: "update_theme_motion", motion: local},
          ],
        }),
      });
      if (res.ok) {
        setDirty(false);
        onMutationComplete?.();
      }
    } finally {
      setSaving(false);
    }
  }, [local, projectId, onMutationComplete]);

  return (
    <section className="panel motion-editor-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Motion Tokens</p>
          <h3>Animation timing & physics</h3>
        </div>
      </div>

      <div className="motion-editor-grid">
        {/* Duration tokens */}
        {(
          [
            ["duration_fast", 0.05, 1, 0.01],
            ["duration_normal", 0.1, 2, 0.05],
            ["duration_slow", 0.2, 3, 0.05],
            ["duration_very_slow", 0.3, 4, 0.05],
          ] as const
        ).map(([key, min, max, step]) => (
          <div key={key} className="motion-editor-card">
            <label>{key.replace("duration_", "").replace("_", " ")}</label>
            <div className="motion-slider-row">
              <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={local[key]}
                onChange={(e) => update(key, parseFloat(e.target.value))}
              />
              <span className="motion-slider-val">{local[key].toFixed(2)}s</span>
            </div>
          </div>
        ))}

        {/* Spring physics */}
        <div className="motion-editor-card">
          <label>Spring Mass</label>
          <div className="motion-slider-row">
            <input
              type="range"
              min={0.1}
              max={5}
              step={0.1}
              value={local.easing_spring.mass}
              onChange={(e) => updateSpring("mass", parseFloat(e.target.value))}
            />
            <span className="motion-slider-val">{local.easing_spring.mass.toFixed(1)}</span>
          </div>
        </div>

        <div className="motion-editor-card">
          <label>Spring Damping</label>
          <div className="motion-slider-row">
            <input
              type="range"
              min={1}
              max={40}
              step={0.5}
              value={local.easing_spring.damping}
              onChange={(e) => updateSpring("damping", parseFloat(e.target.value))}
            />
            <span className="motion-slider-val">{local.easing_spring.damping.toFixed(1)}</span>
          </div>
        </div>

        <div className="motion-editor-card">
          <label>Spring Stiffness</label>
          <div className="motion-slider-row">
            <input
              type="range"
              min={50}
              max={500}
              step={5}
              value={local.easing_spring.stiffness}
              onChange={(e) => updateSpring("stiffness", parseFloat(e.target.value))}
            />
            <span className="motion-slider-val">{local.easing_spring.stiffness.toFixed(0)}</span>
          </div>
        </div>

        {/* Stagger delay */}
        <div className="motion-editor-card">
          <label>Stagger Delay</label>
          <div className="motion-slider-row">
            <input
              type="range"
              min={0.02}
              max={0.5}
              step={0.01}
              value={local.stagger_delay}
              onChange={(e) => update("stagger_delay", parseFloat(e.target.value))}
            />
            <span className="motion-slider-val">{local.stagger_delay.toFixed(2)}s</span>
          </div>
        </div>

        {/* Easing selectors */}
        {(
          [
            ["easing_default", "Default Easing"],
            ["easing_enter", "Enter Easing"],
            ["easing_exit", "Exit Easing"],
            ["easing_bounce", "Bounce Easing"],
          ] as const
        ).map(([key, label]) => (
          <div key={key} className="motion-editor-card">
            <label>{label}</label>
            <select
              value={local[key]}
              onChange={(e) => update(key, e.target.value)}
              style={{padding: "6px 10px", borderRadius: "6px", border: "1px solid #d8dce2"}}
            >
              {EASING_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>

      <div className="motion-editor-actions">
        {dirty && (
          <button
            type="button"
            className="primary-button"
            onClick={() => void handleSave()}
            disabled={saving}
            style={{padding: "6px 20px"}}
          >
            {saving ? "Saving…" : "Apply Motion Changes"}
          </button>
        )}
      </div>
    </section>
  );
}
