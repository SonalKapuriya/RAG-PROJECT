// ─────────────────────────────────────────────
// The CORE feature — paste a JD,
// get all candidates scored and ranked
// ─────────────────────────────────────────────
import { useState } from "react";
import useStore from "../../store/useStore";
import { scoreResumes } from "../../api/client";

const rec_badge = {
  "Strong Yes": "badge-green",
  "Yes":        "badge-accent",
  "Maybe":      "badge-amber",
  "No":         "badge-red",
};

function ScoreBar({ score }) {
  const color = score >= 70 ? "var(--green)" : score >= 50 ? "var(--amber)" : "var(--red)";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div style={{ flex: 1, height: 5, background: "var(--border)", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ width: `${score}%`, height: "100%", background: color,
          borderRadius: 3, transition: "width 0.6s ease" }} />
      </div>
      <span style={{ fontSize: 13, fontWeight: 600, color, minWidth: 32, textAlign: "right" }}>{score}</span>
    </div>
  );
}

function CandidateCard({ candidate, rank, onChat }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card fade-up" style={{ marginBottom: 10 }}>
      {/* Header row */}
      <div style={{ display: "flex", alignItems: "flex-start", gap: 12, marginBottom: 10 }}>
        <div style={{
          width: 32, height: 32, borderRadius: "50%", flexShrink: 0,
          background: "var(--border)", display: "flex", alignItems: "center",
          justifyContent: "center", fontSize: 12, fontWeight: 700,
          color: "var(--muted)", fontFamily: "var(--font-head)",
        }}>{rank}</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ fontWeight: 600, fontSize: 14, fontFamily: "var(--font-head)" }}>
              {candidate.resume_name.replace(".pdf", "")}
            </span>
            <span className={`badge ${rec_badge[candidate.recommendation] || "badge-muted"}`}>
              {candidate.recommendation}
            </span>
          </div>
          <div style={{ marginTop: 6 }}>
            <ScoreBar score={candidate.score} />
          </div>
        </div>
        <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
          <button className="btn btn-ghost" style={{ padding: "5px 10px", fontSize: 12 }}
            onClick={() => setExpanded(!expanded)}>
            {expanded ? "Less" : "Details"}
          </button>
          <button className="btn btn-primary" style={{ padding: "5px 10px", fontSize: 12 }}
            onClick={() => onChat(candidate.resume_name)}>
            Chat
          </button>
        </div>
      </div>

      {/* Summary */}
      <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.6 }}>{candidate.summary}</p>

      {/* Expanded details */}
      {expanded && (
        <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>
            <div style={{ fontSize: 11, color: "var(--green)", fontWeight: 600,
              textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 6 }}>
              Strengths
            </div>
            {candidate.strengths.map((s, i) => (
              <div key={i} style={{ fontSize: 12, color: "var(--text)", marginBottom: 4,
                paddingLeft: 10, borderLeft: "2px solid var(--green)" }}>
                {s}
              </div>
            ))}
          </div>
          <div>
            <div style={{ fontSize: 11, color: "var(--red)", fontWeight: 600,
              textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 6 }}>
              Gaps
            </div>
            {candidate.gaps.map((g, i) => (
              <div key={i} style={{ fontSize: 12, color: "var(--text)", marginBottom: 4,
                paddingLeft: 10, borderLeft: "2px solid var(--red)" }}>
                {g}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ScorePanel() {
  const { llmSettings, setActiveTab, setSelectedCandidate, showToast } = useStore();
  const [jd, setJd]           = useState("");
  const [topN, setTopN]       = useState(10);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleScore = async () => {
    if (!jd.trim()) { showToast("Paste a job description first", "error"); return; }
    setLoading(true);
    setResults(null);
    try {
      const res = await scoreResumes({
        job_description: jd,
        top_n: topN,
        settings: llmSettings,
      });
      setResults(res.data);
    } catch (e) {
      showToast(e.response?.data?.detail || "Scoring failed", "error");
    } finally { setLoading(false); }
  };

  const handleChat = (resumeName) => {
    setSelectedCandidate(resumeName);
    setActiveTab("chat");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
      {/* Input section */}
      <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border)" }}>
        <div style={{ fontFamily: "var(--font-head)", fontSize: 18, fontWeight: 700, marginBottom: 4 }}>
          Screen candidates
        </div>
        <div style={{ fontSize: 13, color: "var(--muted)", marginBottom: 14 }}>
          Paste a job description — every resume is scored and ranked automatically
        </div>

        <textarea
          className="input"
          placeholder="Paste the job description here...&#10;&#10;e.g. We are looking for a Senior Python Developer with 4+ years of experience in FastAPI, machine learning, and cloud deployment..."
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          style={{ minHeight: 120, resize: "vertical", lineHeight: 1.6 }}
        />

        <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <label style={{ fontSize: 12, color: "var(--muted)" }}>Show top</label>
            <select className="input" style={{ width: 64, padding: "6px 8px" }}
              value={topN} onChange={(e) => setTopN(Number(e.target.value))}>
              {[5, 10, 20, 50].map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleScore} disabled={loading || !jd.trim()}>
            {loading ? <><div className="spinner" /> Scoring all resumes...</> : "Score candidates"}
          </button>
          {results && (
            <span style={{ fontSize: 12, color: "var(--muted)" }}>
              {results.total_resumes} candidates scored
            </span>
          )}
        </div>
      </div>

      {/* Results */}
      <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px" }}>
        {!results && !loading && (
          <div style={{ textAlign: "center", padding: "60px 0", color: "var(--muted)" }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>📋</div>
            <div style={{ fontFamily: "var(--font-head)", fontSize: 16, color: "var(--text)", marginBottom: 6 }}>
              Paste a job description to get started
            </div>
            <div style={{ fontSize: 13 }}>
              All uploaded resumes will be scored and ranked against it
            </div>
          </div>
        )}
        {loading && (
          <div style={{ textAlign: "center", padding: "60px 0", color: "var(--muted)" }}>
            <div className="spinner" style={{ margin: "0 auto 14px" }} />
            <div style={{ fontSize: 13 }}>Reading and scoring all resumes with AI...</div>
            <div style={{ fontSize: 12, marginTop: 6 }}>This may take 15–30 seconds</div>
          </div>
        )}
        {results?.candidates?.map((c, i) => (
          <CandidateCard key={c.resume_name} candidate={c} rank={i + 1} onChat={handleChat} />
        ))}
      </div>
    </div>
  );
}