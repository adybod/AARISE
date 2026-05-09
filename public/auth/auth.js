(function () {
  const params = new URLSearchParams(window.location.search);
  const roleFromQuery = (params.get("role") || "").toLowerCase();
  const mode = document.body.dataset.mode;

  function googleStart(modeName, role) {
    const selectedRole = (role || "").toLowerCase();
    if (!selectedRole || !["student", "parent"].includes(selectedRole)) return;
    window.location.href = `/api/auth/google/start?mode=${encodeURIComponent(modeName)}&role=${encodeURIComponent(selectedRole)}`;
  }

  function renderRolePage() {
    const root = document.getElementById("authRoot");
    root.innerHTML = `
      <h1>Choose your role</h1>
      <p>Select how you want to continue.</p>
      <div class="role-grid">
        <a class="role-card" href="/public/auth/login.html?role=student">
          <h3>Student</h3><p>Track growth, activities, and college readiness.</p>
        </a>
        <a class="role-card" href="/public/auth/login.html?role=parent">
          <h3>Parent</h3><p>Support your student with structured guidance.</p>
        </a>
      </div>
    `;
  }

  function messageBlock() {
    const error = params.get("error");
    if (!error) return "";
    const decoded = decodeURIComponent(error);
    const link = mode === "login"
      ? `<a href="/public/auth/signup.html?role=${roleFromQuery || "student"}">Create account</a>`
      : `<a href="/public/auth/login.html?role=${roleFromQuery || "student"}">Go to login</a>`;
    return `<div class="error">${decoded}. ${link}</div>`;
  }

  function renderAuthPage(modeName) {
    const title = modeName === "login" ? "Log in to your account" : "Create your account";
    const subtitle = modeName === "login"
      ? "Only existing accounts can log in."
      : "Only new accounts can sign up.";
    const altLink = modeName === "login"
      ? `/public/auth/signup.html?role=${roleFromQuery || "student"}`
      : `/public/auth/login.html?role=${roleFromQuery || "student"}`;
    const altText = modeName === "login" ? "Need an account? Sign up" : "Already have an account? Log in";

    const root = document.getElementById("authRoot");
    root.innerHTML = `
      <h1>${title}</h1>
      <p>${subtitle}</p>
      <div class="role-pill">${(roleFromQuery || "student").toUpperCase()}</div>
      ${messageBlock()}
      <button class="google-btn" id="googleBtn">
        <span>G</span> Continue with Google
      </button>
      <a class="alt-link" href="${altLink}">${altText}</a>
      <a class="back-link" href="/public/auth/role.html">Change role</a>
    `;
    document.getElementById("googleBtn").addEventListener("click", () => googleStart(modeName, roleFromQuery));
  }

  if (mode === "role") renderRolePage();
  if (mode === "login") renderAuthPage("login");
  if (mode === "signup") renderAuthPage("signup");
})();
