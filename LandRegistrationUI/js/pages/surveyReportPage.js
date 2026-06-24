document.addEventListener("DOMContentLoaded", () => {
  renderLayout();

  const form = document.getElementById("surveyReportForm");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const applicationId = document.getElementById("applicationId").value.trim();
    const uploadedBy = document.getElementById("uploadedBy").value.trim();
    const reportTitle = document.getElementById("reportTitle").value.trim();
    const summary = document.getElementById("summary").value.trim();
    const fileName = document.getElementById("fileName").value.trim();

    if (!applicationId || !uploadedBy || !reportTitle || !summary || !fileName) {
      showMessage("Please fill in all required fields.", "error");
      return;
    }

    const filePath = `/uploads/reports/${fileName}`;

    const reportData = {
      uploaded_by: uploadedBy,
      report_title: reportTitle,
      summary: summary,
      file_name: fileName,
      file_path: filePath
    };

    try {
      const result = await registerSurveyReport(applicationId, reportData);

      showMessage(
        `Survey report registered successfully. Report ID: ${result.report_id}`,
        "success"
      );

      form.reset();
    } catch (error) {
      showMessage(error.message, "error");
    }
  });
});