window.AppConfig = {
  apiBaseUrl: localStorage.getItem("LRMIS_API_BASE_URL") || "http://127.0.0.1:8000"
};

window.setApiBaseUrl = function (url) {
  localStorage.setItem("LRMIS_API_BASE_URL", url);
  window.AppConfig.apiBaseUrl = url;
};

window.apiRequest = async function (path, options = {}) {
  const response = await fetch(window.AppConfig.apiBaseUrl + path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  const text = await response.text();
  let data = null;

  if (text) {
    try {
      data = JSON.parse(text);
    } catch (error) {
      data = text;
    }
  }

  if (!response.ok) {
    const detail = data && data.detail ? data.detail : "Request failed";
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return data;
};