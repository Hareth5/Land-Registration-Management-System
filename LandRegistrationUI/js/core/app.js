import { API_CONFIG, ROUTES } from "./config.js";
import { qs } from "./utils.js";
import { renderNav } from "../components/navigation.js";
import { renderDashboard } from "../pages/dashboardPage.js";
import { renderApplications } from "../pages/applicationsPage.js";
import { renderApplicants } from "../pages/applicantsPage.js";
import { renderStaff } from "../pages/staffPage.js";
import { renderAssignments } from "../pages/assignmentsPage.js";
import { renderAnalytics } from "../pages/analyticsPage.js";
import { renderMaps } from "../pages/mapsPage.js";

const pages = {
  dashboard: renderDashboard,
  applications: renderApplications,
  applicants: renderApplicants,
  staff: renderStaff,
  assignments: renderAssignments,
  analytics: renderAnalytics,
  maps: renderMaps,
};

function currentRoute() {
  const hash = location.hash.replace("#", "");
  return pages[hash] ? hash : "dashboard";
}

async function renderRoute() {
  const routeId = currentRoute();
  const route = ROUTES.find((item) => item.id === routeId);
  qs("#pageTitle").textContent = route?.title || "Dashboard";
  qs("#apiStatus").textContent = `API: ${API_CONFIG.BASE_URL}`;
  renderNav(routeId);
  document.body.classList.remove("nav-open");
  await pages[routeId](qs("#app"));
  qs("#app").focus();
}

qs("#menuToggle").addEventListener("click", () => document.body.classList.toggle("nav-open"));
window.addEventListener("hashchange", renderRoute);

if (!location.hash) {
  location.hash = "#dashboard";
} else {
  renderRoute();
}
