export const API_CONFIG = {
  BASE_URL: "http://127.0.0.1:8000",
  TIMEOUT_MS: 15000,
};

export const ROUTES = [
  { id: "dashboard", label: "Dashboard", icon: "DB", title: "Dashboard" },
  { id: "applications", label: "Applications", icon: "AP", title: "Land Application Management" },
  { id: "applicants", label: "Applicants", icon: "PR", title: "Applicant Portal and Profiles" },
  { id: "staff", label: "Staff", icon: "ST", title: "Surveyors and Registrar" },
  { id: "assignments", label: "Assignments", icon: "AS", title: "Survey and Registrar Assignment" },
  { id: "analytics", label: "Analytics", icon: "AN", title: "Analytics and Visualization" },
  { id: "maps", label: "Maps", icon: "MP", title: "OpenStreetMap View" },
];
