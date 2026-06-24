window.StaffApi = {
  createStaff: function (payload) {
    return apiRequest("/staff/", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  getStaffById: function (staffId) {
    return apiRequest(`/staff/${staffId}`, {
      method: "GET"
    });
  }
};