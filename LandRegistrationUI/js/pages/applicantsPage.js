import { applicantsApi } from "../api/applicantsApi.js";
import { APPLICANT_TYPES } from "../core/constants.js";
import { qs, serializeForm, escapeHtml, formatDate, labelize } from "../core/utils.js";
import { field, formShell } from "../components/forms.js";
import { renderTable } from "../components/table.js";
import { notify, reportError } from "../components/notifications.js";
import { statusPill } from "../core/utils.js";

export function renderApplicants(container) {
  container.innerHTML = `
    <section class="page-grid">
      <article class="page-section span-7">
        <div class="section-header"><div><h2>Create applicant</h2><p>Matches POST /applicants/ request model.</p></div></div>
        <div class="section-body">
          ${formShell("createApplicantForm", [
            field({ label: "Full name", name: "full_name", required: true }),
            field({ label: "Applicant type", name: "applicant_type", options: APPLICANT_TYPES, required: true }),
            field({ label: "National ID", name: "national_id", required: true }),
            field({ label: "Email", name: "email", type: "email", required: true }),
            field({ label: "Phone", name: "phone", required: true }),
            field({ label: "City", name: "city", required: true }),
            field({ label: "Street", name: "street" }),
            field({ label: "Preferred contact", name: "preferred_contact", options: ["email", "phone"], required: true }),
            field({ label: "Language", name: "language", value: "ar" }),
          ], "Create applicant")}
        </div>
      </article>
      <article class="page-section span-5">
        <div class="section-header"><div><h2>Applicant lookup</h2><p>Fetch profile and linked applications by Mongo ObjectId.</p></div></div>
        <div class="section-body">
          <form id="lookupApplicantForm" class="form-grid">
            ${field({ label: "Applicant ID", name: "applicant_id", full: true, required: true })}
            <div class="form-field full"><button class="button" type="submit">Load applicant</button></div>
          </form>
        </div>
      </article>
    </section>
    <section class="page-section" id="applicantResult"></section>
  `;

  qs("#createApplicantForm", container).addEventListener("submit", createApplicant);
  qs("#lookupApplicantForm", container).addEventListener("submit", lookupApplicant);
}

async function createApplicant(event) {
  event.preventDefault();
  const raw = serializeForm(event.currentTarget);
  const payload = {
    full_name: raw.full_name,
    applicant_type: raw.applicant_type,
    identity: { national_id: raw.national_id },
    contacts: { email: raw.email, phone: raw.phone },
    address: { city: raw.city, street: raw.street || null },
    preferences: {
      preferred_contact: raw.preferred_contact,
      language: raw.language || "ar",
      notifications: {
        on_status_change: true,
        on_missing_documents: true,
        on_certificate_ready: true,
      },
    },
  };
  try {
    const result = await applicantsApi.create(payload);
    notify("Applicant created");
    renderApplicantResult(result.applicant, null);
    event.currentTarget.reset();
  } catch (error) {
    reportError(error);
  }
}

async function lookupApplicant(event) {
  event.preventDefault();
  const { applicant_id } = serializeForm(event.currentTarget);
  try {
    const [profile, applications] = await Promise.all([
      applicantsApi.get(applicant_id),
      applicantsApi.applications(applicant_id),
    ]);
    renderApplicantResult(profile, applications);
  } catch (error) {
    reportError(error);
  }
}

function renderApplicantResult(profile, applications) {
  const target = qs("#applicantResult");
  const rows = applications?.applications || [];
  target.innerHTML = `
    <div class="section-header">
      <div><h2>${escapeHtml(profile.full_name)}</h2><p>${escapeHtml(labelize(profile.applicant_type))} - ${escapeHtml(profile.id)}</p></div>
      <span class="status-pill info">${escapeHtml(profile.identity?.verified ? "verified" : "not verified")}</span>
    </div>
    <div class="section-body">
      <dl class="detail-list">
        <div><dt>Email</dt><dd>${escapeHtml(profile.contacts?.email)}</dd></div>
        <div><dt>Phone</dt><dd>${escapeHtml(profile.contacts?.phone)}</dd></div>
        <div><dt>Address</dt><dd>${escapeHtml([profile.address?.city, profile.address?.street].filter(Boolean).join(", "))}</dd></div>
        <div><dt>Created</dt><dd>${escapeHtml(formatDate(profile.created_at))}</dd></div>
      </dl>
    </div>
    <div class="section-body">
      ${renderTable({
        rows,
        empty: "No linked applications were returned for this applicant.",
        columns: [
          { label: "Application", render: (row) => escapeHtml(row.application_id) },
          { label: "Type", render: (row) => escapeHtml(labelize(row.application_type)) },
          { label: "Status", render: (row) => statusPill(row.status) },
          { label: "Zone", render: (row) => escapeHtml(row.parcel_ref?.zone_id || "Not set") },
          { label: "Updated", render: (row) => escapeHtml(formatDate(row.updated_at)) },
        ],
      })}
    </div>
  `;
}
