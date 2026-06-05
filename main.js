/* =============================================
   RESUME KOMBAT AI — MAIN JS
   ============================================= */

// ---- CURSOR GLOW ----
const cursorGlow = document.getElementById('cursorGlow');
if (cursorGlow) {
  document.addEventListener('mousemove', e => {
    cursorGlow.style.left = e.clientX + 'px';
    cursorGlow.style.top = e.clientY + 'px';
  });
}

// ---- NAVBAR SCROLL ----
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  });
}

// ---- NAV BURGER ----
const burger = document.getElementById('navBurger');
const mobileNav = document.getElementById('navMobile');
if (burger && mobileNav) {
  burger.addEventListener('click', () => {
    mobileNav.classList.toggle('open');
  });
}

// ---- SCROLL REVEAL ----
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 80);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.step-card, .feat-card-sm, .feat-big, .dash-card, .improve-card').forEach(el => {
  el.classList.add('reveal');
  revealObserver.observe(el);
});

// ---- HERO PARTICLES ----
function spawnParticles() {
  const container = document.getElementById('heroParticles');
  if (!container) return;
  const colors = ['#00f5ff', '#ff00ff', '#ffff00', '#00ff88', '#ff6600'];
  for (let i = 0; i < 40; i++) {
    const p = document.createElement('div');
    const size = Math.random() * 3 + 1;
    const color = colors[Math.floor(Math.random() * colors.length)];
    p.style.cssText = `
      position:absolute;
      width:${size}px;height:${size}px;
      border-radius:50%;
      background:${color};
      opacity:${Math.random() * 0.4 + 0.1};
      left:${Math.random() * 100}%;
      top:${Math.random() * 100}%;
      animation: particleFloat ${4 + Math.random() * 6}s ease-in-out ${Math.random() * 4}s infinite alternate;
      box-shadow: 0 0 ${size * 2}px ${color};
    `;
    container.appendChild(p);
  }
}

// Add particle CSS
const particleStyle = document.createElement('style');
particleStyle.textContent = `
@keyframes particleFloat {
  from { transform: translate(0, 0); opacity: 0.1; }
  to { transform: translate(${Math.random() > 0.5 ? '' : '-'}${20 + Math.random() * 40}px, -${20 + Math.random() * 60}px); opacity: 0.5; }
}`;
document.head.appendChild(particleStyle);
spawnParticles();

// ---- SHARED STATE ----
window.RK = {
  textA: '', textB: '', jd: '',
  nameA: 'CANDIDATE A', nameB: 'CANDIDATE B',
  hpA: 100, hpB: 100,
  battleData: null,
  fileLoadedA: false, fileLoadedB: false
};

// ---- FILE UPLOAD HANDLING ----
function initFileUploads() {
  const zoneA = document.getElementById('zone-a');
  const zoneB = document.getElementById('zone-b');
  if (!zoneA) return;

  setupZone(zoneA, 'a');
  setupZone(zoneB, 'b');
}

function setupZone(zone, side) {
  if (!zone) return;
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) processUploadedFile(file, side);
  });
}

function handleFileInput(e, side) {
  const file = e.target.files[0];
  if (file) processUploadedFile(file, side);
}

function processUploadedFile(file, side) {
  const reader = new FileReader();
  reader.onload = ev => {
    const text = ev.target.result;
    const displayName = file.name.replace(/\.[^.]+$/, '').toUpperCase().slice(0, 22) || `CANDIDATE ${side.toUpperCase()}`;
    if (side === 'a') {
      window.RK.textA = text;
      window.RK.nameA = displayName;
      window.RK.fileLoadedA = true;
    } else {
      window.RK.textB = text;
      window.RK.nameB = displayName;
      window.RK.fileLoadedB = true;
    }
    const nameEl = document.getElementById(`file-name-${side}`);
    if (nameEl) nameEl.textContent = '✓ ' + file.name;
    const zone = document.getElementById(`zone-${side}`);
    if (zone) zone.classList.add('loaded');
    checkFightReady();
  };
  reader.readAsText(file);
}

function checkFightReady() {
  const btn = document.getElementById('fight-btn');
  if (btn) btn.disabled = !(window.RK.fileLoadedA && window.RK.fileLoadedB);
}

// ---- DEMO DATA ----
function loadDemoData() {
  window.RK.textA = `Alice Chen — Senior Software Engineer
Email: alice.chen@email.com | LinkedIn: linkedin.com/in/alicechen | GitHub: github.com/alicechen

SKILLS
Languages: Python, TypeScript, Go, Java
Frontend: React, Next.js, Vue.js
Backend: Django, FastAPI, Node.js, gRPC
Cloud: AWS (Solutions Architect Certified), GCP, Azure
Infrastructure: Docker, Kubernetes, Terraform, Helm, CI/CD
Databases: PostgreSQL, Redis, Elasticsearch, MongoDB
ML/AI: TensorFlow, PyTorch, scikit-learn, Hugging Face

EXPERIENCE
Senior Software Engineer — TechCorp Inc. (2021–2024)
  • Led migration from monolith to microservices architecture; 40% latency reduction, 60% cost savings
  • Built real-time ML pipeline processing 5M events/day using Kafka + TensorFlow
  • Mentored team of 6 engineers; instituted code review culture and pair programming
  • Reduced P99 latency from 800ms to 120ms via distributed caching strategy

Software Engineer — CloudStartup (2019–2021)
  • Designed GraphQL API serving 2M daily active users with 99.99% uptime SLA
  • Launched A/B testing platform that drove 18% conversion improvement

EDUCATION
B.S. Computer Science — MIT, GPA 3.9/4.0 (2019)
Relevant coursework: Distributed Systems, ML, Algorithms

PROJECTS
  • Open-source ML library: 1,200+ GitHub stars, used in production at 50+ companies
  • Kubernetes operator for auto-scaling: presented at KubeCon 2023
  • E-commerce platform: $2M/month GMV, React + Django + PostgreSQL + Redis

CERTIFICATIONS
  • AWS Solutions Architect Professional
  • Google Cloud Professional Data Engineer
  • CKA (Certified Kubernetes Administrator)

ACHIEVEMENTS
  • Published 3 peer-reviewed ML papers (NeurIPS, ICML)
  • USPTO Patent #10,234,567 — Distributed Cache Invalidation Protocol
  • MIT Outstanding Alumni Award 2023`;

  window.RK.textB = `Bob Martinez — Full Stack Developer
Email: bob.martinez@email.com | LinkedIn: linkedin.com/in/bobmartinez

SKILLS
Languages: JavaScript, TypeScript, Python (basic), PHP
Frontend: React, Vue.js, jQuery, HTML5, CSS3, Bootstrap
Backend: Node.js, Express, Laravel
Databases: MongoDB, MySQL, SQLite
DevOps: Docker, basic AWS (EC2/S3), GitHub Actions
Other: REST APIs, WordPress, Figma

EXPERIENCE
Full Stack Developer — WebAgency Digital (2020–2024)
  • Delivered 15+ client projects using React and Node.js
  • Built and maintained WordPress sites for 30+ SMB clients
  • Implemented payment integrations (Stripe, PayPal) for 5 e-commerce clients
  • Improved page load speed by 30% through asset optimization

Junior Developer — Freelance (2018–2020)
  • Built custom WordPress themes and plugins for local businesses
  • jQuery and PHP development for client requirements

EDUCATION
B.S. Information Technology — State University, GPA 3.2/4.0 (2018)

PROJECTS
  • Personal dev blog — 500 monthly subscribers, covers React and Node.js tutorials
  • TaskFlow SaaS — task management app, 200 active users, React + Node + MongoDB
  • Portfolio site with custom CMS built in Laravel

CERTIFICATIONS
  • Meta Frontend Developer Professional Certificate (2023)
  • freeCodeCamp JavaScript Algorithms & Data Structures

ACHIEVEMENTS
  • Employee of the Month — Q2 2023 at WebAgency
  • Positive client reviews on Clutch.co (4.8/5 average)`;

  window.RK.jd = `Senior Backend Engineer — AI/ML Platform

We are looking for a Senior Backend Engineer to build and scale our AI/ML infrastructure.

Required:
• 4+ years backend engineering experience
• Proficiency in Python and a compiled language (Go preferred)
• Cloud infrastructure (AWS or GCP, production experience)
• Container orchestration: Kubernetes required
• ML frameworks: TensorFlow or PyTorch experience
• Strong database skills: PostgreSQL, Redis
• Experience with distributed systems at scale

Nice to Have:
• Open source contributions
• Published research or patents
• Kubernetes certification (CKA)
• Experience with MLOps pipelines

About the role: You will design ML infrastructure serving millions of users, mentor junior engineers, and collaborate closely with research teams.`;

  window.RK.nameA = 'ALICE CHEN';
  window.RK.nameB = 'BOB MARTINEZ';
  window.RK.fileLoadedA = true;
  window.RK.fileLoadedB = true;

  const nameA = document.getElementById('file-name-a');
  const nameB = document.getElementById('file-name-b');
  const jdEl = document.getElementById('jd-text');
  const zA = document.getElementById('zone-a');
  const zB = document.getElementById('zone-b');

  if (nameA) nameA.textContent = '✓ alice_chen_resume.txt (demo)';
  if (nameB) nameB.textContent = '✓ bob_martinez_resume.txt (demo)';
  if (jdEl) jdEl.value = window.RK.jd;
  if (zA) zA.classList.add('loaded');
  if (zB) zB.classList.add('loaded');

  checkFightReady();
}

// ---- BATTLE INITIATION ----
async function startBattle() {
  const jdEl = document.getElementById('jd-text');
  if (jdEl) window.RK.jd = jdEl.value;

  const nameA = document.getElementById('cd-name-a');
  const nameB = document.getElementById('cd-name-b');
  if (nameA) nameA.textContent = window.RK.nameA;
  if (nameB) nameB.textContent = window.RK.nameB;

  // Show countdown
  const cd = document.getElementById('countdown-overlay');
  if (cd) cd.classList.add('active');

  await runCountdown();
  if (cd) cd.classList.remove('active');

  // Show loading
  const ld = document.getElementById('loading-overlay');
  if (ld) ld.classList.add('active');

  await runAI();
  if (ld) ld.classList.remove('active');

  buildArena();
  const arena = document.getElementById('arena-overlay');
  if (arena) arena.classList.add('active');
  document.body.style.overflow = 'hidden';

  await animateRounds();
}

async function runCountdown() {
  const disp = document.getElementById('cd-num');
  if (!disp) return;
  const steps = [
    { t: '3', c: 'c-cyan' },
    { t: '2', c: 'c-magenta' },
    { t: '1', c: 'c-yellow' },
    { t: 'FIGHT!', c: 'c-fight' }
  ];
  for (const s of steps) {
    disp.textContent = s.t;
    disp.className = 'cd-num pulse-in ' + s.c;
    await sleep(850);
  }
}

async function runAI() {
  const stepEl = document.getElementById('loading-step');
  const steps = [
    'Parsing resume structure...',
    'Extracting skills & experience...',
    'Running semantic analysis...',
    'Computing ATS scores...',
    'Detecting special attack combos...',
    'Generating battle commentary...',
    'Calculating round winners...'
  ];
  for (const s of steps) {
    if (stepEl) stepEl.textContent = s;
    await sleep(380);
  }

  const hasJD = window.RK.jd.trim().length > 30;

  const prompt = `You are Resume Kombat AI. Analyze these two resumes for an epic hiring battle and return ONLY valid JSON — no markdown, no preamble.

Resume A (${window.RK.nameA}):
${window.RK.textA.slice(0, 2000)}

Resume B (${window.RK.nameB}):
${window.RK.textB.slice(0, 2000)}

${hasJD ? `Job Description:\n${window.RK.jd.slice(0, 600)}` : ''}

Return this JSON with real analysis (all scores 0-100, commentary must be vivid game-style language):
{
  "nameA": "${window.RK.nameA}",
  "nameB": "${window.RK.nameB}",
  "rounds": [
    {"id":1,"name":"Skills Clash","scoreA":75,"scoreB":60,"commentary":"vivid game commentary here","winner":"A"},
    {"id":2,"name":"Experience Duel","scoreA":70,"scoreB":65,"commentary":"vivid game commentary here","winner":"A"},
    {"id":3,"name":"Project Warfare","scoreA":80,"scoreB":55,"commentary":"vivid game commentary here","winner":"A"},
    {"id":4,"name":"Education Arena","scoreA":72,"scoreB":62,"commentary":"vivid game commentary here","winner":"A"},
    {"id":5,"name":"Certification Strike","scoreA":75,"scoreB":50,"commentary":"vivid game commentary here","winner":"A"},
    {"id":6,"name":"ATS Showdown","scoreA":85,"scoreB":70,"commentary":"vivid game commentary here","winner":"A"}
  ],
  "overallWinner": "A",
  "totalScoreA": 77,
  "totalScoreB": 60,
  "skillsA": ["Python","AWS","Docker"],
  "skillsB": ["JavaScript","Node.js","React"],
  "commonSkills": ["React","Docker"],
  "uniqueSkillsA": ["Python","TensorFlow","Kubernetes"],
  "uniqueSkillsB": ["Node.js","MongoDB","Laravel"],
  "missingSkillsA": [],
  "missingSkillsB": ["Python","Cloud","ML"],
  "specialAttackA": {"triggered": true, "name": "Cloud Strike", "skills": ["AWS","Kubernetes","Terraform"]},
  "specialAttackB": {"triggered": false, "name": "", "skills": []},
  "recruiterRecommendation": "2-3 sentence recommendation",
  "riskAnalysis": "1-2 sentence risk analysis",
  "improvementsA": ["tip1","tip2","tip3"],
  "improvementsB": ["tip1","tip2","tip3"],
  "radarA": {"skills":85,"experience":78,"projects":88,"education":82,"certifications":76,"ats":88},
  "radarB": {"skills":65,"experience":70,"projects":58,"education":68,"certifications":55,"ats":72},
  "atsScoreA": 88,
  "atsScoreB": 72,
  "jdMatchA": ${hasJD ? 85 : -1},
  "jdMatchB": ${hasJD ? 42 : -1}
}`;

  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    const data = await res.json();
    let raw = data.content.filter(b => b.type === 'text').map(b => b.text).join('');
    raw = raw.replace(/```json|```/g, '').trim();
    const firstBrace = raw.indexOf('{');
    const lastBrace = raw.lastIndexOf('}');
    if (firstBrace !== -1 && lastBrace !== -1) {
      raw = raw.slice(firstBrace, lastBrace + 1);
    }
    window.RK.battleData = JSON.parse(raw);
  } catch (e) {
    console.warn('Using fallback data', e);
    window.RK.battleData = buildFallback();
  }
}

function buildFallback() {
  const rounds = [
    { id: 1, name: 'Skills Clash', scoreA: 88, scoreB: 62, commentary: 'Candidate A unleashes a devastating tech stack combo — cloud computing uppercut followed by an ML finishing blow!', winner: 'A' },
    { id: 2, name: 'Experience Duel', scoreA: 82, scoreB: 71, commentary: 'Both fighters trade blows, but Candidate A\'s enterprise-scale impact deals critical damage!', winner: 'A' },
    { id: 3, name: 'Project Warfare', scoreA: 90, scoreB: 56, commentary: 'Candidate A deploys open-source weapons with 1,200 stars — an absolutely devastating assault!', winner: 'A' },
    { id: 4, name: 'Education Arena', scoreA: 82, scoreB: 68, commentary: 'Candidate A\'s prestigious institution lands a solid foundation strike!', winner: 'A' },
    { id: 5, name: 'Certification Strike', scoreA: 78, scoreB: 52, commentary: 'Triple cert combo hits — AWS Professional + GCP + CKA! Candidate B staggers!', winner: 'A' },
    { id: 6, name: 'ATS Showdown', scoreA: 91, scoreB: 74, commentary: 'Candidate A\'s keyword-optimized resume blazes through every ATS filter with a perfect sweep!', winner: 'A' }
  ];
  return {
    nameA: window.RK.nameA, nameB: window.RK.nameB,
    rounds, overallWinner: 'A', totalScoreA: 85, totalScoreB: 64,
    skillsA: ['Python', 'AWS', 'Docker', 'TensorFlow', 'Kubernetes', 'React'],
    skillsB: ['JavaScript', 'Node.js', 'React', 'MongoDB', 'Express'],
    commonSkills: ['React', 'Docker', 'TypeScript'],
    uniqueSkillsA: ['Python', 'TensorFlow', 'Kubernetes', 'AWS', 'Go'],
    uniqueSkillsB: ['Node.js', 'MongoDB', 'Laravel', 'PHP'],
    missingSkillsA: [], missingSkillsB: ['Python', 'Cloud Platform', 'ML Frameworks', 'Kubernetes'],
    specialAttackA: { triggered: true, name: 'Cloud Strike', skills: ['AWS', 'Kubernetes', 'Terraform'] },
    specialAttackB: { triggered: false, name: '', skills: [] },
    recruiterRecommendation: `${window.RK.nameA} is the clearly stronger candidate for a senior engineering role, demonstrating deep expertise in cloud infrastructure, ML systems, and production-scale architecture. Recommend proceeding to technical interview immediately.`,
    riskAnalysis: 'Low risk hire — verifiable open-source contributions, published research, and enterprise-scale impact reduce uncertainty significantly.',
    improvementsA: ['Highlight leadership metrics more prominently', 'Add estimated dollar impact of cost savings', 'Consider a personal website / portfolio site link'],
    improvementsB: ['Learn Python and at minimum one cloud platform — essential for modern roles', 'Build a project with real traffic (10k+ users) to demonstrate scale', 'Pursue AWS or GCP certification to validate cloud knowledge'],
    radarA: { skills: 88, experience: 82, projects: 90, education: 82, certifications: 78, ats: 91 },
    radarB: { skills: 62, experience: 71, projects: 56, education: 68, certifications: 52, ats: 74 },
    atsScoreA: 91, atsScoreB: 74, jdMatchA: -1, jdMatchB: -1
  };
}

// ---- BUILD ARENA ----
function buildArena() {
  const d = window.RK.battleData;
  window.RK.hpA = 100; window.RK.hpB = 100;

  // Set names
  setTextSafe('arena-name-a', d.nameA);
  setTextSafe('arena-name-b', d.nameB);
  updateHP();

  const container = document.getElementById('rounds-container');
  if (!container) return;
  container.innerHTML = '';

  d.rounds.forEach((r, i) => {
    const specialA = d.specialAttackA?.triggered && r.winner === 'A';
    const specialB = d.specialAttackB?.triggered && r.winner === 'B';
    const specialHtml = (specialA
      ? `<div class="special-banner"><span class="special-label">⚡ SPECIAL ATTACK</span><span class="special-name">${d.specialAttackA.name} — ${d.specialAttackA.skills.join(' + ')}</span></div>`
      : '') + (specialB
      ? `<div class="special-banner"><span class="special-label">⚡ SPECIAL ATTACK</span><span class="special-name">${d.specialAttackB.name} — ${d.specialAttackB.skills.join(' + ')}</span></div>`
      : '');

    const div = document.createElement('div');
    div.className = 'round-card';
    div.id = `rc-${i}`;
    div.innerHTML = `
      <div class="round-card-head">
        <span class="rc-num">ROUND ${r.id}</span>
        <span class="rc-name">${r.name}</span>
        <span class="rc-result" id="rcr-${i}" style="display:none"></span>
      </div>
      <div class="round-card-body" id="rcb-${i}" style="display:none">
        ${specialHtml}
        <div class="score-row">
          <div class="sc-val sc-val-a" id="sca-${i}">—</div>
          <div class="sc-sep">VS</div>
          <div class="sc-val sc-val-b" id="scb-${i}">—</div>
        </div>
        <div class="score-bar" id="sb-${i}">
          <div class="sb-a" id="sba-${i}" style="width:0"></div>
          <div class="sb-b" id="sbb-${i}" style="width:0"></div>
        </div>
        <div class="round-commentary">${r.commentary}</div>
      </div>`;
    container.appendChild(div);
  });
}

async function animateRounds() {
  const d = window.RK.battleData;
  for (let i = 0; i < d.rounds.length; i++) {
    const r = d.rounds[i];
    const card = document.getElementById(`rc-${i}`);
    const body = document.getElementById(`rcb-${i}`);
    const resultEl = document.getElementById(`rcr-${i}`);

    setTextSafe('arena-round-label', `ROUND ${r.id} / 6`);
    setTextSafe('arena-round-name', r.name);

    if (card) card.classList.add('is-active');
    if (body) body.style.display = 'block';
    await sleep(600);

    setTextSafe(`sca-${i}`, r.scoreA);
    setTextSafe(`scb-${i}`, r.scoreB);

    const total = (r.scoreA + r.scoreB) || 1;
    const elA = document.getElementById(`sba-${i}`);
    const elB = document.getElementById(`sbb-${i}`);
    if (elA) elA.style.width = (r.scoreA / total * 50) + '%';
    if (elB) elB.style.width = (r.scoreB / total * 50) + '%';

    await sleep(1000);

    if (resultEl) {
      resultEl.style.display = 'inline-block';
      if (r.winner === 'A') {
        resultEl.className = 'rc-result res-a';
        resultEl.textContent = (d.nameA.split(' ')[0] || 'A') + ' WINS';
        if (card) card.classList.add('won-a');
        window.RK.hpB = Math.max(0, window.RK.hpB - (Math.floor(Math.random() * 8) + 10));
      } else if (r.winner === 'B') {
        resultEl.className = 'rc-result res-b';
        resultEl.textContent = (d.nameB.split(' ')[0] || 'B') + ' WINS';
        if (card) card.classList.add('won-b');
        window.RK.hpA = Math.max(0, window.RK.hpA - (Math.floor(Math.random() * 8) + 10));
      } else {
        resultEl.className = 'rc-result res-tie';
        resultEl.textContent = 'DRAW';
      }
    }

    if (card) card.classList.remove('is-active');
    updateHP();
    await sleep(600);
  }

  setTextSafe('arena-round-label', 'BATTLE COMPLETE');
  setTextSafe('arena-round-name', `${d.overallWinner === 'A' ? d.nameA : d.nameB} IS VICTORIOUS!`);

  const nextBtn = document.getElementById('arena-results-btn');
  if (nextBtn) nextBtn.style.display = 'block';
}

function updateHP() {
  const a = window.RK.hpA, b = window.RK.hpB;
  const hpA = document.getElementById('hp-fill-a');
  const hpB = document.getElementById('hp-fill-b');
  const vA = document.getElementById('hp-val-a');
  const vB = document.getElementById('hp-val-b');
  if (hpA) { hpA.style.width = a + '%'; if (a < 30) hpA.classList.add('low'); }
  if (hpB) { hpB.style.width = b + '%'; if (b < 30) hpB.classList.add('low'); }
  if (vA) vA.textContent = a + ' HP';
  if (vB) vB.textContent = b + ' HP';
}

function closeArena() {
  const arena = document.getElementById('arena-overlay');
  if (arena) arena.classList.remove('active');
  document.body.style.overflow = '';
}

function showDashboard() {
  closeArena();
  buildDashboard();
  const dash = document.getElementById('dashboard-section');
  if (dash) {
    dash.style.display = 'block';
    dash.scrollIntoView({ behavior: 'smooth' });
  }
}

// ---- DASHBOARD ----
function buildDashboard() {
  const d = window.RK.battleData;
  if (!d) return;
  const container = document.getElementById('dashboard-content');
  if (!container) return;

  const wins = d.overallWinner === 'A';
  const winName = wins ? d.nameA : d.nameB;
  const winScore = wins ? d.totalScoreA : d.totalScoreB;
  const loseScore = wins ? d.totalScoreB : d.totalScoreA;

  const jdSection = d.jdMatchA >= 0 ? `
    <div class="dash-card">
      <div class="dash-card-title">Job Description Match</div>
      <div class="analysis-bar">
        <div class="ab-header"><span class="ab-label">${d.nameA}</span><div class="ab-vals"><span class="ab-val-a">${d.jdMatchA}%</span></div></div>
        <div class="ab-track"><div class="ab-fill-a" style="width:${d.jdMatchA}%"></div></div>
      </div>
      <div class="analysis-bar" style="margin-top:10px">
        <div class="ab-header"><span class="ab-label">${d.nameB}</span><div class="ab-vals"><span class="ab-val-b">${d.jdMatchB}%</span></div></div>
        <div class="ab-track" style="justify-content:flex-end"><div class="ab-fill-b" style="width:${d.jdMatchB}%"></div></div>
      </div>
    </div>` : '';

  container.innerHTML = `
    <div class="dash-winner ${wins ? 'w-a' : 'w-b'}">
      <div class="dw-label">🏆 AI VERDICT — WINNER</div>
      <div class="dw-name ${wins ? 'c-cyan' : 'c-mag'}">${winName}</div>
      <div class="dw-score">Final Score: ${winScore} vs ${loseScore}</div>
    </div>

    <div class="dash-grid">
      <div class="dash-card">
        <div class="dash-card-title">Round Scores</div>
        ${d.rounds.map(r => `
          <div class="metric-row">
            <span class="metric-name">${r.name}</span>
            <div class="metric-vals">
              <span class="mv-a">${r.scoreA}</span>
              <span class="mv-b">${r.scoreB}</span>
            </div>
          </div>`).join('')}
      </div>

      <div class="dash-card">
        <div class="dash-card-title">Radar Analysis</div>
        ${buildRadar(d)}
        <div style="display:flex;gap:16px;margin-top:10px;font-family:var(--font-mono);font-size:11px">
          <span style="color:var(--neon-cyan)">■ ${d.nameA.split(' ')[0]}</span>
          <span style="color:var(--neon-magenta)">■ ${d.nameB.split(' ')[0]}</span>
        </div>
      </div>

      <div class="dash-card">
        <div class="dash-card-title">ATS Performance</div>
        <div class="analysis-bar">
          <div class="ab-header"><span class="ab-label">${d.nameA}</span><div class="ab-vals"><span class="ab-val-a">${d.atsScoreA}</span></div></div>
          <div class="ab-track"><div class="ab-fill-a" style="width:${d.atsScoreA}%"></div></div>
        </div>
        <div class="analysis-bar" style="margin-top:12px">
          <div class="ab-header"><span class="ab-label">${d.nameB}</span><div class="ab-vals"><span class="ab-val-b">${d.atsScoreB}</span></div></div>
          <div class="ab-track"><div class="ab-fill-b" style="width:${d.atsScoreB}%"></div></div>
        </div>
      </div>

      ${jdSection}

      <div class="dash-card">
        <div class="dash-card-title">Common Skills</div>
        <div class="tag-cloud">${(d.commonSkills || []).map(s => `<span class="tc-tag tc-common">${s}</span>`).join('')}</div>
      </div>

      <div class="dash-card">
        <div class="dash-card-title">Unique — ${d.nameA}</div>
        <div class="tag-cloud">${(d.uniqueSkillsA || []).map(s => `<span class="tc-tag tc-a">${s}</span>`).join('')}</div>
      </div>

      <div class="dash-card">
        <div class="dash-card-title">Unique — ${d.nameB}</div>
        <div class="tag-cloud">${(d.uniqueSkillsB || []).map(s => `<span class="tc-tag tc-b">${s}</span>`).join('')}</div>
      </div>
    </div>

    <div class="rec-box">
      <div class="rec-title">⚡ RECRUITER RECOMMENDATION</div>
      <div class="rec-text">${d.recruiterRecommendation}</div>
      ${d.riskAnalysis ? `<div class="rec-text" style="margin-top:12px;font-size:13px;color:var(--text-muted)">Risk Analysis: ${d.riskAnalysis}</div>` : ''}
    </div>

    <div style="font-family:var(--font-head);font-size:10px;letter-spacing:3px;color:var(--neon-orange);margin-bottom:16px">⚡ POWER-UP PLANS</div>
    <div class="improve-grid">
      <div class="improve-card">
        <div class="improve-who iw-a">${d.nameA} — IMPROVEMENTS</div>
        <ul class="improve-list">${(d.improvementsA || []).map(t => `<li>${t}</li>`).join('')}</ul>
      </div>
      <div class="improve-card">
        <div class="improve-who iw-b">${d.nameB} — IMPROVEMENTS</div>
        <ul class="improve-list">${(d.improvementsB || []).map(t => `<li>${t}</li>`).join('')}</ul>
      </div>
    </div>
  `;
}

function buildRadar(d) {
  const cats = ['skills', 'experience', 'projects', 'education', 'certifications', 'ats'];
  const labels = ['Skills', 'Exp', 'Projects', 'Edu', 'Certs', 'ATS'];
  const cx = 130, cy = 120, r = 90;
  const angles = cats.map((_, i) => ((i * 60 - 90) * Math.PI / 180));
  const pt = (val, angle) => {
    const rv = val / 100 * r;
    return [cx + rv * Math.cos(angle), cy + rv * Math.sin(angle)];
  };
  const polyA = cats.map((c, i) => pt(d.radarA[c] || 0, angles[i]).join(',')).join(' ');
  const polyB = cats.map((c, i) => pt(d.radarB[c] || 0, angles[i]).join(',')).join(' ');
  const grids = [20, 40, 60, 80, 100].map(v => {
    const pts = angles.map(a => pt(v, a).join(',')).join(' ');
    return `<polygon points="${pts}" fill="none" stroke="rgba(0,245,255,0.07)" stroke-width="1"/>`;
  }).join('');
  const axes = angles.map(a =>
    `<line x1="${cx}" y1="${cy}" x2="${cx + r * Math.cos(a)}" y2="${cy + r * Math.sin(a)}" stroke="rgba(0,245,255,0.1)" stroke-width="1"/>`
  ).join('');
  const lbls = angles.map((a, i) => {
    const lx = cx + (r + 18) * Math.cos(a);
    const ly = cy + (r + 18) * Math.sin(a);
    return `<text x="${lx}" y="${ly}" text-anchor="middle" dominant-baseline="middle" fill="#445566" font-family="Orbitron,monospace" font-size="8" letter-spacing="0.5">${labels[i]}</text>`;
  }).join('');
  return `<svg viewBox="0 0 260 240" style="width:100%;height:auto">
    ${grids}${axes}
    <polygon points="${polyA}" fill="rgba(0,245,255,0.12)" stroke="#00f5ff" stroke-width="1.5"/>
    <polygon points="${polyB}" fill="rgba(255,0,255,0.12)" stroke="#ff00ff" stroke-width="1.5"/>
    ${lbls}
    <circle cx="${cx}" cy="${cy}" r="2" fill="rgba(0,245,255,0.4)"/>
  </svg>`;
}

// ---- TOURNAMENT ----
function initTournament() {
  const sizeButtons = document.querySelectorAll('.size-btn');
  sizeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      sizeButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const size = parseInt(btn.dataset.size);
      buildTournamentSlots(size);
    });
  });
}

function buildTournamentSlots(count) {
  const grid = document.getElementById('t-upload-grid');
  if (!grid) return;
  grid.innerHTML = '';
  for (let i = 1; i <= count; i++) {
    const slot = document.createElement('div');
    slot.className = 't-slot';
    slot.id = `t-slot-${i}`;
    slot.innerHTML = `
      <input type="file" accept=".pdf,.docx,.txt" onchange="fillTSlot(event,${i})">
      <div class="t-slot-num">FIGHTER ${i}</div>
      <div class="t-slot-icon">+</div>
      <div class="t-slot-name" id="tsn-${i}"></div>`;
    grid.appendChild(slot);
  }
}

function fillTSlot(e, idx) {
  const file = e.target.files[0];
  if (!file) return;
  const slot = document.getElementById(`t-slot-${idx}`);
  const nameEl = document.getElementById(`tsn-${idx}`);
  if (slot) slot.classList.add('filled');
  if (nameEl) nameEl.textContent = file.name.replace(/\.[^.]+$/, '').slice(0, 18);
}

// ---- UTIL ----
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function setTextSafe(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
  initFileUploads();
  initTournament();

  // Set active nav link based on current page
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === path ||
        (path === '' || path === 'index.html') && link.getAttribute('href') === 'index.html') {
      link.classList.add('active');
    }
  });
});