import { applicationsApi } from "../api/applicationsApi.js";
import { renderTable } from "../components/table.js";
import { reportError } from "../components/notifications.js";
import { groupBy, statusPill, escapeHtml, formatDate } from "../core/utils.js";
import { state } from "../core/state.js";

export async function renderDashboard(container) {
  container.innerHTML = `<div class="empty-state">Loading operational dashboard...</div>`;
  try {
    state.applications = await applicationsApi.list({ limit: 100, sort_field: "timestamps.submitted_at", sort_order: -1 });
  } catch (error) {
    reportError(error);
  }

  const apps = state.applications || [];
  const byStatus = groupBy(apps, (app) => app.status);
  const pending = apps.filter((app) => !["approved", "certificate_issued", "closed", "rejected"].includes(app.status)).length;
  const recent = apps.slice(0, 6);

  container.innerHTML = `
    <section class="kpi-grid">
      <div class="kpi"><span>Total applications</span><strong>${apps.length}</strong></div>
      <div class="kpi"><span>Pending workload</span><strong>${pending}</strong></div>
      <div class="kpi"><span>Approved</span><strong>${byStatus.approved?.length || 0}</strong></div>
      <div class="kpi"><span>Certificates issued</span><strong>${byStatus.certificate_issued?.length || 0}</strong></div>
    </section>

    <section class="module-strip">
      <article class="module-card"><h3>Land applications</h3><p>Create applications, inspect details, transition statuses, add notes, hold, reject, and issue certificates.</p></article>
      <article class="module-card"><h3>Applicant portal</h3><p>Create applicant profiles, fetch applicant details, and review applications tied to an applicant ID.</p></article>
      <article class="module-card"><h3>Survey assignment</h3><p>Create staff records, auto-assign surveyors, advance milestones, upload reports, and record registrar review.</p></article>
      <article class="module-card"><h3>Analytics and maps</h3><p>Visualize application mix, status distribution, zones, and parcel references from available application data.</p></article>
    </section>

    <section class="page-section">
      <div class="section-header">
        <div><h2>Recent applications</h2><p>Latest records returned by the backend application list endpoint.</p></div>
        <a class="button secondary" href="#applications">Open applications</a>
      </div>
      <div class="section-body">
        ${renderTable({
          rows: recent,
          empty: "No applications available yet.",
          columns: [
            { label: "Application", render: (row) => `<strong>${escapeHtml(row.application_id)}</strong>` },
            { label: "Type", render: (row) => escapeHtml(row.application_type?.replaceAll("_", " ")) },
            { label: "Status", render: (row) => statusPill(row.status) },
            { label: "Applicant", render: (row) => escapeHtml(row.applicant_ref?.applicant_id) },
            { label: "Updated", render: (row) => escapeHtml(formatDate(row.timestamps?.updated_at)) },
          ],
        })}
      </div>
    </section>
  `;
}
