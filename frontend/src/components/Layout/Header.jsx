import useStore from "../../store/useStore";

const tabs = [
  { id: "score", label: "Score Candidates" },
  { id: "chat",  label: "Chat with Resumes" },
  { id: "resumes", label: "Resumes" }
];

export default function Header() {
  const { activeTab, setActiveTab } = useStore();

  return (
    <header style={{
      height: 52, background: "var(--surface)",
      borderBottom: "1px solid var(--border)",
      display: "flex", alignItems: "center",
      padding: "0 24px", gap: 4,
    }}>
      {tabs.map((t) => (
        <button key={t.id}
          onClick={() => setActiveTab(t.id)}
          style={{
            padding: "6px 14px", borderRadius: "var(--radius-xs)",
            fontSize: 13, border: "1px solid",
            background: activeTab === t.id ? "rgba(91,127,255,0.1)" : "transparent",
            borderColor: activeTab === t.id ? "rgba(91,127,255,0.3)" : "transparent",
            color: activeTab === t.id ? "var(--accent)" : "var(--muted)",
            transition: "all 0.15s",
          }}
        >
          {t.label}
        </button>
      ))}
    </header>
  );
}