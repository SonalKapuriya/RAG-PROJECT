import { useRef, useState } from "react";
import useStore from "../../store/useStore";
import { uploadResumes, deleteResume, listResumes } from "../../api/client";
import LLMSettings from "../Settings/LLMSettings";

const FileIcon    = () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6"/></svg>;
const TrashIcon   = () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M3 6h18M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6M10 11v6M14 11v6"/></svg>;
const UploadIcon  = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>;

export default function Sidebar() {
  const { resumes, setResumes, showToast } = useStore();
  const [uploading, setUploading] = useState(false);
  const [drag, setDrag]           = useState(false);
  const inputRef                  = useRef();

  const fetchResumes = () =>
    listResumes().then((r) => setResumes(r.data.resumes || []));

  const handleUpload = async (files) => {
    const pdfs = Array.from(files).filter((f) => f.name.endsWith(".pdf"));
    if (!pdfs.length) { showToast("Only PDF files accepted", "error"); return; }
    setUploading(true);
    try {
      const res = await uploadResumes(pdfs);
      const ok  = res.data.uploaded.filter((u) => u.status === "success").length;
      showToast(`${ok} resume${ok !== 1 ? "s" : ""} uploaded`);
      fetchResumes();
    } catch { showToast("Upload failed", "error"); }
    finally  { setUploading(false); }
  };

  const handleDelete = async (filename) => {
    try {
      await deleteResume(filename);
      showToast(`${filename} deleted`);
      fetchResumes();
    } catch { showToast("Delete failed", "error"); }
  };

  return (
    <aside style={{
      width: "var(--sidebar-w)", background: "var(--surface)",
      borderRight: "1px solid var(--border)",
      display: "flex", flexDirection: "column",
      height: "100vh", overflow: "hidden", flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{ padding: "18px 16px 14px", borderBottom: "1px solid var(--border)" }}>
        <div style={{ fontFamily: "var(--font-head)", fontSize: 17, fontWeight: 800,
          background: "linear-gradient(135deg, var(--accent), var(--accent2))",
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
          RecruitAI
        </div>
        <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2 }}>
          {resumes.length} resume{resumes.length !== 1 ? "s" : ""} indexed
        </div>
      </div>

      {/* Upload zone */}
      <div style={{ padding: "12px 16px" }}>
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => { e.preventDefault(); setDrag(false); handleUpload(e.dataTransfer.files); }}
          style={{
            border: `1.5px dashed ${drag ? "var(--accent)" : "var(--border)"}`,
            borderRadius: "var(--radius-sm)", padding: "14px 12px",
            textAlign: "center", cursor: "pointer",
            background: drag ? "rgba(91,127,255,0.05)" : "transparent",
            transition: "all 0.15s",
          }}
        >
          <input ref={inputRef} type="file" accept=".pdf" multiple
            style={{ display: "none" }}
            onChange={(e) => handleUpload(e.target.files)} />
          <div style={{ color: "var(--accent)", display: "flex", justifyContent: "center", marginBottom: 6 }}>
            <UploadIcon />
          </div>
          {uploading
            ? <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, fontSize: 12, color: "var(--accent)" }}>
                <div className="spinner" /> Processing...
              </div>
            : <>
                <div style={{ fontSize: 12, fontWeight: 500 }}>Drop PDFs or click</div>
                <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2 }}>Upload resumes</div>
              </>
          }
        </div>
      </div>

      {/* Resume list */}
      <div style={{ flex: 1, overflowY: "auto", padding: "0 8px" }}>
        <div className="section-title" style={{ padding: "0 8px" }}>Indexed resumes</div>
        {resumes.length === 0
          ? <div style={{ fontSize: 12, color: "var(--muted)", textAlign: "center", padding: "16px 8px" }}>
              No resumes yet
            </div>
          : resumes.map((r) => (
            <div key={r.filename}
              style={{
                display: "flex", alignItems: "center", gap: 8,
                padding: "8px 8px", borderRadius: "var(--radius-xs)",
                transition: "background 0.15s", cursor: "default",
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = "var(--card)"}
              onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
            >
              <span style={{ color: "var(--accent2)", flexShrink: 0 }}><FileIcon /></span>
              <span style={{ flex: 1, fontSize: 12, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
                title={r.filename}>{r.filename}</span>
              <span style={{ fontSize: 10, color: "var(--muted)", flexShrink: 0 }}>{r.chunks}c</span>
              <button
                onClick={() => handleDelete(r.filename)}
                style={{ background: "none", border: "none", color: "var(--muted)",
                  padding: "2px", borderRadius: 4, display: "flex",
                  opacity: 0, transition: "opacity 0.15s" }}
                onMouseEnter={(e) => { e.currentTarget.style.opacity = 1; e.currentTarget.style.color = "var(--red)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.opacity = 0; e.currentTarget.style.color = "var(--muted)"; }}
              >
                <TrashIcon />
              </button>
            </div>
          ))
        }
      </div>

      {/* LLM Settings at bottom */}
      <div style={{ borderTop: "1px solid var(--border)", paddingTop: 14 }}>
        <LLMSettings />
      </div>
    </aside>
  );
}