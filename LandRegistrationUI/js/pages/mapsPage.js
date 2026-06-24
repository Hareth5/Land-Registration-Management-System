import { applicationsApi } from "../api/applicationsApi.js";
import { reportError } from "../components/notifications.js";
import { escapeHtml, groupBy, labelize, statusPill } from "../core/utils.js";

const BASE_POINTS = [
  [31.9038, 35.2034],
  [31.5326, 35.0998],
  [32.2211, 35.2544],
  [31.7054, 35.2024],
  [32.4594, 35.3009],
  [31.4167, 34.3333],
];

export async function renderMaps(container) {
  container.innerHTML = `<div class="empty-state">Loading map data...</div>`;
  let applications = [];
  try {
    applications = await applicationsApi.list({ limit: 100 });
  } catch (error) {
    reportError(error);
  }

  const byZone = groupBy(applications, (app) => app.parcel_ref?.zone_id);
  const zones = Object.entries(byZone).map(([zone, rows], index) => ({
    zone,
    rows,
    point: BASE_POINTS[index % BASE_POINTS.length],
  }));

  container.innerHTML = `
    <section class="page-grid">
      <article class="page-section span-8">
        <div class="section-header"><div><h2>Application map</h2><p>OpenStreetMap + Leaflet visualization using application zone data.</p></div></div>
        <div class="section-body"><div id="lrmisMap" class="map-panel"></div></div>
      </article>
      <article class="page-section span-4">
        <div class="section-header"><div><h2>Zones</h2><p>Applications grouped by parcel_ref.zone_id.</p></div></div>
        <div class="section-body zone-list">
          ${zones.map((zone) => `<div class="zone-row"><span>${escapeHtml(zone.zone)}</span><strong>${zone.rows.length}</strong></div>`).join("") || `<div class="empty-state">No zone references found.</div>`}
        </div>
      </article>
    </section>
  `;

  drawMap(zones);
}

function drawMap(zones) {
  const map = L.map("lrmisMap").setView([31.9, 35.2], 8);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  zones.forEach((zone, index) => {
    const offset = index * 0.025;
    const marker = L.circleMarker([zone.point[0] + offset, zone.point[1] + offset], {
      radius: Math.max(9, Math.min(26, zone.rows.length * 4)),
      color: "#176b5d",
      fillColor: "#b56b2a",
      fillOpacity: 0.72,
      weight: 2,
    }).addTo(map);
    marker.bindPopup(`
      <strong>${escapeHtml(zone.zone)}</strong><br />
      ${zone.rows.length} application(s)
      <hr />
      ${zone.rows.slice(0, 6).map((app) => `${escapeHtml(app.application_id)} - ${statusPill(app.status)} - ${escapeHtml(labelize(app.application_type))}`).join("<br />")}
    `);
  });
}
