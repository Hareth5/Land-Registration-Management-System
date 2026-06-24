export function qs(selector, scope = document) {
  return scope.querySelector(selector);
}

export function qsa(selector, scope = document) {
  return [...scope.querySelectorAll(selector)];
}

export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function labelize(value) {
  return String(value ?? "not set").replaceAll("_", " ");
}

export function formatDate(value) {
  if (!value) return "Not recorded";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function statusClass(status) {
  if (["approved", "certificate_issued", "closed", "surveyed"].includes(status)) return "success";
  if (["on_hold", "missing_documents", "under_objection", "needs_correction"].includes(status)) return "warning";
  if (["rejected"].includes(status)) return "danger";
  return "info";
}

export function statusPill(status) {
  return `<span class="status-pill ${statusClass(status)}">${escapeHtml(labelize(status))}</span>`;
}

export function serializeForm(form) {
  const data = new FormData(form);
  return Object.fromEntries(data.entries());
}

export function splitList(value) {
  return String(value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function groupBy(items, getter) {
  return items.reduce((acc, item) => {
    const key = getter(item) || "unknown";
    acc[key] = acc[key] || [];
    acc[key].push(item);
    return acc;
  }, {});
}

export function downloadJson(filename, payload) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
