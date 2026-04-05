import { useState, useRef, useEffect } from "react";
import useStore from "../../store/useStore";
import { askGeneral, askCandidate } from "../../api/client";
import MessageBubble from "./MessageBubble";

const suggestions = [
  "Which candidates have Python experience?",
  "Who has worked in a startup?",
  "List candidates with ML or AI background",
  "Who has leadership or management experience?",
  "Compare the top 2 candidates",
];

export default function ChatPanel() {
  const {
    llmSettings, chatHistory, addChatPair, clearChat,
    messages, addMessage, selectedCandidate, setSelectedCandidate, showToast,
  } = useStore();

  const [input, setInput]     = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef             = useRef();
  const inputRef              = useRef();

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;
    addMessage({ role: "human", content: q });
    setInput("");
    setLoading(true);

    try {
      let data;
      if (selectedCandidate) {
        const res = await askCandidate({
          resume_name: selectedCandidate,
          question: q,
          chat_history: chatHistory,
          settings: llmSettings,
        });
        data = res.data;
      } else {
        const res = await askGeneral({
          question: q,
          chat_history: chatHistory,
          settings: llmSettings,
        });
        data = res.data;
      }
      addMessage({ role: "ai", content: data.answer });
      addChatPair(q, data.answer);
    } catch (e) {
      addMessage({ role: "ai", content: "⚠️ " + (e.response?.data?.detail || "Something went wrong") });
    } finally { setLoading(false); }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
      {/* Sub-header */}
      <div style={{
        padding: "12px 24px", borderBottom: "1px solid var(--border)",
        display: "flex", alignItems: "center", gap: 10,
      }}>
        {selectedCandidate ? (
          <>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 600 }}>
                Chatting about: <span style={{ color: "var(--accent)" }}>{selectedCandidate.replace(".pdf", "")}</span>
              </div>
              <div style={{ fontSize: 11, color: "var(--muted)" }}>Questions are scoped to this candidate only</div>
            </div>
            <button className="btn btn-ghost" style={{ fontSize: 12, padding: "5px 10px" }}
              onClick={() => { setSelectedCandidate(null); clearChat(); }}>
              All resumes
            </button>
          </>
        ) : (
          <div style={{ fontSize: 13, color: "var(--muted)" }}>
            Asking across <strong style={{ color: "var(--text)" }}>all resumes</strong> — or pick a candidate from Score panel to focus
          </div>
        )}
        {messages.length > 0 && (
          <button className="btn btn-ghost" style={{ fontSize: 12, padding: "5px 10px" }} onClick={clearChat}>
            Clear
          </button>
        )}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px",
        display: "flex", flexDirection: "column", gap: 14 }}>
        {messages.length === 0 ? (
          <div style={{ flex: 1, display: "flex", flexDirection: "column",
            alignItems: "center", justifyContent: "center", gap: 16, color: "var(--muted)" }}>
            <div style={{ fontFamily: "var(--font-head)", fontSize: 17, color: "var(--text)" }}>
              Ask anything about your candidates
            </div>
            <div style={{ fontSize: 13 }}>Try one of these:</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center", maxWidth: 520 }}>
              {suggestions.map((s) => (
                <button key={s}
                  onClick={() => { setInput(s); inputRef.current?.focus(); }}
                  style={{
                    padding: "7px 14px", borderRadius: 20,
                    background: "var(--card)", border: "1px solid var(--border)",
                    color: "var(--text)", fontSize: 12, transition: "all 0.15s",
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = "var(--accent)"; e.currentTarget.style.color = "var(--accent)"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.color = "var(--text)"; }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((m, i) => <MessageBubble key={i} message={m} />)}
            {loading && (
              <div style={{ display: "flex", gap: 10, alignSelf: "flex-start" }}>
                <div style={{ width: 30, height: 30, borderRadius: "50%", background: "var(--card)",
                  border: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <div className="spinner" style={{ width: 12, height: 12, borderWidth: 1.5 }} />
                </div>
                <div style={{ background: "var(--card)", border: "1px solid var(--border)",
                  borderRadius: 10, padding: "10px 14px", display: "flex", gap: 4, alignItems: "center" }}>
                  {[0, 150, 300].map((d) => (
                    <div key={d} style={{ width: 6, height: 6, borderRadius: "50%",
                      background: "var(--accent)", opacity: 0.4,
                      animation: `bounce 1.2s ${d}ms infinite` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div style={{ padding: "14px 24px", borderTop: "1px solid var(--border)",
        display: "flex", gap: 10, alignItems: "flex-end" }}>
        <textarea
          ref={inputRef}
          className="input"
          placeholder="Ask about candidates... (Shift+Enter for new line)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          style={{ flex: 1, resize: "none", minHeight: 44, maxHeight: 130, lineHeight: 1.5 }}
          rows={1}
        />
        <button
          className="btn btn-primary"
          onClick={send}
          disabled={!input.trim() || loading}
          style={{ height: 44, padding: "0 16px" }}
        >
          Send
        </button>
      </div>
    </div>
  );
}