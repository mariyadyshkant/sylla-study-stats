async function loadCourses() {
  const res = await fetch('/api/v1/courses');
  const courses = await res.json();
  const el = document.getElementById('courses');
  el.innerHTML = courses
    .map(
      (c) => `
      <div class="course-card">
        <div>${c.name}${c.teacher ? ' — ' + c.teacher : ''}</div>
        <div class="hours">${(c.studied_minutes_total / 60).toFixed(1)} h studiate</div>
      </div>`
    )
    .join('');
}

async function loadWeekly() {
  const res = await fetch('/api/v1/stats/weekly');
  const rows = await res.json();
  const tbody = document.querySelector('#weekly tbody');
  tbody.innerHTML = rows
    .map((r) => `<tr><td>${r.week_start}</td><td>${r.course_name}</td><td>${r.studied_minutes}</td></tr>`)
    .join('');
}

loadCourses();
loadWeekly();
