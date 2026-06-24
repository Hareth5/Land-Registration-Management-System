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

export const staffApi = {
  create(payload) {
    return apiFetch("/staff/", { method: "POST", body: payload });
  },
  get(staffId) {
    return apiFetch(`/staff/${encodeURIComponent(staffId)}`);
  },
};
