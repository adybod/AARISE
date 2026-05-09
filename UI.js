(() => {
  const featureSections = [
    {
      title: "AI-powered college planning",
      description: "Turn uncertainty into a clear weekly plan tailored to your goals, grade level, and dream universities.",
      points: ["Smart timeline guidance", "Actionable weekly steps", "Clarity on what matters most"],
    },
    {
      title: "Academic & extracurricular tracking",
      description: "Keep academics, activities, and leadership growth organized in one clean workspace designed for momentum.",
      points: ["Course and GPA tracking", "Activity impact notes", "Consistency over time"],
    },
    {
      title: "Personalized student roadmaps",
      description: "Follow a long-term roadmap that adapts to your strengths, priorities, and target regions.",
      points: ["Grade-by-grade milestones", "Country-specific guidance", "Flexible and personalized"],
    },
  ];

  const state = { user: null, profile: { grade: "", targets: "", goal: "" }, activities: [] };

  async function api(path, options = {}) {
    const response = await fetch(path, {
      credentials: "include",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "request_failed");
    return data;
  }

  function renderFeatureSection(feature, index) {
    const reverse = index % 2 ? "reverse" : "";
    const items = feature.points.map((p) => `<li>${p}</li>`).join("");
    return `<section class="feature-row reveal ${reverse}"><div class="feature-copy"><p class="feature-kicker">Feature ${index + 1}</p><h3>${feature.title}</h3><p class="feature-description">${feature.description}</p><ul>${items}</ul></div><div class="feature-visual"><div class="mockup-card"></div></div></section>`;
  }

  function renderApp() {
    const loggedIn = Boolean(state.user);
    document.body.innerHTML = `
      <header class="site-header"><nav class="navbar"><a class="logo" href="/"><span class="logo-mark">A</span><span class="logo-text">AARISE</span></a><div class="nav-links"><a href="#about">About Us</a><a href="#pricing">Pricing</a>${loggedIn ? `<button class="cta-btn nav-btn" id="logoutBtn">Log Out</button>` : `<a class="cta-btn nav-btn" href="/public/auth/role.html">Login / Sign Up</a>`}</div></nav></header>
      <main>
        <section class="hero" id="about"><p class="hero-kicker">Built for ambitious students worldwide</p><h1>Tired of overpriced college counseling?</h1><p class="hero-subheading">AARISE helps students organize achievements, track academic growth, receive AI-powered college guidance, and build stronger university applications without expensive private counselors.</p><div class="hero-actions">${loggedIn ? `<button class="btn-primary" id="openDashboardBtn">Open Dashboard</button>` : `<a class="btn-primary" href="/public/auth/role.html">Get Started</a>`}<a class="btn-secondary" href="#featureShowcase">Learn More</a></div></section>
        <section class="feature-intro reveal" id="featureShowcase"><h2>A calm, focused system for long-term growth</h2><p>Everything is designed to feel clear, motivating, and structured so students can make meaningful progress.</p></section>
        ${featureSections.map(renderFeatureSection).join("")}
        <section class="pricing reveal" id="pricing"><div class="pricing-card"><h2>Accessible by design</h2><p>Built to be more affordable and available than traditional private counseling while still deeply personalized.</p></div></section>
        <section class="dashboard ${loggedIn ? "" : "hidden"}" id="dashboard"><div class="feature-intro"><h2>Your student workspace</h2><p>Saved in your account and synced across devices.</p></div><div class="dashboard-grid"><article class="panel"><h3>Profile</h3><form id="profileForm" class="stack-form"><label>Full Name<input name="name" type="text" value="${state.user?.name || ""}" disabled /></label><label>Role<input name="role" type="text" value="${state.user?.role || ""}" disabled /></label><label>Grade / Year<input name="grade" type="text" value="${state.profile.grade || ""}" /></label><label>Target Universities<input name="targets" type="text" value="${state.profile.targets || ""}" /></label><label>Primary Goal<textarea name="goal" rows="4">${state.profile.goal || ""}</textarea></label><button type="submit" class="btn-primary full-width">Save Profile</button></form><p id="profileMessage" class="success-message"></p></article><article class="panel"><h3>Achievements</h3><form id="activityForm" class="stack-form"><label>New Achievement<input name="achievement" type="text" placeholder="Add one achievement or activity" /></label><button type="submit" class="btn-secondary full-width">Add Achievement</button></form><ul class="activity-list">${state.activities.map((a) => `<li>${a.content}</li>`).join("")}</ul></article></div></section>
      </main>
    `;
    wireEvents();
    setupRevealAnimations();
  }

  function wireEvents() {
    document.getElementById("openDashboardBtn")?.addEventListener("click", () => document.getElementById("dashboard")?.scrollIntoView({ behavior: "smooth" }));
    document.getElementById("logoutBtn")?.addEventListener("click", async () => {
      await api("/api/auth/logout", { method: "POST" });
      window.location.reload();
    });
    document.getElementById("profileForm")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      await api("/api/me/profile", { method: "PUT", body: JSON.stringify({ grade: (form.get("grade") || "").toString().trim(), targets: (form.get("targets") || "").toString().trim(), goal: (form.get("goal") || "").toString().trim() }) });
      document.getElementById("profileMessage").textContent = "Profile saved.";
    });
    document.getElementById("activityForm")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const input = event.currentTarget.querySelector('input[name="achievement"]');
      const content = input.value.trim();
      if (!content) return;
      await api("/api/me/activities", { method: "POST", body: JSON.stringify({ content }) });
      input.value = "";
      await hydrateUserData();
      renderApp();
    });
  }

  function setupRevealAnimations() {
    const revealEls = document.querySelectorAll(".reveal");
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });
    revealEls.forEach((el) => observer.observe(el));
  }

  async function hydrateSession() {
    const result = await api("/api/auth/session");
    state.user = result.user;
  }

  async function hydrateUserData() {
    if (!state.user) return;
    state.profile = await api("/api/me/profile");
    const activities = await api("/api/me/activities");
    state.activities = activities.items || [];
  }

  const style = document.createElement("style");
  style.textContent = `
    :root { --bg:#f7f6f3; --surface:#fff; --text:#1f1f1f; --text-soft:#4f4f4f; --line:#e7e4dc; --shadow:0 16px 40px rgba(20,20,20,.06); --radius:18px; }
    * { box-sizing:border-box; } html { scroll-behavior:smooth; } body { margin:0; background:radial-gradient(900px 420px at 50% -180px,#ece8dd,transparent 75%),var(--bg); color:var(--text); font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
    .hidden{display:none!important;} .site-header{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(247,246,243,.84);backdrop-filter:blur(10px);}
    .navbar{max-width:1120px;margin:0 auto;min-height:74px;padding:0 1.2rem;display:flex;align-items:center;justify-content:space-between;}
    .logo{display:flex;align-items:center;gap:.55rem;color:var(--text);text-decoration:none;font-weight:700;letter-spacing:-.01em;}
    .logo-mark{width:32px;height:32px;border-radius:10px;display:grid;place-items:center;background:#111;color:#fff;font-size:.88rem;}
    .nav-links{display:flex;align-items:center;gap:.4rem;} .nav-links a,.nav-btn{text-decoration:none;border:0;background:transparent;color:#2b2b2b;border-radius:999px;padding:.55rem .9rem;font-size:.94rem;cursor:pointer;transition:background-color .2s ease,transform .2s ease;}
    .nav-links a:hover,.nav-btn:hover{background:#ece8df;transform:translateY(-1px);} .nav-links .cta-btn{background:#151515;color:#fff;padding:.58rem 1rem;}
    main{padding-top:82px;} .hero{max-width:980px;margin:0 auto;padding:4.8rem 1.2rem 4rem;text-align:center;}
    .hero-kicker{margin:0;font-weight:600;color:#666;font-size:.95rem;} .hero h1{margin:.95rem auto 0;font-size:clamp(2.35rem,7vw,5rem);line-height:1.02;letter-spacing:-.04em;max-width:860px;}
    .hero-subheading{margin:1.2rem auto 0;max-width:760px;color:var(--text-soft);font-size:clamp(1rem,2.4vw,1.22rem);line-height:1.65;}
    .hero-actions{margin-top:1.8rem;display:flex;justify-content:center;gap:.65rem;flex-wrap:wrap;}
    .btn-primary,.btn-secondary{border-radius:12px;padding:.72rem 1.15rem;font-size:.95rem;text-decoration:none;border:1px solid transparent;cursor:pointer;}
    .btn-primary{background:#111;color:#fff;} .btn-secondary{background:#fff;color:#2f2f2f;border-color:#dfdbd2;}
    .feature-intro{max-width:850px;margin:0 auto;padding:2.5rem 1.2rem 1.1rem;text-align:center;} .feature-intro h2{margin:0;font-size:clamp(1.7rem,4vw,2.5rem);}
    .feature-intro p{margin:.9rem auto 0;max-width:710px;color:var(--text-soft);line-height:1.65;}
    .feature-row{max-width:1120px;margin:0 auto;padding:2.5rem 1.2rem;display:grid;grid-template-columns:1fr 1fr;gap:1.8rem;align-items:center;}
    .feature-row.reverse .feature-copy{order:2;} .feature-row.reverse .feature-visual{order:1;} .feature-kicker{margin:0;color:#777;font-size:.85rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}
    .feature-copy h3{margin:.7rem 0 0;font-size:clamp(1.4rem,3.6vw,2.1rem);} .feature-description{margin:.8rem 0 0;color:var(--text-soft);line-height:1.68;}
    .feature-copy ul{margin:1rem 0 0;padding-left:1.1rem;color:#505050;line-height:1.8;} .mockup-card{border-radius:var(--radius);background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow);min-height:220px;}
    .pricing{max-width:1120px;margin:0 auto;padding:2rem 1.2rem 1rem;} .pricing-card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:1.3rem;text-align:center;}
    .dashboard{max-width:1120px;margin:0 auto;padding:2.5rem 1.2rem 4rem;} .dashboard-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;}
    .panel{background:#fff;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:1rem;} .panel h3{margin:0;font-size:1.05rem;}
    .stack-form{display:grid;gap:.75rem;margin-top:.8rem;} .stack-form label{display:grid;gap:.36rem;color:#3d3d3d;font-size:.91rem;}
    input,textarea{border:1px solid #ddd8ce;border-radius:11px;padding:.7rem .75rem;font:inherit;background:#fff;color:#1f1f1f;} .full-width{width:100%;}
    .activity-list{margin:.8rem 0 0;padding-left:1.1rem;color:#555;line-height:1.62;} .success-message{color:#2f6a30;font-size:.9rem;min-height:1.1rem;}
    .reveal{opacity:0;transform:translateY(20px);transition:opacity .55s ease,transform .55s ease;} .reveal.is-visible{opacity:1;transform:translateY(0);}
    @media (max-width:900px){.feature-row{grid-template-columns:1fr;gap:1rem;padding:2rem 1.2rem;}.feature-row.reverse .feature-copy,.feature-row.reverse .feature-visual{order:initial;}}
    @media (max-width:760px){.navbar{min-height:66px;padding:0 .8rem;}.logo-text{display:none;}.nav-links a,.nav-btn{font-size:.86rem;padding:.48rem .65rem;}.hero{padding:4rem .9rem 3rem;}}
  `;
  document.head.appendChild(style);

  (async () => {
    try {
      await hydrateSession();
      await hydrateUserData();
    } catch (_e) {}
    renderApp();
  })();
})();
