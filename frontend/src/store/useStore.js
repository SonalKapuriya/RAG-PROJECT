// ─────────────────────────────────────────────
// Global state with Zustand
// Shared across all components
// ─────────────────────────────────────────────
import { create } from "zustand";

const useStore = create((set, get) => ({
  // ── Resumes ──────────────────────────────
  resumes: [],
  setResumes: (resumes) => set({ resumes }),

  // ── LLM Settings (dynamic per session) ───
  llmSettings: {
    provider: "groq",
    model: "llama-3.1-8b-instant",
    temperature: 0.0,
    max_tokens: 1024,
    top_k: 5,
  },
  setLLMSettings: (patch) =>
    set((s) => ({ llmSettings: { ...s.llmSettings, ...patch } })),

  // ── Available models from backend ────────
  availableModels: { groq: [], gemini: [] },
  setAvailableModels: (models) => set({ availableModels: models }),

  // ── Chat history (last 3 pairs = 6 msgs) ─
  chatHistory: [],
  addChatPair: (question, answer) =>
    set((s) => {
      const updated = [
        ...s.chatHistory,
        { role: "human", content: question },
        { role: "ai",    content: answer   },
      ];
      return { chatHistory: updated.slice(-6) };
    }),
  clearChat: () => set({ chatHistory: [], messages: [] }),

  // ── UI messages (what's rendered) ────────
  messages: [],
  addMessage: (msg) =>
    set((s) => ({ messages: [...s.messages, msg] })),

    // ── Active tab ────────────────────────────
    activeTab: "score",
  setActiveTab: (tab) => set({ activeTab: tab }),

  // ── Selected candidate (for deep-dive) ───
  selectedCandidate: null,
  setSelectedCandidate: (name) => set({ selectedCandidate: name }),

  // ── Toast ─────────────────────────────────
  toast: null,
  showToast: (msg, type = "success") => {
    set({ toast: { msg, type } });
    setTimeout(() => set({ toast: null }), 3500);
  },
}));

export default useStore;