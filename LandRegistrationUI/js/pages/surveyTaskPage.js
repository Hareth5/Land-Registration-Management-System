document.addEventListener("DOMContentLoaded", function () {
  renderLayout("milestone");

  const form = document.getElementById("milestoneForm");

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    UI.clearMessage("message");

    const applicationId = document.getElementById("applicationId").value.trim();

    let meta = {};
    try {
      meta = UI.parseJsonObject(document.getElementById("meta").value);
    } catch (error) {
      UI.showMessage("message", "Meta must be valid JSON.", "error");
      return;
    }

    const payload = {
      milestone_type: document.getElementById("milestoneType").value,
      by: document.getElementById("by").value,
      meta: meta
    };

    try {
      await AssignmentsApi.addSurveyMilestone(applicationId, payload);
      UI.showMessage("message", "Survey milestone added successfully.", "success");
      form.reset();
    } catch (error) {
      UI.showMessage("message", error.message, "error");
    }
  });
});
