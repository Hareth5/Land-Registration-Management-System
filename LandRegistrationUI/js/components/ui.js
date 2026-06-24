window.UI = {
  showMessage: function (id, message, type) {
    const box = document.getElementById(id);
    if (!box) return;
    box.className = `message-box ${type}`;
    box.textContent = message;
  },

  clearMessage: function (id) {
    const box = document.getElementById(id);
    if (!box) return;
    box.className = "message-box";
    box.textContent = "";
  },

  parseCommaList: function (value) {
    return value
      .split(",")
      .map(item => item.trim())
      .filter(item => item.length > 0);
  },

  parseJsonObject: function (value) {
    if (!value || !value.trim()) return {};
    return JSON.parse(value);
  },

  showStaffProfile: function (staff) {
    const box = document.getElementById("staffProfile");
    if (!box) return;

    box.style.display = "block";
    document.getElementById("profileName").textContent = staff.name || "-";
    document.getElementById("profileCode").textContent = staff.staff_code || "-";
    document.getElementById("profileRole").textContent = staff.role || "-";
    document.getElementById("profileDepartment").textContent = staff.department || "-";
    document.getElementById("profileEmail").textContent = staff.contacts && staff.contacts.email ? staff.contacts.email : "-";
    document.getElementById("profilePhone").textContent = staff.contacts && staff.contacts.phone ? staff.contacts.phone : "-";
    document.getElementById("profileSkills").textContent = Array.isArray(staff.skills) ? staff.skills.join(", ") : "-";
    document.getElementById("profileZones").textContent = staff.coverage && Array.isArray(staff.coverage.zone_ids) ? staff.coverage.zone_ids.join(", ") : "-";
    document.getElementById("profileWorkload").textContent = staff.workload ? `${staff.workload.active_tasks} / ${staff.workload.max_tasks}` : "-";
    document.getElementById("profileActive").textContent = staff.active ? "Active" : "Inactive";
  }
};
