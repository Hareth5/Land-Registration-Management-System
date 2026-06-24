import { assignmentsApi } from "../api/assignmentsApi.js";
import { field, formShell } from "../components/forms.js";
import { notify, reportError } from "../components/notifications.js";
import { MILESTONE_ACTORS, REGISTRAR_DECISIONS, SURVEY_MILESTONES } from "../core/constants.js";
import { qs, serializeForm } from "../core/utils.js";

export function renderAssignments(container) {
  container.innerHTML = `
    <section class="page-grid">
      <article class="page-section span-6">
        <div class="section-header"><div><h2>Auto-assign surveyor</h2><p>Requires application status survey_required and parcel_ref.zone_id.</p></div></div>
        <div class="section-body">${formShell("autoAssignForm", [field({ label: "Application ID", name: "application_id", required: true, full: true })], "Auto-assign")}</div>
      </article>
      <article class="page-section span-6">
        <div class="section-header"><div><h2>Survey milestone</h2><p>Advances the survey task in backend-defined sequence.</p></div></div>
        <div class="section-body">${formShell("milestoneForm", [
          field({ label: "Application ID", name: "application_id", required: true }),
          field({ label: "Milestone", name: "milestone_type", options: SURVEY_MILESTONES, required: true }),
          field({ label: "By", name: "by", options: MILESTONE_ACTORS, required: true }),
          field({ label: "Meta", name: "meta", placeholder: "Optional JSON", full: true }),
        ], "Add milestone")}</div>
      </article>
      <article class="page-section span-6">
        <div class="section-header"><div><h2>Survey report</h2><p>Allowed after survey_completed.</p></div></div>
        <div class="section-body">${formShell("reportForm", [
          field({ label: "Application ID", name: "application_id", required: true }),
          field({ label: "Uploaded by", name: "uploaded_by", required: true }),
          field({ label: "Report title", name: "report_title", required: true }),
          field({ label: "File name", name: "file_name", required: true }),
          field({ label: "File path", name: "file_path", required: true, full: true }),
          field({ label: "Summary", name: "summary", type: "textarea", required: true, full: true }),
        ], "Upload report")}</div>
      </article>
      <article class="page-section span-6">
        <div class="section-header"><div><h2>Registrar review</h2><p>Allowed after report_uploaded.</p></div></div>
        <div class="section-body">${formShell("reviewForm", [
          field({ label: "Application ID", name: "application_id", required: true }),
          field({ label: "Reviewed by", name: "reviewed_by", required: true }),
          field({ label: "Decision", name: "decision", options: REGISTRAR_DECISIONS, required: true }),
          field({ label: "Notes", name: "notes", type: "textarea", required: true, full: true }),
        ], "Submit review")}</div>
      </article>
    </section>
    <section class="page-section" id="assignmentResult"><div class="section-body empty-state">Workflow responses will appear here.</div></section>
  `;

  qs("#autoAssignForm", container).addEventListener("submit", handleAutoAssign);
  qs("#milestoneForm", container).addEventListener("submit", handleMilestone);
  qs("#reportForm", container).addEventListener("submit", handleReport);
  qs("#reviewForm", container).addEventListener("submit", handleReview);
}

async function handleAutoAssign(event) {
  event.preventDefault();
  const { application_id } = serializeForm(event.currentTarget);
  await showResult(() => assignmentsApi.autoAssignSurveyor(application_id), "Surveyor assigned");
}

async function handleMilestone(event) {
  event.preventDefault();
  const raw = serializeForm(event.currentTarget);
  await showResult(() => assignmentsApi.addMilestone(raw.application_id, {
    milestone_type: raw.milestone_type,
    by: raw.by,
    meta: parseMeta(raw.meta),
  }), "Milestone added");
}

async function handleReport(event) {
  event.preventDefault();
  const raw = serializeForm(event.currentTarget);
  const { application_id, ...payload } = raw;
  await showResult(() => assignmentsApi.addReport(application_id, payload), "Report uploaded");
}

async function handleReview(event) {
  event.preventDefault();
  const raw = serializeForm(event.currentTarget);
  const { application_id, ...payload } = raw;
  await showResult(() => assignmentsApi.registrarReview(application_id, payload), "Registrar review submitted");
}

function parseMeta(value) {
  if (!value) return {};
  try {
    return JSON.parse(value);
  } catch {
    return { note: value };
  }
}

async function showResult(action, message) {
  try {
    const result = await action();
    notify(message);
    qs("#assignmentResult").innerHTML = `<div class="section-header"><div><h2>${message}</h2><p>Backend response</p></div></div><div class="section-body"><pre>${JSON.stringify(result, null, 2)}</pre></div>`;
  } catch (error) {
    reportError(error);
  }
}
