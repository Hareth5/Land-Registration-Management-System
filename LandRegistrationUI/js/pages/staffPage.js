document.addEventListener("DOMContentLoaded", function () {
  renderLayout("staff");

  const createForm = document.getElementById("createStaffForm");
  const getForm = document.getElementById("getStaffForm");

  createForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    UI.clearMessage("message");

    const payload = {
      staff_code: document.getElementById("staffCode").value.trim(),
      name: document.getElementById("name").value.trim(),
      role: document.getElementById("role").value,
      department: document.getElementById("department").value.trim(),
      skills: UI.parseCommaList(document.getElementById("skills").value),
      contacts: {
        phone: document.getElementById("phone").value.trim(),
        email: document.getElementById("email").value.trim()
      },
      coverage: {
        zone_ids: UI.parseCommaList(document.getElementById("zones").value)
      },
      workload: {
        active_tasks: Number(document.getElementById("activeTasks").value || 0),
        max_tasks: Number(document.getElementById("maxTasks").value || 10)
      },
      active: document.getElementById("active").checked
    };

    try {
      const result = await StaffApi.createStaff(payload);
      const staffId = result && result.staff_id ? ` Staff ID: ${result.staff_id}.` : "";
      UI.showMessage("message", `Staff member created successfully.${staffId}`, "success");
      createForm.reset();
      document.getElementById("active").checked = true;
      document.getElementById("activeTasks").value = 0;
      document.getElementById("maxTasks").value = 10;
    } catch (error) {
      UI.showMessage("message", error.message, "error");
    }
  });

  getForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    UI.clearMessage("message");

    const staffId = document.getElementById("staffId").value.trim();

    try {
      const staff = await StaffApi.getStaffById(staffId);
      UI.showMessage("message", "Staff profile loaded successfully.", "success");
      UI.showStaffProfile(staff);
    } catch (error) {
      UI.showMessage("message", error.message, "error");
    }
  });
});
