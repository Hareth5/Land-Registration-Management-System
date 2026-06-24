import { ROUTES } from "../core/config.js";
import { qs } from "../core/utils.js";

export function renderNav(activeRoute) {
  qs("#mainNav").innerHTML = ROUTES.map(
    (route) => `
      <a href="#${route.id}" class="${route.id === activeRoute ? "active" : ""}">
        <span class="nav-icon">${route.icon}</span>
        <span>${route.label}</span>
      </a>
    `,
  ).join("");
}
