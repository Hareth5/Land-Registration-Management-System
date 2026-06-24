window.AssignmentsApi = {
  autoAssignSurveyor: function (applicationId) {
    return apiRequest(`/applications/${applicationId}/auto-assign-surveyor`, {
      method: "POST"
    });
  },

  addSurveyMilestone: function (applicationId, payload) {
    return apiRequest(`/applications/${applicationId}/survey-milestone`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },

  addSurveyReport: function (applicationId, payload) {
    return apiRequest(`/applications/${applicationId}/survey-report`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  registrarReview: function (applicationId, payload) {
    return apiRequest(`/applications/${applicationId}/registrar-review`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  }
};