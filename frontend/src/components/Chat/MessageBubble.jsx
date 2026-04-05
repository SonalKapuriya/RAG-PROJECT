import ReactMarkdown from "react-markdown";

export default function MessageBubble({ message }) {
  const isHuman = message.role === "human";

  return (
    <div className="fade-up" style={{
      display: "flex", gap: 10, maxWidth: 760,
      alignSelf: isHuman ? "flex-end" : "flex-start",
      flexDirection: isHuman ? "row-reverse" : "row",
    }}>
      {/* Avatar */}
      <div style={{
        width: 30, height: 30, borderRadius: "50%", flexShrink: 0,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 11, fontWeight: 700, fontFamily: "var(--font-head)",
        background: isHuman
          ? "linear-gradient(135deg, var(--accent), var(--accent2))"
          : "var(--card)",
        border: isHuman ? "none" : "1px solid var(--border)",
        color: isHuman ? "white" : "var(--accent2)",
      }}>
        {isHuman ? "HR" : "AI"}
      </div>

      {/* Bubble */}
      <div style={{
        padding: "10px 14px", borderRadius: 10,
        background: isHuman
          ? "rgba(91,127,255,0.15)"
          : "var(--card)",
        border: `1px solid ${isHuman ? "rgba(91,127,255,0.2)" : "var(--border)"}`,
        fontSize: 14, lineHeight: 1.65, color: "var(--text)",
        maxWidth: "calc(100% - 42px)",
      }}>
        {isHuman
          ? <span>{message.content}</span>
          : <ReactMarkdown
              components={{
                p: ({children}) => <p style={{ marginBottom: 8 }}>{children}</p>,
                ul: ({children}) => <ul style={{ paddingLeft: 16, marginBottom: 8 }}>{children}</ul>,
                li: ({children}) => <li style={{ marginBottom: 4 }}>{children}</li>,
                strong: ({children}) => <strong style={{ color: "var(--text)", fontWeight: 600 }}>{children}</strong>,
                code: ({children}) => <code style={{ background: "var(--border)", padding: "1px 5px",
                  borderRadius: 4, fontSize: 12, fontFamily: "monospace" }}>{children}</code>,
              }}
            >{message.content}</ReactMarkdown>
        }
      </div>
    </div>
  );
}