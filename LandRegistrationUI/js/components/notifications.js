import { qs, escapeHtml } from "../core/utils.js";

export function notify(message, type = "success") {
  const root = qs("#toastRoot");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = escapeHtml(message);
  root.appendChild(toast);
  setTimeout(() => toast.remove(), 4200);
}

export function reportError(error) {
  notify(error?.message || "Something went wrong", "error");
}
