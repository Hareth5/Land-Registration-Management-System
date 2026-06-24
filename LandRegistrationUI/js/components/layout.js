window.renderLayout = function (activePage) {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;

  const inPagesFolder = window.location.pathname.includes("/pages/");
  const base = inPagesFolder ? "../" : "";

  const links = [
    { key: "home", text: "Dashboard", href: `${base}test.html` },
    { key: "staff", text: "Staff Management", href: `${base}pages/staff.html` },
    { key: "auto", text: "Auto Assignment", href: `${base}pages/auto-assignment.html` },
    { key: "milestone", text: "Survey Milestone", href: `${base}pages/survey-task.html` },
    { key: "report", text: "Survey Report", href: `${base}pages/survey-report.html` },
    { key: "review", text: "Registrar Review", href: `${base}pages/registrar-review.html` }
  ];

  sidebar.innerHTML = `
    <div class="sidebar-title">LRMIS<br>Survey Module</div>
    <nav class="sidebar-nav">
      ${links.map(link => `<a class="${link.key === activePage ? "active" : ""}" href="${link.href}">${link.text}</a>`).join("")}
    </nav>
  `;
};
