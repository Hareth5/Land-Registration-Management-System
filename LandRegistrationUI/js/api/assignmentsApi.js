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

export const assignmentsApi = {
  autoAssignSurveyor(applicationId) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/auto-assign-surveyor`, { method: "POST" });
  },
  addMilestone(applicationId, payload) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/survey-milestone`, {
      method: "PATCH",
      body: payload,
    });
  },
  addReport(applicationId, payload) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/survey-report`, {
      method: "POST",
      body: payload,
    });
  },
  registrarReview(applicationId, payload) {
    return apiFetch(`/applications/${encodeURIComponent(applicationId)}/registrar-review`, {
      method: "PATCH",
      body: payload,
    });
  },
};
