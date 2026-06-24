import { request } from "./http.js";

export const staffApi = {
  create(payload) {
    return request("/staff/", { method: "POST", body: payload });
  },
  get(staffId) {
    return request(`/staff/${encodeURIComponent(staffId)}`);
  },
};
