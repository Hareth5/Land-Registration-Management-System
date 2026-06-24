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

export const applicantsApi = {
  create(payload) {
    return apiFetch("/applicants/", { method: "POST", body: payload });
  },
  get(applicantId) {
    return apiFetch(`/applicants/${encodeURIComponent(applicantId)}`);
  },
  applications(applicantId) {
    return apiFetch(`/applicants/${encodeURIComponent(applicantId)}/applications`);
  },
};
