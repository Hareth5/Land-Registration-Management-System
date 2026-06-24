import { request } from "./http.js";

export const assignmentsApi = {
  autoAssignSurveyor(applicationId) {
    return request(`/applications/${encodeURIComponent(applicationId)}/auto-assign-surveyor`, { method: "POST" });
  },
  addMilestone(applicationId, payload) {
    return request(`/applications/${encodeURIComponent(applicationId)}/survey-milestone`, {
      method: "PATCH",
      body: payload,
    });
  },
  addReport(applicationId, payload) {
    return request(`/applications/${encodeURIComponent(applicationId)}/survey-report`, {
      method: "POST",
      body: payload,
    });
  },
  registrarReview(applicationId, payload) {
    return request(`/applications/${encodeURIComponent(applicationId)}/registrar-review`, {
      method: "PATCH",
      body: payload,
    });
  },
};
