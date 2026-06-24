import { applicationsApi } from "../api/applicationsApi.js";
import { renderTable } from "../components/table.js";
import { reportError } from "../components/notifications.js";
import { groupBy, statusPill, escapeHtml } from "../core/utils.js";
import { state } from "../core/state.js";

export async function renderDashboard(container) {
  container.innerHTML = `<div class="empty-state">Loading...</div>`;
  try {
    state.applications = await applicationsApi.list({ limit: 100 });
  } catch (error) {
    reportError(error);
  }

  const apps = state.applications || [];
  const byStatus = groupBy(apps, (app) => app.status);
  const pending = apps.filter((app) => !["approved", "certificate_issued", "closed", "rejected"].includes(app.status)).length;
  const recent = apps.slice(0, 6);

  container.innerHTML = `
    <section class="kpi-grid">
      <div class="kpi"><span>Applications</span><strong>${apps.length}</strong></div>
      <div class="kpi"><span>Pending</span><strong>${pending}</strong></div>
      <div class="kpi"><span>Approved</span><strong>${byStatus.approved?.length || 0}</strong></div>
      <div class="kpi"><span>Certificates</span><strong>${byStatus.certificate_issued?.length || 0}</strong></div>
    </section>

    <section class="module-strip">
      <article class="module-card"><h3>Applications</h3><p>Registration cases and certificates.</p></article>
      <article class="module-card"><h3>Applicants</h3><p>Citizen and representative profiles.</p></article>
      <article class="module-card"><h3>Survey</h3><p>Surveyors, reports, and registrar review.</p></article>
      <article class="module-card"><h3>Maps</h3><p>Zones and application locations.</p></article>
    </section>

    <section class="page-section">
      <div class="section-header">
        <div><h2>Recent applications</h2></div>
        <a class="button secondary" href="#applications">Open</a>
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
          ],
        })}
      </div>
    </section>
  `;
}
