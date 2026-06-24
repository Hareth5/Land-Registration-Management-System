import { staffApi } from "../api/staffApi.js";
import { field, formShell } from "../components/forms.js";
import { notify, reportError } from "../components/notifications.js";
import { escapeHtml, formatDate, labelize, qs, serializeForm, splitList } from "../core/utils.js";

export function renderStaff(container) {
  container.innerHTML = `
    <section class="page-grid">
      <article class="page-section span-7">
        <div class="section-header"><div><h2>Create staff</h2></div></div>
        <div class="section-body">
          ${formShell("staffForm", [
            field({ label: "Staff code", name: "staff_code", required: true }),
            field({ label: "Name", name: "name", required: true }),
            field({ label: "Role", name: "role", options: ["surveyor", "registrar"], required: true }),
            field({ label: "Department", name: "department", required: true }),
            field({ label: "Skills", name: "skills", placeholder: "Comma-separated" }),
            field({ label: "Email", name: "email", type: "email", required: true }),
            field({ label: "Phone", name: "phone", required: true }),
            field({ label: "Coverage zones", name: "zone_ids", placeholder: "Comma-separated zone IDs", required: true }),
            field({ label: "Active tasks", name: "active_tasks", type: "number", value: "0" }),
            field({ label: "Max tasks", name: "max_tasks", type: "number", value: "10" }),
          ], "Create staff")}
        </div>
      </article>
      <article class="page-section span-5">
        <div class="section-header"><div><h2>Staff lookup</h2></div></div>
        <div class="section-body">
          <form id="staffLookupForm" class="form-grid">
            ${field({ label: "Staff Mongo ID", name: "staff_id", full: true, required: true })}
            <div class="form-field full"><button class="button" type="submit">Load staff</button></div>
          </form>
        </div>
      </article>
    </section>
    <section class="page-section" id="staffResult"></section>
  `;
  qs("#staffForm", container).addEventListener("submit", createStaff);
  qs("#staffLookupForm", container).addEventListener("submit", lookupStaff);
}

async function createStaff(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const raw = serializeForm(form);
  const payload = {
    staff_code: raw.staff_code,
    name: raw.name,
    role: raw.role,
    department: raw.department,
    skills: splitList(raw.skills),
    contacts: { phone: raw.phone, email: raw.email },
    coverage: { zone_ids: splitList(raw.zone_ids) },
    workload: { active_tasks: Number(raw.active_tasks || 0), max_tasks: Number(raw.max_tasks || 10) },
    active: true,
  };
  try {
    const result = await staffApi.create(payload);
    notify(`Staff created: ${result.staff_id}`);
    form.reset();
  } catch (error) {
    reportError(error);
  }
}

async function lookupStaff(event) {
  event.preventDefault();
  const { staff_id } = serializeForm(event.currentTarget);
  try {
    const staff = await staffApi.get(staff_id);
    qs("#staffResult").innerHTML = `
      <div class="section-header"><div><h2>${escapeHtml(staff.name)}</h2><p>${escapeHtml(staff.staff_code)} - ${escapeHtml(labelize(staff.role))}</p></div>${staff.active ? '<span class="status-pill success">active</span>' : '<span class="status-pill danger">inactive</span>'}</div>
      <div class="section-body">
        <dl class="detail-list">
          <div><dt>Email</dt><dd>${escapeHtml(staff.contacts?.email)}</dd></div>
          <div><dt>Phone</dt><dd>${escapeHtml(staff.contacts?.phone)}</dd></div>
          <div><dt>Zones</dt><dd>${escapeHtml((staff.coverage?.zone_ids || []).join(", "))}</dd></div>
          <div><dt>Workload</dt><dd>${escapeHtml(staff.workload?.active_tasks)} / ${escapeHtml(staff.workload?.max_tasks)}</dd></div>
          <div><dt>Skills</dt><dd>${escapeHtml((staff.skills || []).join(", "))}</dd></div>
          <div><dt>Created</dt><dd>${escapeHtml(formatDate(staff.created_at))}</dd></div>
        </dl>
      </div>
    `;
  } catch (error) {
    reportError(error);
  }
}
