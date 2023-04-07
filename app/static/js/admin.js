const adminStudentForm = document.getElementById("admin-student-form");
const adminTeacherForm = document.getElementById("admin-teacher-form");
const adminGroupForm = document.getElementById("admin-group-form");
const adminStudentForGroupForm = document.getElementById(
  "admin-student-for-group-form"
);

adminTeacherForm.style.display = "none";
adminGroupForm.style.display = "none";
adminStudentForGroupForm.style.display = "none";

// Toggles for different forms on admin page

function showStudentForm() {
  adminStudentForm.style.display = "";
  adminTeacherForm.style.display = "none";
  adminGroupForm.style.display = "none";
  adminStudentForGroupForm.style.display = "none";
}

function showTeacherForm() {
  adminStudentForm.style.display = "none";
  adminTeacherForm.style.display = "";
  adminGroupForm.style.display = "none";
  adminStudentForGroupForm.style.display = "none";
}

function showGroupForm() {
  adminStudentForm.style.display = "none";
  adminTeacherForm.style.display = "none";
  adminGroupForm.style.display = "";
  adminStudentForGroupForm.style.display = "none";
}

function showStudentForGroupForm() {
  adminStudentForm.style.display = "none";
  adminTeacherForm.style.display = "none";
  adminGroupForm.style.display = "none";
  adminStudentForGroupForm.style.display = "";
}

// Fetch for form handling

const studentForm = document.getElementById("student-form");

studentForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const studentFormData = new FormData(studentForm);
  let studentEntries = [...studentFormData.entries()];
  let studentInformation = {
    studentNumber: studentEntries[0][1],
    studentFirstName: studentEntries[1][1],
    studentLastName: studentEntries[2][1],
    studentEmail: studentEntries[3][1],
    studentGroup: studentEntries[4][1],
  };
  console.log(studentFormData);
  console.log(studentInformation);
  fetch("/api/student", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(studentInformation),
  })
    .then((response) => response.json())
    .then((data) => console.log(data))
    .then(() => studentForm.reset())
    .catch((error) => {
      alert("Sommige informatie bestaat al");
    });
});

const teacherForm = document.getElementById("teacher-form");

const teacherFormData = new FormData(teacherForm);
teacherForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const teacherFormData = new FormData(teacherForm);
  let teacherEntries = [...teacherFormData.entries()];
  let teacherInformation = {};
  if (teacherEntries[3]) {
    teacherInformation = {
      teacherFirstName: teacherEntries[0][1],
      teacherLastName: teacherEntries[1][1],
      teacherEmail: teacherEntries[2][1],
      teacherAdmin: teacherEntries[3][1],
    };
  } else {
    teacherInformation = {
      teacherFirstName: teacherEntries[0][1],
      teacherLastName: teacherEntries[1][1],
      teacherEmail: teacherEntries[2][1],
    };
  }

  fetch("/api/teacher", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(teacherInformation),
  })
    .then((response) => response.json())
    .then((data) => console.log(data))
    .then(() => teacherForm.reset())
    .catch((error) => {
      alert("Sommige informatie bestaat al");
    });
});

const groupForm = document.getElementById("group-form");
const groupFormData = new FormData(groupForm);

groupForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const groupFormData = new FormData(groupForm);
  let groupEntries = [...groupFormData.entries()];
  let groupInformation = {
    groupName: groupEntries[0][1],
    groupStartDate: groupEntries[1][1],
    groupEndDate: groupEntries[2][1]
  };
  console.log(groupFormData);
  console.log(groupInformation);
  fetch("/api/group", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(groupInformation),
  })
    .then((response) => response.json())
    .then((data) => console.log(data))
    .then(() => groupForm.reset())
    .catch((error) => {
      alert("Sommige informatie bestaat al");
    });
});
