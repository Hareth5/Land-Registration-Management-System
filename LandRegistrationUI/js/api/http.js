import { API_CONFIG } from "../core/config.js";

export async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT_MS);
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  const hasBody = options.body !== undefined;

  if (hasBody && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
      body: hasBody && !(options.body instanceof FormData) ? JSON.stringify(options.body) : options.body,
    });

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : await response.text();

    if (!response.ok) {
      const message = data?.detail || data?.message || data || `HTTP ${response.status}`;
      throw new Error(Array.isArray(message) ? message.map((item) => item.msg).join(", ") : message);
    }

    return data;
  } finally {
    clearTimeout(timeout);
  }
}
