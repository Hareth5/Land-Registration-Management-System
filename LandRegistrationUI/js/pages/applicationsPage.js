import { applicationsApi } from "../api/applicationsApi.js";
import { APPLICATION_STATUSES, APPLICATION_TYPES, ALLOWED_TRANSITIONS } from "../core/constants.js";
import { state } from "../core/state.js";
import { escapeHtml, labelize, qs, serializeForm, splitList, statusPill } from "../core/utils.js";
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
        <div><h2>Applications</h2></div>
        <button class="button" id="newApplicationBtn" type="button">New</button>
      </div>
      <div class="section-body">
        <form class="filters" id="applicationFilters">
          <select name="status"><option value="">Status</option>${APPLICATION_STATUSES.map((s) => `<option value="${s}">${labelize(s)}</option>`).join("")}</select>
          <select name="application_type"><option value="">Type</option>${APPLICATION_TYPES.map((s) => `<option value="${s}">${labelize(s)}</option>`).join("")}</select>
          <button class="button secondary" type="submit">Filter</button>
        </form>
      </div>
      <div class="section-body">
        ${renderTable({
          rows: state.applications,
          empty: "No applications match the current filters.",
          columns: [
            { label: "ID", render: (row) => `<button class="link-button" data-view-app="${escapeHtml(row.application_id)}" type="button">${escapeHtml(row.application_id)}</button>` },
            { label: "Type", render: (row) => escapeHtml(labelize(row.application_type)) },
            { label: "Status", render: (row) => statusPill(row.status) },
            { label: "Next", render: (row) => renderTransitionButtons(row, "table") },
            { label: "Applicant", render: (row) => escapeHtml(row.applicant_ref?.applicant_id) },
            { label: "Parcel", render: (row) => escapeHtml(row.parcel_ref?.parcel_id || row.parcel_ref?.parcel_number || "Not set") },
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
  root.onclick = async (event) => {
    const id = event.target.closest("[data-view-app]")?.dataset.viewApp;
    const transitionButton = event.target.closest("[data-transition-app]");
    if (id) openApplicationDetail(id);
    if (transitionButton) {
      const { transitionApp, transitionStatus } = transitionButton.dataset;
      await runAction(() => applicationsApi.transition(transitionApp, transitionStatus), null, `Moved to ${labelize(transitionStatus)}`);
    }
  };
}

function getAllowedTransitions(application) {
  return ALLOWED_TRANSITIONS[application.status] || application.workflow?.allowed_next || [];
}

function renderTransitionButtons(application, context = "modal") {
  const allowed = getAllowedTransitions(application);
  if (!allowed.length) return `<span class="muted">-</span>`;

  return `
    <div class="${context === "table" ? "next-actions" : "button-row"}">
      ${allowed
        .map(
          (status) => `
            <button
              class="button ${context === "table" ? "compact" : "secondary"}"
              data-transition-app="${escapeHtml(application.application_id)}"
              data-transition-status="${escapeHtml(status)}"
              type="button"
            >${escapeHtml(labelize(status))}</button>
          `,
        )
        .join("")}
    </div>
  `;
}

function openCreateApplication() {
  const applicantOptions = getApplicantOptions();
  const parcelOptions = getParcelOptions();
  const canCreate = applicantOptions.length > 0 && parcelOptions.length > 0;
  const modal = openModal({
    title: "Create application",
    body: `
      ${formShell("createApplicationForm", [
        field({ label: "Type", name: "application_type", options: APPLICATION_TYPES, required: true }),
        field({ label: "Applicant", name: "applicant_id", options: applicantOptions.length ? applicantOptions : [{ value: "", label: "No applicants found", disabled: true }], required: true }),
        field({ label: "Parcel", name: "parcel_id", options: parcelOptions.length ? parcelOptions : [{ value: "", label: "No parcels found", disabled: true }], required: true }),
      ], "Create")}
      ${canCreate ? "" : `<p class="form-note">Create or load records first. The backend has no applicant or parcel list endpoint, so these lists come from existing applications.</p>`}
    `,
  });
  if (!canCreate) {
    qs("#createApplicationForm button[type='submit']", modal.root).disabled = true;
  }
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

function getApplicantOptions() {
  const seen = new Map();
  state.applications.forEach((application) => {
    const ref = application.applicant_ref || {};
    const id = ref.applicant_id;
    if (!id || seen.has(id)) return;
    const name = ref.full_name || ref.name || ref.applicant_name;
    seen.set(id, {
      value: id,
      label: name ? `${name} (${id})` : `Applicant ${id}`,
    });
  });
  return [...seen.values()];
}

function getParcelOptions() {
  const seen = new Map();
  state.applications.forEach((application) => {
    const ref = application.parcel_ref || {};
    const id = ref.parcel_id;
    if (!id || seen.has(id)) return;
    const parts = [ref.parcel_number, ref.block_number && `Block ${ref.block_number}`, ref.basin_number && `Basin ${ref.basin_number}`, ref.zone_id && `Zone ${ref.zone_id}`].filter(Boolean);
    seen.set(id, {
      value: id,
      label: parts.length ? `${parts.join(" - ")} (${id})` : `Parcel ${id}`,
    });
  });
  return [...seen.values()];
}

async function openApplicationDetail(applicationId) {
  try {
    const app = await applicationsApi.get(applicationId);
    state.selectedApplication = app;
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
          <div><dt>Zone</dt><dd>${escapeHtml(app.parcel_ref?.zone_id || "-")}</dd></div>
        </dl>
        <div class="detail-block workflow-panel">
          <h3>Change status</h3>
          ${renderTransitionButtons(app)}
        </div>
        <div class="detail-block">
          <h3>Actions</h3>
          <div class="button-row">
            <button class="button secondary" data-action="note" type="button">Note</button>
            <button class="button warning" data-action="missing" type="button">Missing docs</button>
            <button class="button warning" data-action="hold" type="button">Hold</button>
            <button class="button warning" data-action="objection" type="button">Objection</button>
            <button class="button danger" data-action="reject" type="button">Reject</button>
            <button class="button" data-action="certificate" type="button">Certificate</button>
          </div>
        </div>
        <h3>Documents</h3>
        <div class="document-chips">${docs.length ? docs.map((doc) => `<span class="document-chip">${escapeHtml(labelize(doc.document_type))}: ${escapeHtml(labelize(doc.status))}</span>`).join("") : `<span class="muted">No documents</span>`}</div>
        <h3>Notes</h3>
        <ul class="timeline">${notes.length ? notes.map((note) => `<li>${escapeHtml(note.note || note)}</li>`).join("") : `<li>No notes</li>`}</ul>
      `,
    });

    modal.root.addEventListener("click", async (event) => {
      const transitionButton = event.target.closest("[data-transition-app]");
      const action = event.target.closest("[data-action]")?.dataset.action;
      if (transitionButton) {
        const { transitionApp, transitionStatus } = transitionButton.dataset;
        await runAction(() => applicationsApi.transition(transitionApp, transitionStatus), modal, `Moved to ${labelize(transitionStatus)}`);
      }
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
    modal?.close();
    await renderApplications(root);
  } catch (error) {
    reportError(error);
  }
}
