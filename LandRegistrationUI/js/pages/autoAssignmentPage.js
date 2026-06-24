document.addEventListener("DOMContentLoaded", function () {
  renderLayout("auto");

  const form = document.getElementById("autoAssignForm");

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    UI.clearMessage("message");

    const applicationId = document.getElementById("applicationId").value.trim();

    try {
      const result = await AssignmentsApi.autoAssignSurveyor(applicationId);
      const surveyorName = result && result.assigned_surveyor_name ? ` to ${result.assigned_surveyor_name}` : "";
      const taskId = result && result.task_id ? ` Task ID: ${result.task_id}.` : "";
      UI.showMessage("message", `Surveyor assigned successfully${surveyorName}.${taskId}`, "success");
      form.reset();
    } catch (error) {
      UI.showMessage("message", error.message, "error");
    }
  });
});
