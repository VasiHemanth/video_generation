/**
 * ExportPanel.tsx — UI for jumping between visual themes and exporting mapped to specific platforms.
 */

import {useEffect, useState} from "react";
import {apiBaseUrl, listThemes} from "../api";
import type {ExportPreset} from "../types";

export interface ExportPanelProps {
  projectId: string;
  currentTheme: string;
  onMutationComplete?: () => void;
}

export function ExportPanel({
  projectId,
  currentTheme,
  onMutationComplete,
}: ExportPanelProps) {
  const [themes, setThemes] = useState<string[]>([]);
  const [presets, setPresets] = useState<ExportPreset[]>([]);
  const [selectedTheme, setSelectedTheme] = useState(currentTheme);
  const [selectedPreset, setSelectedPreset] = useState<string>("");
  const [submittingTheme, setSubmittingTheme] = useState(false);
  const [submittingExport, setSubmittingExport] = useState(false);

  useEffect(() => {
    setSelectedTheme(currentTheme);
  }, [currentTheme]);

  useEffect(() => {
    async function loadData() {
      try {
        const [themeList, presetRes] = await Promise.all([
          listThemes(),
          fetch(`${apiBaseUrl}/api/export/presets`).then(r => r.json() as Promise<{presets: ExportPreset[]}>),
        ]);
        setThemes(themeList);
        setPresets(presetRes.presets);
        if (presetRes.presets.length > 0) {
          setSelectedPreset(presetRes.presets[0].slug);
        }
      } catch (err) {
        // Silently ignore loading errors.
      }
    }
    void loadData();
  }, []);

  async function handleThemeSwap() {
    if (selectedTheme === currentTheme) return;
    setSubmittingTheme(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/projects/${projectId}/ir`, {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ops: [{op: "swap_theme", theme_name: selectedTheme}],
        }),
      });
      if (res.ok) {
        onMutationComplete?.();
      }
    } finally {
      setSubmittingTheme(false);
    }
  }

  async function handleExport() {
    if (!selectedPreset) return;
    setSubmittingExport(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/projects/${projectId}/export/${selectedPreset}`, {
        method: "POST",
      });
      if (res.ok) {
        onMutationComplete?.();
      }
    } finally {
      setSubmittingExport(false);
    }
  }

  return (
    <section className="panel export-panel" style={{display: "flex", gap: "24px", flexDirection: "row", flexWrap: "wrap", padding: "18px 24px"}}>
      
      {/* Theme Swapper */}
      <div style={{flex: 1, minWidth: "200px"}}>
        <label className="eyebrow" style={{display: "block", marginBottom: "8px"}}>Theme Override</label>
        <div style={{display: "flex", gap: "8px"}}>
          <select 
            value={selectedTheme} 
            onChange={e => setSelectedTheme(e.target.value)}
            style={{flex: 1, padding: "8px 12px", height: "40px"}}
          >
            {themes.map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <button 
            type="button" 
            className="ghost-button" 
            onClick={() => void handleThemeSwap()}
            disabled={submittingTheme || selectedTheme === currentTheme}
            style={{padding: "4px 14px", height: "40px"}}
          >
             {submittingTheme ? "..." : "Apply"}
          </button>
        </div>
      </div>

      {/* Exporter */}
      <div style={{flex: 1, minWidth: "200px"}}>
        <label className="eyebrow" style={{display: "block", marginBottom: "8px"}}>Platform Export</label>
        <div style={{display: "flex", gap: "8px"}}>
          <select 
            value={selectedPreset} 
            onChange={e => setSelectedPreset(e.target.value)}
            style={{flex: 1, padding: "8px 12px", height: "40px"}}
          >
            {presets.map(p => (
              <option key={p.slug} value={p.slug}>
                {p.label} ({p.aspect_ratio})
              </option>
            ))}
          </select>
          <button 
            type="button" 
            className="primary-button" 
            onClick={() => void handleExport()}
            disabled={submittingExport}
            style={{padding: "4px 14px", height: "40px"}}
          >
             {submittingExport ? "Exporting..." : "Export"}
          </button>
        </div>
      </div>

    </section>
  );
}
