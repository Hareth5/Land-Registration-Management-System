document.addEventListener("DOMContentLoaded", function () {
  renderLayout("review");

  const form = document.getElementById("registrarReviewForm");

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    UI.clearMessage("message");

    const applicationId = document.getElementById("applicationId").value.trim();

    const payload = {
      reviewed_by: document.getElementById("reviewedBy").value.trim(),
      decision: document.getElementById("decision").value,
      notes: document.getElementById("notes").value.trim()
    };

    try {
      await AssignmentsApi.registrarReview(applicationId, payload);
      UI.showMessage("message", "Registrar review completed successfully.", "success");
      form.reset();
    } catch (error) {
      UI.showMessage("message", error.message, "error");
    }
  });
});
