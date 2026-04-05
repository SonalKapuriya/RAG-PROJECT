// ─────────────────────────────────────────────
// Settings panel — HR can change model,
// temperature, max_tokens, top_k live
// ─────────────────────────────────────────────
import { useEffect } from "react";
import useStore from "../../store/useStore";
import { getModels } from "../../api/client";

export default function LLMSettings() {
  const { llmSettings, setLLMSettings, availableModels, setAvailableModels } = useStore();

  useEffect(() => {
    getModels()
      .then((r) => setAvailableModels(r.data))
      .catch(() => {});
  }, []);

  const models = availableModels[llmSettings.provider] || [];

  return (
    <div style={{ padding: "0 16px 16px" }}>
      <div className="section-title" style={{ marginBottom: 10 }}>AI Settings</div>

      {/* Provider */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ fontSize: 11, color: "var(--muted)", display: "block", marginBottom: 4 }}>Provider</label>
        <div style={{ display: "flex", gap: 6 }}>
          {["groq", "gemini"].map((p) => (
            <button
              key={p}
              onClick={() => {
                const defaultModel = availableModels[p]?.[0] || "";
                setLLMSettings({ provider: p, model: defaultModel });
              }}
              style={{
                flex: 1, padding: "6px 0", borderRadius: "var(--radius-xs)",
                fontSize: 12, border: "1px solid",
                background: llmSettings.provider === p ? "rgba(91,127,255,0.15)" : "transparent",
                borderColor: llmSettings.provider === p ? "rgba(91,127,255,0.4)" : "var(--border)",
                color: llmSettings.provider === p ? "var(--accent)" : "var(--muted)",
                textTransform: "capitalize",
              }}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Model */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ fontSize: 11, color: "var(--muted)", display: "block", marginBottom: 4 }}>Model</label>
        <select
          className="input"
          style={{ padding: "8px 10px", fontSize: 12 }}
          value={llmSettings.model}
          onChange={(e) => setLLMSettings({ model: e.target.value })}
        >
          {models.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>

      {/* Temperature */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ fontSize: 11, color: "var(--muted)", display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
          <span>Temperature</span>
          <span style={{ color: "var(--accent)" }}>{llmSettings.temperature.toFixed(1)}</span>
        </label>
        <input
          type="range" min="0" max="1" step="0.1"
          value={llmSettings.temperature}
          onChange={(e) => setLLMSettings({ temperature: parseFloat(e.target.value) })}
          style={{ width: "100%", accentColor: "var(--accent)" }}
        />
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--muted)", marginTop: 2 }}>
          <span>Precise</span><span>Creative</span>
        </div>
      </div>

      {/* Top K */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ fontSize: 11, color: "var(--muted)", display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
          <span>Top-K chunks</span>
          <span style={{ color: "var(--accent)" }}>{llmSettings.top_k}</span>
        </label>
        <input
          type="range" min="1" max="20" step="1"
          value={llmSettings.top_k}
          onChange={(e) => setLLMSettings({ top_k: parseInt(e.target.value) })}
          style={{ width: "100%", accentColor: "var(--accent)" }}
        />
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--muted)", marginTop: 2 }}>
          <span>Focused</span><span>Broad</span>
        </div>
      </div>

      {/* Max tokens */}
      <div>
        <label style={{ fontSize: 11, color: "var(--muted)", display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
          <span>Max tokens</span>
          <span style={{ color: "var(--accent)" }}>{llmSettings.max_tokens}</span>
        </label>
        <input
          type="range" min="128" max="4096" step="128"
          value={llmSettings.max_tokens}
          onChange={(e) => setLLMSettings({ max_tokens: parseInt(e.target.value) })}
          style={{ width: "100%", accentColor: "var(--accent)" }}
        />
      </div>
    </div>
  );
}