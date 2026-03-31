/**
 * AssetManager.tsx — Simple UI to manage project assets.
 * Let's users register external URLs for images, fonts, audio, and SVG.
 */

import {useState, useCallback} from "react";
import {apiBaseUrl} from "../api";

export interface AssetManagerProps {
  projectId: string;
  assets?: Record<string, any[]>;
  onMutationComplete?: () => void;
}

export function AssetManager({projectId, assets, onMutationComplete}: AssetManagerProps) {
  const [assetType, setAssetType] = useState<"images" | "audio" | "svg" | "fonts">("images");
  const [assetId, setAssetId] = useState("");
  const [assetUrl, setAssetUrl] = useState("");
  const [saving, setSaving] = useState(false);

  const handleAddAsset = useCallback(async () => {
    if (!assetId.trim() || !assetUrl.trim()) return;
    
    setSaving(true);
    try {
      const payload = {
        id: assetId.trim(),
        path: assetUrl.trim(),
        ...(assetType === "fonts" ? {family: assetId.trim(), source: assetUrl.trim()} : {})
      };
      
      const res = await fetch(`${apiBaseUrl}/api/projects/${projectId}/ir`, {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ops: [
            {
              op: "add_asset",
              asset_type: assetType,
              asset: payload,
            },
          ],
        }),
      });

      if (res.ok) {
        setAssetId("");
        setAssetUrl("");
        onMutationComplete?.();
      }
    } finally {
      setSaving(false);
    }
  }, [projectId, assetType, assetId, assetUrl, onMutationComplete]);

  const existingAssets = assets?.[assetType] || [];

  return (
    <section className="panel asset-manager-panel" style={{marginTop: "16px"}}>
      <div className="section-heading">
        <div>
          <p className="eyebrow">Project Media</p>
          <h3>Asset Manager</h3>
        </div>
      </div>

      <div style={{display: "flex", gap: "12px", marginTop: "12px", flexDirection: "column"}}>
        <div style={{display: "flex", gap: "8px", flexDirection: "column", background: "#f9f9fc", padding: "12px", borderRadius: "8px", border: "1px solid #e8e8f0"}}>
          <p style={{fontSize: "11px", fontWeight: 600, color: "#1c1c2e", marginBottom: "4px"}}>Register New Asset</p>
          <select 
            value={assetType}
            onChange={(e) => setAssetType(e.target.value as any)}
            style={{padding: "6px", borderRadius: "4px", border: "1px solid #d8dce2"}}
          >
            <option value="images">Image (png/jpg)</option>
            <option value="svg">SVG Graphic</option>
            <option value="audio">Audio (mp3/wav)</option>
            <option value="fonts">Custom Font (ttf/woff2)</option>
          </select>
          <input 
            type="text" 
            placeholder="Asset ID (e.g. 'logo-main')" 
            value={assetId}
            onChange={(e) => setAssetId(e.target.value)}
            style={{padding: "6px", borderRadius: "4px", border: "1px solid #d8dce2"}}
          />
          <input 
            type="text" 
            placeholder="URL (e.g. 'https://example.com/logo.png')" 
            value={assetUrl}
            onChange={(e) => setAssetUrl(e.target.value)}
            style={{padding: "6px", borderRadius: "4px", border: "1px solid #d8dce2"}}
          />
          <button 
            type="button" 
            className="primary-button" 
            onClick={() => void handleAddAsset()}
            disabled={saving || !assetId.trim() || !assetUrl.trim()}
          >
            {saving ? "Registering…" : "Register Asset"}
          </button>
        </div>

        {existingAssets.length > 0 && (
          <div style={{marginTop: "8px"}}>
            <p style={{fontSize: "11px", fontWeight: 600, color: "#6a6a80", marginBottom: "8px", textTransform: "uppercase"}}>
              Registered {assetType}
            </p>
            <div style={{display: "flex", flexDirection: "column", gap: "6px", maxHeight: "150px", overflowY: "auto"}}>
              {existingAssets.map((asset: any) => (
                <div key={asset.id} style={{fontSize: "11px", background: "#fff", padding: "6px 8px", borderRadius: "4px", border: "1px solid #e8e8f0", display: "flex", justifyContent: "space-between"}}>
                  <strong>{asset.id}</strong>
                  <span style={{color: "#5BA8A0", textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap", maxWidth: "150px"}}>{asset.path || asset.source}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
