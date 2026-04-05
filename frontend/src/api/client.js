// ─────────────────────────────────────────────
// All API calls in one place
// Change BASE_URL once to point anywhere
// ─────────────────────────────────────────────
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: BASE_URL });

// ── Resumes ───────────────────────────────────
export const uploadResumes = (files) => {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  return api.post("/resumes/upload", form);
};

export const listResumes  = ()         => api.get("/resumes/list");
export const deleteResume = (filename) => api.delete(`/resumes/${encodeURIComponent(filename)}`);

// ── Chat ──────────────────────────────────────
export const askGeneral   = (payload)  => api.post("/chat/ask", payload);
export const askCandidate = (payload)  => api.post("/chat/ask-candidate", payload);
export const getModels    = ()         => api.get("/chat/models");

// ── Jobs ──────────────────────────────────────
export const scoreResumes = (payload)  => api.post("/jobs/score", payload);

// ── Health ────────────────────────────────────
export const healthCheck  = ()         => api.get("/health");