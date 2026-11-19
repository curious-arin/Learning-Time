// Change this if your FastAPI server runs on a different address.
const API_BASE = "http://127.0.0.1:8000";
const PAGE_SIZE = 8;

const rows = document.getElementById("studentRows");
const dialog = document.getElementById("studentDialog");
const form = document.getElementById("studentForm");
const notice = document.getElementById("notice");
let students = [];
let page = 1;
let editingId = null;

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) }
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail;
    throw new Error(Array.isArray(detail) ? detail.map(x => x.msg).join(", ") : detail || "Request failed");
  }
  return body;
}

function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  })[char]);
}
function grade(marks) {
  if (marks >= 90) return "A+";
  if (marks >= 80) return "A";
  if (marks >= 70) return "B";
  if (marks >= 60) return "C";
  return "F";
}
function showNotice(message, isError = false) {
  notice.textContent = message;
  notice.style.color = isError ? "#c03939" : "#3155c5";
}
function refreshStats(list) {
  document.getElementById("totalCount").textContent = list.length;
  const average = list.length ? list.reduce((sum, s) => sum + Number(s.marks), 0) / list.length : 0;
  document.getElementById("averageMarks").textContent = list.length ? `${average.toFixed(1)}%` : "—";
  document.getElementById("courseCount").textContent = new Set(list.map(s => s.course)).size;
}
function updateCourseOptions() {
  const select = document.getElementById("courseFilter");
  const current = select.value;
  const courses = [...new Set(students.map(s => s.course))].sort();
  select.innerHTML = '<option value="">All courses</option>' + courses.map(c => `<option value="${escapeHTML(c)}">${escapeHTML(c)}</option>`).join("");
  select.value = courses.includes(current) ? current : "";
}
function render() {
  const search = document.getElementById("searchInput").value.trim().toLowerCase();
  const course = document.getElementById("courseFilter").value.toLowerCase();
  const sortBy = document.getElementById("sortBy").value;
  const order = document.getElementById("sortOrder").value;
  let list = students.filter(s =>
    (`${s.name} ${s.id}`).toLowerCase().includes(search) &&
    (!course || s.course.toLowerCase() === course)
  );
  if (sortBy) list.sort((a,b) => {
    const result = typeof a[sortBy] === "string"
      ? a[sortBy].localeCompare(b[sortBy])
      : Number(a[sortBy]) - Number(b[sortBy]);
    return order === "desc" ? -result : result;
  });
  refreshStats(students);
  const pages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
  page = Math.min(page, pages);
  const visible = list.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  rows.innerHTML = visible.length ? visible.map(s => `
    <tr>
      <td><span class="student-name">${escapeHTML(s.name)}</span><span class="subtle">${escapeHTML(s.email)}</span></td>
      <td>${escapeHTML(s.id)}</td><td>${escapeHTML(s.course)}</td><td>${escapeHTML(s.age)}</td>
      <td>${escapeHTML(s.marks)} / 100</td><td><span class="grade">${grade(Number(s.marks))}</span></td>
      <td class="actions"><button data-edit="${escapeHTML(s.id)}">Edit</button><button class="delete" data-delete="${escapeHTML(s.id)}">Delete</button></td>
    </tr>`).join("") : '<tr><td colspan="7" class="empty">No students found.</td></tr>';
  document.getElementById("pageInfo").textContent = `Page ${page} of ${pages} · ${list.length} result(s)`;
  document.getElementById("prevBtn").disabled = page <= 1;
  document.getElementById("nextBtn").disabled = page >= pages;
}
async function loadStudents() {
  try {
    const data = await api("/students");
    students = Object.entries(data).map(([id, s]) => ({ id, ...s }));
    updateCourseOptions();
    render();
  } catch (error) {
    rows.innerHTML = `<tr><td colspan="7" class="empty">Could not load students. ${escapeHTML(error.message)}<br>Check that FastAPI is running and CORS is enabled.</td></tr>`;
    showNotice(error.message, true);
  }
}
function openForm(student = null) {
  form.reset();
  document.getElementById("formError").textContent = "";
  editingId = student?.id ?? null;
  document.getElementById("dialogTitle").textContent = editingId ? "Edit student" : "Add student";
  document.getElementById("saveBtn").textContent = editingId ? "Save changes" : "Save student";
  for (const key of ["id","name","age","email","course","marks"]) {
    form.elements[key].value = student?.[key] ?? "";
    form.elements[key].disabled = editingId && key === "id";
  }
  dialog.showModal();
}
document.getElementById("addBtn").addEventListener("click", () => openForm());
document.getElementById("closeDialog").addEventListener("click", () => dialog.close());
document.getElementById("cancelBtn").addEventListener("click", () => dialog.close());
form.addEventListener("submit", async event => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  payload.age = Number(payload.age);
  payload.marks = Number(payload.marks);
  try {
    if (editingId) {
      delete payload.id;
      await api(`/students/${encodeURIComponent(editingId)}`, { method: "PUT", body: JSON.stringify(payload) });
      showNotice("Student updated successfully.");
    } else {
      await api("/create", { method: "POST", body: JSON.stringify(payload) });
      showNotice("Student created successfully.");
    }
    dialog.close();
    await loadStudents();
  } catch (error) {
    document.getElementById("formError").textContent = error.message;
  }
});
rows.addEventListener("click", async event => {
  const editId = event.target.dataset.edit;
  const deleteId = event.target.dataset.delete;
  if (editId) {
    const student = students.find(s => s.id === editId);
    if (student) openForm(student);
  }
  if (deleteId && confirm(`Delete student ${deleteId}? This cannot be undone.`)) {
    try {
      await api(`/delete/${encodeURIComponent(deleteId)}`, { method: "DELETE" });
      showNotice("Student deleted successfully.");
      await loadStudents();
    } catch (error) { showNotice(error.message, true); }
  }
});
["searchInput","courseFilter","sortBy","sortOrder"].forEach(id => {
  document.getElementById(id).addEventListener(id === "searchInput" ? "input" : "change", () => { page = 1; render(); });
});
document.getElementById("prevBtn").addEventListener("click", () => { page--; render(); });
document.getElementById("nextBtn").addEventListener("click", () => { page++; render(); });
loadStudents();
