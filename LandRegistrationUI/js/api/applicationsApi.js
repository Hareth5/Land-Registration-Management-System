import { request } from "./http.js";

export const applicationsApi = {
  list(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") query.set(key, value);
    });
    return request(`/applications/${query.toString() ? `?${query}` : ""}`);
  },
  get(applicationId) {
    return request(`/applications/${encodeURIComponent(applicationId)}`);
  },
  create(payload) {
    return request("/applications/", { method: "POST", body: payload });
  },
  transition(applicationId, newStatus) {
    return request(`/applications/${encodeURIComponent(applicationId)}/transition`, {
      method: "PATCH",
      body: { new_status: newStatus },
    });
  },
  hold(applicationId, reason) {
    return request(`/applications/${encodeURIComponent(applicationId)}/hold`, {
      method: "POST",
      body: { reason },
    });
  },
  reject(applicationId, reason) {
    return request(`/applications/${encodeURIComponent(applicationId)}/reject`, {
      method: "POST",
      body: { reason },
    });
  },
  certificate(applicationId) {
    return request(`/applications/${encodeURIComponent(applicationId)}/certificate`, { method: "POST" });
  },
  addNote(applicationId, note) {
    return request(`/applications/${encodeURIComponent(applicationId)}/notes`, {
      method: "POST",
      body: { note },
    });
  },
  missingDocuments(applicationId, documents) {
    return request(`/applications/${encodeURIComponent(applicationId)}/missing-documents`, {
      method: "POST",
      body: { documents },
    });
  },
  objection(applicationId, reason) {
    return request(`/applications/${encodeURIComponent(applicationId)}/objection`, {
      method: "POST",
      body: { reason },
    });
  },
};
