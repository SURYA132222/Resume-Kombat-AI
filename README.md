# ⚔ Resume Kombat AI

> **AI-Powered Resume Battle Platform** — Where Resumes Fight for the Job.

An immersive, esports-style hiring intelligence platform that pits two resumes against each other in a 6-round AI battle, generating explainable scores, live commentary, radar analytics, ATS breakdowns, and recruiter-grade recommendations.

---

## 🎮 Live Demo

Open `index.html` in any browser. No build step. No server required.

---

## 📁 Project Structure

```
resume-kombat/
├── index.html          ← Landing page
├── battle.html         ← Upload & battle arena
├── tournament.html     ← 4/8/16-fighter knockouts
├── analytics.html      ← Deep charts & intelligence
├── about.html          ← How it works, FAQ, roadmap
├── 404.html            ← Error page
├── css/
│   ├── main.css        ← Full design system + all components
│   └── animations.css  ← Keyframes & motion effects
└── js/
    └── main.js         ← Battle engine, AI API, state management
```

---

## ⚡ Features

### Battle Arena
- **6 Rounds**: Skills Clash → Experience Duel → Project Warfare → Education Arena → Certification Strike → ATS Showdown
- **Health Bars**: Real-time HP reduction as rounds are won
- **AI Commentary**: Claude generates vivid, context-aware game-style commentary per round
- **Special Attacks**: Detects elite skill combos (Cloud Strike, Full Stack Fury, AI Combo, Backend Blitz, etc.)
- **Countdown Intro**: Animated 3-2-1-FIGHT! sequence

### Upload Modes
| Mode | Description |
|------|-------------|
| Standard Battle | Upload 2 resumes, get full battle |
| JD Matching | Add a job description for keyword + semantic match % |
| GitHub Battle | Enter two GitHub usernames for profile comparison |

### Analytics Dashboard
- Radar chart comparison (6 dimensions)
- ATS score breakdown by category
- Skill overlap Venn diagram
- Keyword density map
- Career timeline visualization
- JD match percentage (if JD provided)

### Tournament Mode
- **4, 8, or 16 fighters** supported
- AI-powered knockout bracket
- Round-by-round results with commentary
- Champion crowned with full reasoning

---

## 🤖 AI Integration

Uses the **Anthropic Claude API** (`claude-sonnet-4-20250514`) directly from the browser.

**What AI generates:**
- Round-by-round scores (0–100) with reasoning
- Dynamic battle commentary
- Special attack combo detection
- Recruiter hire/no-hire recommendation
- Risk analysis
- Per-candidate improvement plans
- Radar chart data (6 axes)
- ATS scores
- JD match percentages

**Prompt structure:**
```
System context → Resume A text → Resume B text → [Optional JD] → JSON schema
```

Returns structured JSON parsed directly into the UI.

---

## 🏗 Architecture

```
Browser
  ↓ FileReader API (PDF/DOCX/TXT)
  ↓ Text extraction
  ↓ Anthropic Claude API (/v1/messages)
  ↓ JSON response parsing
  ↓ Battle state machine
  ↓ SVG/CSS animated render
```

**No backend required** for the current version. All processing is client-side except the Claude API call.

---

## 📊 Scoring System

| Round | Category | Weight | What's Evaluated |
|-------|----------|--------|-----------------|
| R1 | Skills Clash | **25%** | Stack depth, breadth, modernity |
| R2 | Experience Duel | **25%** | YOE, seniority, impact, scale |
| R3 | Project Warfare | **20%** | Portfolio, real usage, complexity |
| R4 | Education Arena | **10%** | Degree, institution, GPA |
| R5 | Certification Strike | **10%** | Certs, recency, prestige |
| R6 | ATS Showdown | **10%** | Keywords, structure, parsability |

---

## ⚡ Special Attack Combos

| Combo | Required Skills |
|-------|----------------|
| ☁ Cloud Strike | AWS + Kubernetes + Terraform |
| 🔥 Full Stack Fury | React + Node + MongoDB/PostgreSQL |
| 🧠 AI Combo | Python + TensorFlow + PyTorch |
| ⚙ Backend Blitz | Python + Django + PostgreSQL + Docker |
| 🛡 Data Fortress | Spark + Kafka + BigQuery + Airflow |
| 🚀 DevOps Storm | K8s + Terraform + GitHub Actions + ArgoCD |

---

## 🎨 Design System

**Theme:** Original Futuristic Cyber Arena (no copyrighted IP)

| Token | Value |
|-------|-------|
| `--neon-cyan` | `#00f5ff` |
| `--neon-magenta` | `#ff00ff` |
| `--neon-yellow` | `#ffff00` |
| `--neon-orange` | `#ff6600` |
| `--neon-green` | `#00ff88` |
| `--bg-void` | `#020408` |
| `--font-head` | Orbitron |
| `--font-body` | Rajdhani |
| `--font-mono` | Share Tech Mono |

---

## 🚀 Getting Started

### Option 1: Just open in browser
```bash
# Clone or download
open index.html
# or
python3 -m http.server 8080
# → http://localhost:8080
```

### Option 2: VS Code Live Server
1. Install **Live Server** extension
2. Right-click `index.html` → Open with Live Server

### Option 3: Any static host
Upload all files as-is to Netlify, Vercel, GitHub Pages, or any CDN.

---

## 🔧 Configuration

The Claude API key is handled by the Anthropic platform in the claude.ai environment. For self-hosting:

1. Create a proxy server that adds your API key header
2. Or use environment variables via a lightweight backend (see planned backend below)

> ⚠️ **Never expose API keys in client-side JS for production.**

---

## 🗺 Planned Backend (FastAPI)

```
backend/
├── main.py               ← FastAPI app entry
├── routers/
│   ├── battles.py        ← POST /battles
│   ├── resumes.py        ← POST /resumes/upload
│   ├── tournaments.py    ← POST /tournaments
│   └── analytics.py     ← GET /analytics/{battle_id}
├── services/
│   ├── parser.py         ← pdfplumber + python-docx + spaCy
│   ├── ai_engine.py      ← Claude API integration
│   ├── scorer.py         ← Weighted scoring logic
│   └── commentary.py     ← Commentary generation
├── models/
│   ├── battle.py         ← Pydantic schemas
│   └── resume.py
├── db/
│   ├── schema.sql        ← PostgreSQL tables
│   └── connection.py
└── Dockerfile
```

**Planned API endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/battles` | Create new battle |
| `GET`  | `/battles/{id}` | Get battle results |
| `POST` | `/resumes/upload` | Upload and parse resume |
| `GET`  | `/resumes/{id}` | Get parsed resume data |
| `POST` | `/tournaments` | Create tournament |
| `GET`  | `/tournaments/{id}` | Get bracket |
| `GET`  | `/analytics/{battle_id}` | Deep analytics |

---

## 🗄 Planned Database Schema

```sql
-- battles
CREATE TABLE battles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_a_id UUID REFERENCES resumes(id),
  resume_b_id UUID REFERENCES resumes(id),
  jd_id UUID REFERENCES job_descriptions(id),
  winner CHAR(1) CHECK (winner IN ('A','B')),
  total_score_a INT,
  total_score_b INT,
  battle_data JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- resumes
CREATE TABLE resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  filename TEXT,
  raw_text TEXT,
  parsed_data JSONB,
  skills TEXT[],
  ats_score INT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- scores
CREATE TABLE scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  battle_id UUID REFERENCES battles(id),
  round_id INT,
  round_name TEXT,
  score_a INT,
  score_b INT,
  winner CHAR(1),
  commentary TEXT
);

-- job_descriptions
CREATE TABLE job_descriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT,
  raw_text TEXT,
  required_skills TEXT[],
  created_at TIMESTAMP DEFAULT NOW()
);

-- tournaments
CREATE TABLE tournaments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  size INT CHECK (size IN (4,8,16)),
  bracket_data JSONB,
  champion TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔒 Security Notes

- All file reading is client-side via FileReader API
- Resume text is **not stored** in the browser-only version
- Only a text slice (max ~2000 chars per resume) is sent to Claude API
- Planned backend will add: rate limiting, input sanitization, file validation, secure upload to S3/GCS

---

## 🗺 Roadmap

- [x] Battle Arena (6 rounds, HP bars, commentary)
- [x] Analytics Dashboard (radar, ATS, keywords, timeline)
- [x] Tournament Mode (4/8/16 fighters)
- [x] JD Matching Mode
- [x] GitHub Battle Mode (UI ready)
- [x] Special Attack Combos
- [ ] FastAPI backend + PostgreSQL
- [ ] PDF parsing (pdfplumber)
- [ ] Audio engine (Howler.js — original sounds)
- [ ] LinkedIn Comparison Mode
- [ ] User accounts + battle history
- [ ] Shareable battle links
- [ ] Team hiring mode

---

## 📄 License

Original work. All theme assets, code, and design are original IP.  
No copyrighted characters, names, music, voices, or assets from any game franchise.

---

## 🙌 Built With

- [Anthropic Claude](https://anthropic.com) — AI analysis engine
- [Orbitron](https://fonts.google.com/specimen/Orbitron) — Display font
- [Rajdhani](https://fonts.google.com/specimen/Rajdhani) — Body font
- Vanilla HTML/CSS/JS — Zero build dependencies
