/**
 * HistoryPanel.tsx — Chronological history of IR patches / checkpoints.
 */

import {useEffect, useState, useCallback} from "react";
import {apiBaseUrl} from "../api";

export interface HistoryCheckpoint {
  id: number;
  step_name: string;
  timestamp: string;
}

export interface HistoryPanelProps {
  projectId: string;
  onRestoreComplete?: () => void;
}

export function HistoryPanel({projectId, onRestoreComplete}: HistoryPanelProps) {
  const [history, setHistory] = useState<HistoryCheckpoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [restoringId, setRestoringId] = useState<number | null>(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/projects/${projectId}/history`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchHistory();
  }, [fetchHistory]);

  const handleRestore = useCallback(
    async (id: number) => {
      setRestoringId(id);
      try {
        const res = await fetch(`${apiBaseUrl}/api/projects/${projectId}/restore/${id}`, {
          method: "POST",
        });
        if (res.ok) {
          onRestoreComplete?.();
          // Re-fetch to show the new restore commit
          void fetchHistory();
        }
      } finally {
        setRestoringId(null);
      }
    },
    [projectId, onRestoreComplete, fetchHistory],
  );

  return (
    <section className="panel history-panel">
      <div className="section-heading" style={{display: "flex", justifyContent: "space-between"}}>
        <div>
          <p className="eyebrow">Versioning</p>
          <h3>Project History</h3>
        </div>
        <button 
          className="secondary-button" 
          onClick={() => void fetchHistory()}
          style={{padding: "4px 8px"}}
        >
          Refresh
        </button>
      </div>

      {loading && history.length === 0 ? (
        <p className="muted-copy" style={{marginTop: "8px"}}>Loading history…</p>
      ) : history.length === 0 ? (
        <p className="muted-copy" style={{marginTop: "8px"}}>No edits recorded yet.</p>
      ) : (
        <div className="history-list">
          {history.map((entry, index) => {
            const date = new Date(entry.timestamp);
            const isLatest = index === 0;

            return (
              <div key={`${entry.id}-${entry.timestamp}`} className="history-entry">
                <div>
                  <div className="history-ops">{entry.step_name}</div>
                  <div className="history-ts">
                    {date.toLocaleDateString()} {date.toLocaleTimeString()}
                  </div>
                </div>
                {!isLatest && (
                  <button
                    type="button"
                    onClick={() => void handleRestore(entry.id)}
                    disabled={restoringId !== null}
                  >
                    {restoringId === entry.id ? "Restoring…" : "Restore"}
                  </button>
                )}
                {isLatest && <span style={{fontSize: "10px", color: "#5BA8A0", fontWeight: 600}}>CURRENT</span>}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
