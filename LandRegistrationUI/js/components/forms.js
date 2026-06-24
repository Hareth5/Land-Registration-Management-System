import { escapeHtml } from "../core/utils.js";

export function field({ label, name, type = "text", value = "", options = null, required = false, full = false, rows = 4, placeholder = "" }) {
  const requiredAttr = required ? "required" : "";
  const className = full ? "form-field full" : "form-field";
  if (options) {
    return `
      <div class="${className}">
        <label for="${name}">${escapeHtml(label)}</label>
        <select id="${name}" name="${name}" ${requiredAttr}>
          ${options.map((option) => {
            const value = typeof option === "object" ? option.value : option;
            const text = typeof option === "object" ? option.label : String(option).replaceAll("_", " ");
            const disabled = typeof option === "object" && option.disabled ? "disabled" : "";
            return `<option value="${escapeHtml(value)}" ${disabled}>${escapeHtml(text)}</option>`;
          }).join("")}
        </select>
      </div>
    `;
  }
  if (type === "textarea") {
    return `
      <div class="${className}">
        <label for="${name}">${escapeHtml(label)}</label>
        <textarea id="${name}" name="${name}" rows="${rows}" placeholder="${escapeHtml(placeholder)}" ${requiredAttr}>${escapeHtml(value)}</textarea>
      </div>
    `;
  }
  return `
    <div class="${className}">
      <label for="${name}">${escapeHtml(label)}</label>
      <input id="${name}" name="${name}" type="${type}" value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder)}" ${requiredAttr} />
    </div>
  `;
}

export function formShell(id, fields, submitLabel = "Save") {
  return `
    <form id="${id}" class="form-grid">
      ${fields.join("")}
      <div class="form-field full">
        <button class="button" type="submit">${escapeHtml(submitLabel)}</button>
      </div>
    </form>
  `;
}
