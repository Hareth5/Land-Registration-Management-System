document.addEventListener("DOMContentLoaded", function () {
  renderLayout("home");

  const apiInput = document.getElementById("apiBaseUrl");
  const form = document.getElementById("apiSettingsForm");

  if (apiInput) apiInput.value = window.AppConfig.apiBaseUrl;

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      setApiBaseUrl(apiInput.value.trim());
      UI.showMessage("message", "API base URL saved successfully", "success");
    });
  }
});
