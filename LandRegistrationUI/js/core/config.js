export const API_CONFIG = {
  BASE_URL:
    globalThis.LRMIS_API_BASE_URL ||
    `${window.location.protocol}//${window.location.hostname}:8000`,
  TIMEOUT_MS: 15000,
};

export const ROUTES = [
  { id: "dashboard", label: "Dashboard", icon: "DB", title: "Dashboard" },
  { id: "applications", label: "Applications", icon: "AP", title: "Applications" },
  { id: "applicants", label: "Applicants", icon: "PR", title: "Applicants" },
  { id: "staff", label: "Staff", icon: "ST", title: "Staff" },
  { id: "assignments", label: "Assignments", icon: "AS", title: "Assignments" },
  { id: "analytics", label: "Analytics", icon: "AN", title: "Analytics" },
  { id: "maps", label: "Maps", icon: "MP", title: "Maps" },
];
