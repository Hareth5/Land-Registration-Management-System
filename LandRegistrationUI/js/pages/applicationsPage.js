import { applicationsApi } from "../api/applicationsApi.js";
import { APPLICATION_STATUSES, APPLICATION_TYPES, ALLOWED_TRANSITIONS } from "../core/constants.js";
import { state } from "../core/state.js";
import { escapeHtml, formatDate, labelize, qs, serializeForm, splitList, statusPill } from "../core/utils.js";
import { renderTable } from "../components/table.js";
import { field, formShell } from "../components/forms.js";
import { openModal } from "../components/modal.js";
import { notify, reportError } from "../components/notifications.js";

let root;

export async function renderApplications(container) {
  root = container;
  root.innerHTML = `<div class="empty-state">Loading applications...</div>`;
  await loadApplications();
  draw();
}

async function loadApplications(filters = {}) {
  try {
    state.applications = await applicationsApi.list({ ...filters, limit: 100 });
  } catch (error) {
    state.applications = [];
    reportError(error);
  }
}

function draw() {
  root.innerHTML = `
    <section class="page-section">
      <div class="section-header">
        <div><h2>Applications register</h2><p>Create, filter, inspect, and advance land registration cases.</p></div>
        <button class="button" id="newApplicationBtn" type="button">New application</button>
      </div>
      <div class="section-body">
        <form class="filters" id="applicationFilters">
          <select name="status"><option value="">All statuses</option>${APPLICATION_STATUSES.map((s) => `<option value="${s}">${labelize(s)}</option>`).join("")}</select>
          <select name="application_type"><option value="">All types</option>${APPLICATION_TYPES.map((s) => `<option value="${s}">${labelize(s)}</option>`).join("")}</select>
          <input name="sort_field" value="timestamps.submitted_at" aria-label="Sort field" />
          <select name="sort_order"><option value="-1">Newest first</option><option value="1">Oldest first</option></select>
          <button class="button secondary" type="submit">Apply</button>
        </form>
      </div>
      <div class="section-body">
        ${renderTable({
          rows: state.applications,
          empty: "No applications match the current filters.",
          columns: [
            { label: "Application", render: (row) => `<button class="button secondary" data-view-app="${escapeHtml(row.application_id)}" type="button">${escapeHtml(row.application_id)}</button>` },
            { label: "Type", render: (row) => escapeHtml(labelize(row.application_type)) },
            { label: "Status", render: (row) => statusPill(row.status) },
            { label: "Applicant", render: (row) => escapeHtml(row.applicant_ref?.applicant_id) },
            { label: "Parcel", render: (row) => escapeHtml(row.parcel_ref?.parcel_id || row.parcel_ref?.parcel_number || "Not set") },
            { label: "Updated", render: (row) => escapeHtml(formatDate(row.timestamps?.updated_at)) },
          ],
        })}
      </div>
    </section>
  `;
  bind();
}

function bind() {
  qs("#newApplicationBtn", root).addEventListener("click", openCreateApplication);
  qs("#applicationFilters", root).addEventListener("submit", async (event) => {
    event.preventDefault();
    await loadApplications(serializeForm(event.currentTarget));
    draw();
  });
  root.addEventListener("click", async (event) => {
    const id = event.target.closest("[data-view-app]")?.dataset.viewApp;
    if (id) openApplicationDetail(id);
  });
}

function openCreateApplication() {
  const modal = openModal({
    title: "Create application",
    body: formShell("createApplicationForm", [
      field({ label: "Application type", name: "application_type", options: APPLICATION_TYPES, required: true }),
      field({ label: "Applicant ID", name: "applicant_id", required: true }),
      field({ label: "Parcel ID", name: "parcel_id", required: true }),
    ], "Create application"),
  });
  qs("#createApplicationForm", modal.root).addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const result = await applicationsApi.create(serializeForm(event.currentTarget));
      notify(`Application ${result.application_id} created`);
      modal.close();
      await renderApplications(root);
    } catch (error) {
      reportError(error);
    }
  });
}

async function openApplicationDetail(applicationId) {
  try {
    const app = await applicationsApi.get(applicationId);
    state.selectedApplication = app;
    const allowed = ALLOWED_TRANSITIONS[app.status] || app.workflow?.allowed_next || [];
    const docs = app.required_documents || [];
    const notes = app.internal?.notes || [];
    const modal = openModal({
      title: `Application ${escapeHtml(app.application_id)}`,
      body: `
        <dl class="detail-list">
          <div><dt>Status</dt><dd>${statusPill(app.status)}</dd></div>
          <div><dt>Type</dt><dd>${escapeHtml(labelize(app.application_type))}</dd></div>
          <div><dt>Applicant</dt><dd>${escapeHtml(app.applicant_ref?.applicant_id)}</dd></div>
          <div><dt>Parcel</dt><dd>${escapeHtml(app.parcel_ref?.parcel_id || "Not set")}</dd></div>
          <div><dt>Zone</dt><dd>${escapeHtml(app.parcel_ref?.zone_id || "Missing from backend record")}</dd></div>
          <div><dt>Updated</dt><dd>${escapeHtml(formatDate(app.timestamps?.updated_at))}</dd></div>
        </dl>
        <hr />
        <div class="workflow-actions">
          <div class="button-row">
            ${allowed.map((status) => `<button class="button secondary" data-transition="${status}" type="button">Move to ${labelize(status)}</button>`).join("") || `<span class="muted">No standard transition is available from this status.</span>`}
          </div>
          <div class="button-row">
            <button class="button secondary" data-action="note" type="button">Add note</button>
            <button class="button warning" data-action="missing" type="button">Missing documents</button>
            <button class="button warning" data-action="hold" type="button">Place on hold</button>
            <button class="button warning" data-action="objection" type="button">Record objection</button>
            <button class="button danger" data-action="reject" type="button">Reject</button>
            <button class="button" data-action="certificate" type="button">Issue certificate</button>
          </div>
        </div>
        <h3>Documents</h3>
        <div class="document-chips">${docs.length ? docs.map((doc) => `<span class="document-chip">${escapeHtml(labelize(doc.document_type))}: ${escapeHtml(labelize(doc.status))}</span>`).join("") : `<span class="muted">No document records are exposed for this application.</span>`}</div>
        <h3>Notes</h3>
        <ul class="timeline">${notes.length ? notes.map((note) => `<li>${escapeHtml(note.note || note)}</li>`).join("") : `<li>No notes recorded.</li>`}</ul>
      `,
    });

    modal.root.addEventListener("click", async (event) => {
      const transition = event.target.closest("[data-transition]")?.dataset.transition;
      const action = event.target.closest("[data-action]")?.dataset.action;
      if (transition) await runAction(() => applicationsApi.transition(app.application_id, transition), modal, `Moved to ${labelize(transition)}`);
      if (action) await handleApplicationAction(action, app.application_id, modal);
    });
  } catch (error) {
    reportError(error);
  }
}

async function handleApplicationAction(action, applicationId, modal) {
  if (action === "certificate") return runAction(() => applicationsApi.certificate(applicationId), modal, "Certificate issued");
  const prompts = {
    note: ["Note", "note", "Add note"],
    missing: ["Missing documents", "documents", "Mark missing documents"],
    hold: ["Hold reason", "reason", "Place on hold"],
    objection: ["Objection reason", "reason", "Record objection"],
    reject: ["Rejection reason", "reason", "Reject application"],
  };
  const [label, name, button] = prompts[action];
  const prompt = openModal({
    title: button,
    body: formShell("applicationActionForm", [field({ label, name, type: "textarea", full: true, required: true, placeholder: action === "missing" ? "Comma-separated document names" : "" })], button),
  });
  qs("#applicationActionForm", prompt.root).addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = serializeForm(event.currentTarget);
    const calls = {
      note: () => applicationsApi.addNote(applicationId, data.note),
      missing: () => applicationsApi.missingDocuments(applicationId, splitList(data.documents)),
      hold: () => applicationsApi.hold(applicationId, data.reason),
      objection: () => applicationsApi.objection(applicationId, data.reason),
      reject: () => applicationsApi.reject(applicationId, data.reason),
    };
    await runAction(calls[action], prompt, button);
    modal.close();
  });
}

async function runAction(action, modal, message) {
  try {
    await action();
    notify(message);
    modal.close();
    await renderApplications(root);
  } catch (error) {
    reportError(error);
  }
}
