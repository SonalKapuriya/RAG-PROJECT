import { useEffect, useState } from "react";
import useStore from "../../store/useStore";
import { deleteResume, listResumes } from "../../api/client";

const FileIcon  = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>;
const TrashIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M3 6h18M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6M10 11v6M14 11v6"/></svg>;

export default function ResumePanel() {
  const { resumes, setResumes, showToast } = useStore();
  const [deleting, setDeleting] = useState(null);

  const fetchResumes = () =>
    listResumes().then((r) => setResumes(r.data.resumes || []));

  useEffect(() => { fetchResumes(); }, []);

  const handleDelete = async (filename) => {
    setDeleting(filename);
    try {
      await deleteResume(filename);
      showToast(`${filename} deleted from system and Qdrant`);
      fetchResumes();
    } catch {
      showToast("Delete failed", "error");
    } finally { setDeleting(null); }
  };

  return (
    <div style={{ padding: "24px", overflowY: "auto", height: "100%" }}>
      <div style={{ fontFamily: "var(--font-head)", fontSize: 18, fontWeight: 700, marginBottom: 4 }}>
        Uploaded Resumes
      </div>
      <div style={{ fontSize: 13, color: "var(--muted)", marginBottom: 20 }}>
        {resumes.length} resume{resumes.length !== 1 ? "s" : ""} indexed in Qdrant —
        deleting removes all vectors permanently
      </div>

      {resumes.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--muted)" }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>📂</div>
          <div style={{ fontFamily: "var(--font-head)", fontSize: 15, color: "var(--text)", marginBottom: 6 }}>
            No resumes uploaded yet
          </div>
          <div style={{ fontSize: 13 }}>Upload PDFs from the sidebar to get started</div>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12 }}>
          {resumes.map((r) => (
            <div key={r.filename} className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {/* Icon + name */}
              <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                <span style={{ color: "var(--accent2)", flexShrink: 0, marginTop: 1 }}><FileIcon /></span>
                <span style={{ fontSize: 13, fontWeight: 500, wordBreak: "break-all", lineHeight: 1.5 }}>
                  {r.filename}
                </span>
              </div>

              {/* Chunk count */}
              <div style={{ fontSize: 11, color: "var(--muted)" }}>
                {r.chunks} chunks stored in Qdrant
              </div>

              {/* Delete button */}
              <button
                className="btn btn-danger"
                style={{ fontSize: 12, padding: "6px 12px", width: "100%", justifyContent: "center" }}
                disabled={deleting === r.filename}
                onClick={() => handleDelete(r.filename)}
              >
                {deleting === r.filename
                  ? <><div className="spinner" style={{ width: 12, height: 12, borderWidth: 1.5 }} /> Deleting...</>
                  : <><TrashIcon /> Delete resume</>
                }
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}