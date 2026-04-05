import { useEffect } from "react";
import useStore from "./store/useStore";
import { listResumes, healthCheck } from "./api/client";
import Sidebar from "./components/Layout/Sidebar";
import Header from "./components/Layout/Header";
import ScorePanel from "./components/Jobs/ScorePanel";
import ChatPanel from "./components/Chat/ChatPanel";
import ResumePanel from "./components/Resumes/ResumePanel";
import "./styles/globals.css";

const bounce = `@keyframes bounce {
  0%,80%,100%{transform:translateY(0);opacity:0.4}
  40%{transform:translateY(-5px);opacity:1}
}`;

export default function App() {
  const { activeTab, toast, setResumes } = useStore();

  useEffect(() => {
    listResumes()
      .then((r) => setResumes(r.data.resumes || []))
      .catch(() => {});
  }, []);

  return (
    <>
      <style>{bounce}</style>
      <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
        <Sidebar />
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          <Header />
          <main style={{ flex: 1, overflow: "hidden" }}>
            {activeTab === "score" && <ScorePanel />}
            {activeTab === "chat"  && <ChatPanel />}
            {activeTab === "resumes" && <ResumePanel />}
          </main>
        </div>
      </div>

      {/* Toast */}
      {toast && (
        <div style={{
          position: "fixed", bottom: 20, right: 20,
          background: "var(--card)", border: "1px solid",
          borderColor: toast.type === "error" ? "rgba(242,107,107,0.3)" : "rgba(61,214,140,0.3)",
          borderRadius: "var(--radius-sm)", padding: "10px 16px",
          fontSize: 13,
          color: toast.type === "error" ? "var(--red)" : "var(--green)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
          animation: "fadeUp 0.3s ease", zIndex: 999,
        }}>
          {toast.msg}
        </div>
      )}
    </>
  );
}