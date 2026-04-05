import { useState, useRef, useEffect } from "react";

const API = "http://localhost:8000";

// ── Icons ─────────────────────────────────────────────────
const Icon = ({ d, size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);
const UploadIcon   = () => <Icon d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" />;
const TrashIcon    = () => <Icon d="M3 6h18M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6M10 11v6M14 11v6M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" size={15}/>;
const SendIcon     = () => <Icon d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z" size={17}/>;
const FileIcon     = () => <Icon d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8" size={15}/>;
const SparkleIcon  = () => <Icon d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z" size={15}/>;
const BotIcon      = () => <Icon d="M12 2a2 2 0 012 2v1h3a2 2 0 012 2v10a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h3V4a2 2 0 012-2zM9 11a1 1 0 100 2 1 1 0 000-2zm6 0a1 1 0 100 2 1 1 0 000-2z" />;
const ListIcon     = () => <Icon d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />;
const FilterIcon   = () => <Icon d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z" />;

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #0d0f14;
    --surface:  #151820;
    --card:     #1c2030;
    --border:   #262c3d;
    --accent:   #6c8eff;
    --accent2:  #a78bfa;
    --green:    #4ade80;
    --red:      #f87171;
    --amber:    #fbbf24;
    --text:     #e8eaf0;
    --muted:    #6b7280;
    --font-head: 'Syne', sans-serif;
    --font-body: 'DM Sans', sans-serif;
    --radius:   12px;
    --radius-sm: 8px;
  }

  body { background: var(--bg); color: var(--text); font-family: var(--font-body); min-height: 100vh; }

  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

  .app {
    display: grid;
    grid-template-columns: 280px 1fr;
    grid-template-rows: 60px 1fr;
    height: 100vh;
    overflow: hidden;
  }

  /* ── Header ── */
  .header {
    grid-column: 1 / -1;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 24px;
    gap: 12px;
  }
  .header-logo {
    font-family: var(--font-head);
    font-weight: 800;
    font-size: 18px;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .header-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 6px var(--green); }
  .header-status { font-size: 12px; color: var(--muted); font-weight: 300; }
  .tab-bar { margin-left: auto; display: flex; gap: 4px; }
  .tab {
    padding: 6px 14px;
    border-radius: var(--radius-sm);
    font-size: 13px;
    font-family: var(--font-body);
    font-weight: 400;
    cursor: pointer;
    border: 1px solid transparent;
    color: var(--muted);
    background: transparent;
    transition: all 0.15s;
    display: flex; align-items: center; gap: 6px;
  }
  .tab:hover { color: var(--text); background: var(--card); }
  .tab.active { color: var(--accent); background: rgba(108,142,255,0.1); border-color: rgba(108,142,255,0.25); }

  /* ── Sidebar ── */
  .sidebar {
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .sidebar-header {
    padding: 16px 20px 12px;
    border-bottom: 1px solid var(--border);
  }
  .sidebar-title { font-family: var(--font-head); font-size: 13px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }
  .sidebar-count { font-size: 11px; color: var(--muted); margin-top: 2px; }

  .upload-zone {
    margin: 16px;
    border: 1.5px dashed var(--border);
    border-radius: var(--radius);
    padding: 20px 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }
  .upload-zone:hover, .upload-zone.drag { border-color: var(--accent); background: rgba(108,142,255,0.05); }
  .upload-zone input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
  .upload-icon { color: var(--accent); margin-bottom: 8px; display: flex; justify-content: center; }
  .upload-text { font-size: 13px; color: var(--text); font-weight: 500; }
  .upload-sub  { font-size: 11px; color: var(--muted); margin-top: 3px; }

  .resume-list { flex: 1; overflow-y: auto; padding: 0 12px 12px; }
  .resume-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 10px;
    border-radius: var(--radius-sm);
    margin-bottom: 4px;
    transition: background 0.15s;
    group: true;
  }
  .resume-item:hover { background: var(--card); }
  .resume-icon { color: var(--accent2); flex-shrink: 0; }
  .resume-name { font-size: 12.5px; color: var(--text); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .resume-del {
    opacity: 0; color: var(--red); cursor: pointer; background: none; border: none;
    padding: 3px; border-radius: 4px; transition: opacity 0.15s;
    display: flex; align-items: center;
  }
  .resume-item:hover .resume-del { opacity: 1; }

  .uploading-bar {
    margin: 0 16px 12px;
    background: var(--card);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    font-size: 12px;
    color: var(--accent);
    display: flex; align-items: center; gap: 8px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner { width: 14px; height: 14px; border: 2px solid rgba(108,142,255,0.2); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0; }

  /* ── Main ── */
  .main { display: flex; flex-direction: column; overflow: hidden; }

  /* ── Ask panel ── */
  .ask-panel { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

  .chat-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }

  .empty-state {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 12px;
    color: var(--muted); text-align: center;
  }
  .empty-icon { width: 48px; height: 48px; border-radius: 50%; background: var(--card); display: flex; align-items: center; justify-content: center; color: var(--accent); }
  .empty-title { font-family: var(--font-head); font-size: 16px; font-weight: 600; color: var(--text); }
  .empty-sub { font-size: 13px; max-width: 280px; line-height: 1.6; }

  .suggestions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 8px; }
  .suggestion {
    padding: 7px 14px; border-radius: 20px;
    font-size: 12px; cursor: pointer;
    background: var(--card); border: 1px solid var(--border);
    color: var(--text); transition: all 0.15s;
  }
  .suggestion:hover { border-color: var(--accent); color: var(--accent); }

  .msg { display: flex; gap: 12px; max-width: 780px; }
  .msg.human { align-self: flex-end; flex-direction: row-reverse; }
  .msg-avatar {
    width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; font-size: 13px;
  }
  .msg.human .msg-avatar { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: white; font-weight: 600; }
  .msg.ai .msg-avatar { background: var(--card); border: 1px solid var(--border); color: var(--accent2); }
  .msg-bubble {
    padding: 12px 16px; border-radius: 12px;
    font-size: 14px; line-height: 1.65; max-width: calc(100% - 44px);
  }
  .msg.human .msg-bubble { background: linear-gradient(135deg, rgba(108,142,255,0.18), rgba(167,139,250,0.12)); border: 1px solid rgba(108,142,255,0.2); color: var(--text); }
  .msg.ai .msg-bubble { background: var(--card); border: 1px solid var(--border); color: var(--text); }
  .msg-bubble pre { white-space: pre-wrap; font-family: var(--font-body); }

  @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  .msg { animation: fadeUp 0.25s ease; }

  .typing { display: flex; gap: 4px; align-items: center; padding: 4px 0; }
  .typing span { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); opacity: 0.4; }
  @keyframes bounce { 0%,80%,100%{transform:translateY(0);opacity:0.4} 40%{transform:translateY(-5px);opacity:1} }
  .typing span:nth-child(1){animation:bounce 1.2s 0s infinite}
  .typing span:nth-child(2){animation:bounce 1.2s 0.15s infinite}
  .typing span:nth-child(3){animation:bounce 1.2s 0.3s infinite}

  .input-bar {
    padding: 16px 24px;
    border-top: 1px solid var(--border);
    display: flex; gap: 10px; align-items: flex-end;
  }
  .input-wrap { flex: 1; position: relative; }
  .chat-input {
    width: 100%; background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 12px 16px;
    color: var(--text); font-family: var(--font-body); font-size: 14px;
    resize: none; outline: none; line-height: 1.5;
    transition: border-color 0.15s; min-height: 48px; max-height: 140px;
  }
  .chat-input:focus { border-color: rgba(108,142,255,0.5); }
  .chat-input::placeholder { color: var(--muted); }
  .send-btn {
    width: 44px; height: 44px; border-radius: var(--radius-sm); flex-shrink: 0;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border: none; cursor: pointer; color: white;
    display: flex; align-items: center; justify-content: center;
    transition: opacity 0.15s; font-size: 14px;
  }
  .send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .send-btn:not(:disabled):hover { opacity: 0.85; }

  .mode-toggle {
    display: flex; gap: 4px; padding: 0 24px 12px;
  }
  .mode-btn {
    padding: 5px 12px; border-radius: 20px; font-size: 12px; cursor: pointer;
    border: 1px solid var(--border); background: transparent; color: var(--muted);
    transition: all 0.15s; display: flex; align-items: center; gap: 5px;
  }
  .mode-btn.active { background: rgba(108,142,255,0.1); border-color: rgba(108,142,255,0.3); color: var(--accent); }

  /* ── Shortlist panel ── */
  .shortlist-panel { flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 24px; gap: 16px; }
  .shortlist-title { font-family: var(--font-head); font-size: 20px; font-weight: 700; }
  .shortlist-sub { font-size: 13px; color: var(--muted); margin-top: 4px; }
  .criteria-input {
    width: 100%; background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 14px 16px;
    color: var(--text); font-family: var(--font-body); font-size: 14px;
    resize: none; outline: none; line-height: 1.5; height: 80px;
    transition: border-color 0.15s;
  }
  .criteria-input:focus { border-color: rgba(108,142,255,0.5); }
  .criteria-input::placeholder { color: var(--muted); }
  .shortlist-btn {
    align-self: flex-start;
    padding: 10px 24px; border-radius: var(--radius-sm);
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border: none; color: white; font-family: var(--font-body);
    font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px;
    transition: opacity 0.15s;
  }
  .shortlist-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .shortlist-result {
    flex: 1; overflow-y: auto;
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px;
    font-size: 14px; line-height: 1.75; white-space: pre-wrap;
    color: var(--text);
  }

  /* ── Resumes list panel ── */
  .resumes-panel { flex: 1; overflow-y: auto; padding: 24px; }
  .resumes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
  .resume-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 16px;
    display: flex; flex-direction: column; gap: 10px;
    transition: border-color 0.15s;
  }
  .resume-card:hover { border-color: rgba(108,142,255,0.3); }
  .resume-card-icon { color: var(--accent2); }
  .resume-card-name { font-size: 13px; font-weight: 500; word-break: break-all; }
  .resume-card-del {
    align-self: flex-start; padding: 5px 10px; border-radius: 6px;
    background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.2);
    color: var(--red); font-size: 12px; cursor: pointer;
    display: flex; align-items: center; gap: 5px; transition: all 0.15s;
  }
  .resume-card-del:hover { background: rgba(248,113,113,0.2); }

  .panel-title { font-family: var(--font-head); font-size: 20px; font-weight: 700; margin-bottom: 4px; }
  .panel-sub { font-size: 13px; color: var(--muted); margin-bottom: 20px; }

  .toast {
    position: fixed; bottom: 24px; right: 24px;
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 12px 16px;
    font-size: 13px; display: flex; align-items: center; gap: 8px;
    animation: fadeUp 0.3s ease; z-index: 100;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  }
  .toast.success { border-color: rgba(74,222,128,0.3); color: var(--green); }
  .toast.error   { border-color: rgba(248,113,113,0.3); color: var(--red); }
`;

export default function App() {
  const [tab, setTab]               = useState("ask");
  const [resumes, setResumes]       = useState([]);
  const [uploading, setUploading]   = useState(false);
  const [drag, setDrag]             = useState(false);
  const [messages, setMessages]     = useState([]);
  const [input, setInput]           = useState("");
  const [loading, setLoading]       = useState(false);
  const [mode, setMode]             = useState("chat");   // "single" | "chat"
  const [criteria, setCriteria]     = useState("");
  const [shortlistResult, setShortlistResult] = useState("");
  const [shortlistLoading, setShortlistLoading] = useState(false);
  const [toast, setToast]           = useState(null);
  const chatEndRef                  = useRef(null);
  const textareaRef                 = useRef(null);

  // chat history for /ask/chat endpoint (last 6 messages = 3 pairs)
  const [chatHistory, setChatHistory] = useState([]);

  useEffect(() => { fetchResumes(); }, []);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  const showToast = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  // ── Fetch resume list ──────────────────────────────────
  const fetchResumes = async () => {
    try {
      const res = await fetch(`${API}/resumes/list`);
      const data = await res.json();
      setResumes(data.resumes || []);
    } catch { /* qdrant not running yet */ }
  };

  // ── Upload resumes ─────────────────────────────────────
  const handleUpload = async (files) => {
    if (!files || files.length === 0) return;
    const pdfs = Array.from(files).filter(f => f.name.endsWith(".pdf"));
    if (pdfs.length === 0) { showToast("Only PDF files are accepted", "error"); return; }

    setUploading(true);
    const form = new FormData();
    pdfs.forEach(f => form.append("files", f));

    try {
      const res  = await fetch(`${API}/resumes/upload`, { method: "POST", body: form });
      const data = await res.json();
      const ok   = data.uploaded.filter(u => u.status === "success").length;
      showToast(`${ok} resume${ok !== 1 ? "s" : ""} uploaded successfully`);
      fetchResumes();
    } catch { showToast("Upload failed — is the backend running?", "error"); }
    finally  { setUploading(false); }
  };

  // ── Delete resume ──────────────────────────────────────
  const handleDelete = async (filename) => {
    try {
      await fetch(`${API}/resumes/${encodeURIComponent(filename)}`, { method: "DELETE" });
      showToast(`${filename} deleted`);
      fetchResumes();
    } catch { showToast("Delete failed", "error"); }
  };

  // ── Send question ──────────────────────────────────────
  const sendMessage = async () => {
    const q = input.trim();
    if (!q || loading) return;

    const userMsg = { role: "human", content: q };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      let res, data;
      if (mode === "chat") {
        res  = await fetch(`${API}/ask/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: q, chat_history: chatHistory })
        });
        data = await res.json();
        // update history (keep last 6 = 3 pairs)
        const newHistory = [...chatHistory, { role: "human", content: q }, { role: "ai", content: data.answer }];
        setChatHistory(newHistory.slice(-6));
      } else {
        res  = await fetch(`${API}/ask`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: q })
        });
        data = await res.json();
      }
      setMessages(prev => [...prev, { role: "ai", content: data.answer }]);
    } catch {
      setMessages(prev => [...prev, { role: "ai", content: "⚠️ Could not reach the backend. Make sure it's running on port 8000." }]);
    } finally { setLoading(false); }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  // ── Shortlist ──────────────────────────────────────────
  const handleShortlist = async () => {
    if (!criteria.trim() || shortlistLoading) return;
    setShortlistLoading(true);
    setShortlistResult("");
    try {
      const res  = await fetch(`${API}/shortlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ criteria })
      });
      const data = await res.json();
      setShortlistResult(data.shortlist);
    } catch { setShortlistResult("⚠️ Could not reach the backend."); }
    finally  { setShortlistLoading(false); }
  };

  const suggestions = [
    "Which candidates know Python?",
    "Who has ML experience?",
    "List candidates with leadership roles",
    "Who has a master's degree?",
  ];

  return (
    <>
      <style>{css}</style>
      <div className="app">

        {/* ── Header ── */}
        <header className="header">
          <div className="header-logo">RecruitAI</div>
          <div className="header-dot" />
          <span className="header-status">{resumes.length} resume{resumes.length !== 1 ? "s" : ""} indexed</span>
          <nav className="tab-bar">
            {[
              { id: "ask",       label: "Ask AI",    icon: <BotIcon /> },
              { id: "shortlist", label: "Shortlist", icon: <FilterIcon /> },
              { id: "resumes",   label: "Resumes",   icon: <ListIcon /> },
            ].map(t => (
              <button key={t.id} className={`tab ${tab === t.id ? "active" : ""}`} onClick={() => setTab(t.id)}>
                {t.icon}{t.label}
              </button>
            ))}
          </nav>
        </header>

        {/* ── Sidebar ── */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <div className="sidebar-title">Resumes</div>
            <div className="sidebar-count">{resumes.length} file{resumes.length !== 1 ? "s" : ""} indexed</div>
          </div>

          {/* Upload zone */}
          <div
            className={`upload-zone ${drag ? "drag" : ""}`}
            onDragOver={e => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={e => { e.preventDefault(); setDrag(false); handleUpload(e.dataTransfer.files); }}
          >
            <input type="file" accept=".pdf" multiple onChange={e => handleUpload(e.target.files)} />
            <div className="upload-icon"><UploadIcon /></div>
            <div className="upload-text">Drop PDFs here</div>
            <div className="upload-sub">or click to browse</div>
          </div>

          {uploading && (
            <div className="uploading-bar">
              <div className="spinner" /> Processing resumes...
            </div>
          )}

          {/* Resume list */}
          <div className="resume-list">
            {resumes.map(r => (
              <div key={r} className="resume-item">
                <span className="resume-icon"><FileIcon /></span>
                <span className="resume-name" title={r}>{r}</span>
                <button className="resume-del" onClick={() => handleDelete(r)}><TrashIcon /></button>
              </div>
            ))}
            {resumes.length === 0 && (
              <div style={{ padding: "16px 8px", fontSize: 12, color: "var(--muted)", textAlign: "center" }}>
                No resumes yet.<br />Upload PDFs to get started.
              </div>
            )}
          </div>
        </aside>

        {/* ── Main content ── */}
        <main className="main">

          {/* ASK TAB */}
          {tab === "ask" && (
            <div className="ask-panel">
              {/* Mode toggle */}
              <div className="mode-toggle" style={{ paddingTop: 16 }}>
                <button className={`mode-btn ${mode === "chat" ? "active" : ""}`} onClick={() => setMode("chat")}>
                  <BotIcon /> Chat mode
                </button>
                <button className={`mode-btn ${mode === "single" ? "active" : ""}`} onClick={() => { setMode("single"); setChatHistory([]); }}>
                  <SparkleIcon /> Single question
                </button>
                {mode === "chat" && messages.length > 0 && (
                  <button className="mode-btn" onClick={() => { setMessages([]); setChatHistory([]); }} style={{ marginLeft: "auto" }}>
                    Clear chat
                  </button>
                )}
              </div>

              {/* Chat area */}
              <div className="chat-area">
                {messages.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon"><BotIcon /></div>
                    <div className="empty-title">Ask about your candidates</div>
                    <div className="empty-sub">Upload resumes on the left, then ask anything about the candidates.</div>
                    <div className="suggestions">
                      {suggestions.map(s => (
                        <button key={s} className="suggestion" onClick={() => { setInput(s); textareaRef.current?.focus(); }}>
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <>
                    {messages.map((m, i) => (
                      <div key={i} className={`msg ${m.role}`}>
                        <div className="msg-avatar">
                          {m.role === "human" ? "HR" : <BotIcon />}
                        </div>
                        <div className="msg-bubble">
                          <pre>{m.content}</pre>
                        </div>
                      </div>
                    ))}
                    {loading && (
                      <div className="msg ai">
                        <div className="msg-avatar"><BotIcon /></div>
                        <div className="msg-bubble">
                          <div className="typing">
                            <span /><span /><span />
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={chatEndRef} />
                  </>
                )}
              </div>

              {/* Input bar */}
              <div className="input-bar">
                <div className="input-wrap">
                  <textarea
                    ref={textareaRef}
                    className="chat-input"
                    placeholder={mode === "chat" ? "Ask a follow-up question..." : "Ask a question about candidates..."}
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKey}
                    rows={1}
                  />
                </div>
                <button className="send-btn" onClick={sendMessage} disabled={!input.trim() || loading}>
                  <SendIcon />
                </button>
              </div>
            </div>
          )}

          {/* SHORTLIST TAB */}
          {tab === "shortlist" && (
            <div className="shortlist-panel">
              <div>
                <div className="panel-title">Shortlist candidates</div>
                <div className="panel-sub">Describe the ideal candidate and get a ranked list from your resume pool.</div>
              </div>
              <textarea
                className="criteria-input"
                placeholder="e.g. Python developer with 3+ years experience, ML knowledge, and startup background"
                value={criteria}
                onChange={e => setCriteria(e.target.value)}
              />
              <button className="shortlist-btn" onClick={handleShortlist} disabled={!criteria.trim() || shortlistLoading}>
                {shortlistLoading ? <><div className="spinner" /> Analyzing...</> : <><FilterIcon /> Shortlist candidates</>}
              </button>
              {shortlistResult && (
                <div className="shortlist-result">{shortlistResult}</div>
              )}
            </div>
          )}

          {/* RESUMES TAB */}
          {tab === "resumes" && (
            <div className="resumes-panel">
              <div className="panel-title">All resumes</div>
              <div className="panel-sub">{resumes.length} resume{resumes.length !== 1 ? "s" : ""} currently indexed in Qdrant</div>
              <div className="resumes-grid">
                {resumes.map(r => (
                  <div key={r} className="resume-card">
                    <div className="resume-card-icon"><FileIcon /></div>
                    <div className="resume-card-name">{r}</div>
                    <button className="resume-card-del" onClick={() => handleDelete(r)}>
                      <TrashIcon /> Delete
                    </button>
                  </div>
                ))}
                {resumes.length === 0 && (
                  <div style={{ color: "var(--muted)", fontSize: 14 }}>No resumes uploaded yet.</div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Toast */}
      {toast && <div className={`toast ${toast.type}`}>{toast.msg}</div>}
    </>
  );
}