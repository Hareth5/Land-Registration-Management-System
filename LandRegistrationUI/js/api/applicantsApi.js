import { request } from "./http.js";

export const applicantsApi = {
  create(payload) {
    return request("/applicants/", { method: "POST", body: payload });
  },
  get(applicantId) {
    return request(`/applicants/${encodeURIComponent(applicantId)}`);
  },
  applications(applicantId) {
    return request(`/applicants/${encodeURIComponent(applicantId)}/applications`);
  },
};
