import { applicationsApi } from "../api/applicationsApi.js";
import { renderTable } from "../components/table.js";
import { reportError } from "../components/notifications.js";
import { downloadJson, escapeHtml, groupBy, labelize, statusPill } from "../core/utils.js";

export async function renderAnalytics(container) {
  container.innerHTML = `<div class="empty-state">Loading analytics...</div>`;
  let applications = [];
  try {
    applications = await applicationsApi.list({ limit: 100 });
  } catch (error) {
    reportError(error);
  }

  const byStatus = groupBy(applications, (app) => app.status);
  const byType = groupBy(applications, (app) => app.application_type);
  const byZone = groupBy(applications, (app) => app.parcel_ref?.zone_id);
  const statusRows = Object.entries(byStatus).map(([status, rows]) => ({ status, count: rows.length }));
  const typeRows = Object.entries(byType).map(([type, rows]) => ({ type, count: rows.length }));
  const zoneRows = Object.entries(byZone).map(([zone, rows]) => ({ zone, count: rows.length }));

  container.innerHTML = `
    <section class="kpi-grid">
      <div class="kpi"><span>Total records analyzed</span><strong>${applications.length}</strong></div>
      <div class="kpi"><span>Distinct statuses</span><strong>${statusRows.length}</strong></div>
      <div class="kpi"><span>Application types</span><strong>${typeRows.length}</strong></div>
      <div class="kpi"><span>Parcel zones</span><strong>${zoneRows.filter((row) => row.zone !== "unknown").length}</strong></div>
    </section>
    <section class="page-grid">
      <article class="page-section span-6">
        <div class="section-header"><div><h2>Status distribution</h2><p>Computed from GET /applications/.</p></div></div>
        <div class="section-body">${renderBarList(statusRows, "status")}</div>
      </article>
      <article class="page-section span-6">
        <div class="section-header"><div><h2>Application type mix</h2><p>Counts grouped by application_type.</p></div></div>
        <div class="section-body">${renderBarList(typeRows, "type")}</div>
      </article>
      <article class="page-section span-12">
        <div class="section-header">
          <div><h2>Zone workload</h2><p>Grouped by parcel_ref.zone_id when present in backend records.</p></div>
          <button class="button secondary" id="exportAnalytics" type="button">Export JSON</button>
        </div>
        <div class="section-body">
          ${renderTable({
            rows: zoneRows,
            empty: "No zone data is available in application parcel references.",
            columns: [
              { label: "Zone", render: (row) => escapeHtml(row.zone) },
              { label: "Applications", render: (row) => escapeHtml(row.count) },
              { label: "Share", render: (row) => `${applications.length ? Math.round((row.count / applications.length) * 100) : 0}%` },
            ],
          })}
        </div>
      </article>
    </section>
  `;
  document.querySelector("#exportAnalytics")?.addEventListener("click", () => downloadJson("lrmis-analytics.json", { statusRows, typeRows, zoneRows }));
}

function renderBarList(rows, key) {
  const total = rows.reduce((sum, row) => sum + row.count, 0) || 1;
  if (!rows.length) return `<div class="empty-state">No data available.</div>`;
  return rows
    .sort((a, b) => b.count - a.count)
    .map((row) => {
      const label = row[key];
      const percent = Math.round((row.count / total) * 100);
      return `
        <div class="zone-row">
          <span>${key === "status" ? statusPill(label) : escapeHtml(labelize(label))}</span>
          <strong>${row.count} (${percent}%)</strong>
        </div>
      `;
    })
    .join("");
}
