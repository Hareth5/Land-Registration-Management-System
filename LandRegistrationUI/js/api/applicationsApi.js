import { API_CONFIG } from "../core/config.js";

async function apiFetch(path, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  const hasBody = options.body !== undefined;

  if (hasBody) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_CONFIG.BASE_URL}${path}`, {
    ...options,
    headers,
    body: hasBody ? JSON.stringify(options.body) : undefined,
  });
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = data?.detail || data?.message || `HTTP ${response.status}`;
    throw new Error(Array.isArray(message) ? message.map((item) => item.msg).join(", ") : message);
  }

  return data;
}

export const applicationsApi = {
  list(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") query.set(key, value);
    });
    return apiFetch(`/applications/${query.toString() ? `?${query}` : ""}`);
  },
  get(applicationId) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}`);
  },
  create(payload) {
    return apiFetch("/applications/", { method: "POST", body: payload });
  },
  transition(applicationId, newStatus) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/transition`, {
      method: "PATCH",
      body: { new_status: newStatus },
    });
  },
  hold(applicationId, reason) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/hold`, {
      method: "POST",
      body: { reason },
    });
  },
  reject(applicationId, reason) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/reject`, {
      method: "POST",
      body: { reason },
    });
  },
  certificate(applicationId) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/certificate`, { method: "POST" });
  },
  addNote(applicationId, note) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/notes`, {
      method: "POST",
      body: { note },
    });
  },
  missingDocuments(applicationId, documents) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/missing-documents`, {
      method: "POST",
      body: { documents },
    });
  },
  objection(applicationId, reason) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/objection`, {
      method: "POST",
      body: { reason },
    });
  },
};
