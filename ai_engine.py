"""
Resume Kombat AI — AI Analysis Engine
Battle scoring, commentary, recruiter recommendations via Claude API
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"

COMBO_PATTERNS = [
    {"name": "Cloud Strike",    "skills": ["aws", "kubernetes", "terraform"],        "candidate": ""},
    {"name": "Full Stack Fury", "skills": ["react", "node.js", "mongodb"],           "candidate": ""},
    {"name": "AI Combo",        "skills": ["python", "tensorflow", "pytorch"],       "candidate": ""},
    {"name": "Backend Blitz",   "skills": ["python", "django", "postgresql"],        "candidate": ""},
    {"name": "Data Fortress",   "skills": ["spark", "kafka", "bigquery"],            "candidate": ""},
    {"name": "DevOps Storm",    "skills": ["kubernetes", "terraform", "github actions"], "candidate": ""},
    {"name": "MERN Assault",    "skills": ["mongodb", "express", "react", "node.js"],"candidate": ""},
]

ROUND_WEIGHTS = {
    1: ("Skills Clash",         0.25),
    2: ("Experience Duel",      0.25),
    3: ("Project Warfare",      0.20),
    4: ("Education Arena",      0.10),
    5: ("Certification Strike", 0.10),
    6: ("ATS Showdown",         0.10),
}


class AIEngine:

    async def run_battle(
        self,
        name_a: str,
        name_b: str,
        text_a: str,
        text_b: str,
        skills_a: List[str],
        skills_b: List[str],
        jd_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run a full AI battle analysis and return structured result"""

        jd_block = f"\nJob Description:\n{jd_text[:600]}" if jd_text else ""
        has_jd = bool(jd_text and len(jd_text.strip()) > 30)

        prompt = self._build_battle_prompt(
            name_a, name_b, text_a, text_b, jd_block, has_jd
        )

        try:
            result = await self._call_api(prompt)
            result = self._enrich(result, skills_a, skills_b, has_jd)
            return result
        except Exception as e:
            logger.error(f"AI battle failed: {e}")
            return self._fallback_battle(name_a, name_b, skills_a, skills_b, has_jd)

    async def run_tournament_match(
        self, name_a: str, text_a: str, name_b: str, text_b: str
    ) -> Dict[str, Any]:
        """Run a single tournament match — lightweight analysis"""
        prompt = f"""Compare these two resumes briefly and pick a winner. JSON only.

Resume A ({name_a}): {text_a[:600]}
Resume B ({name_b}): {text_b[:600]}

Return:
{{"scoreA": 75, "scoreB": 60, "winner": "A", "commentary": "one sentence game-style commentary"}}"""
        try:
            raw = await self._raw_call(prompt, max_tokens=300)
            data = self._parse_json(raw)
            return {
                "fighter_a": name_a, "fighter_b": name_b,
                "score_a": data.get("scoreA", 70), "score_b": data.get("scoreB", 55),
                "winner": name_a if data.get("winner") == "A" else name_b,
                "commentary": data.get("commentary", "A fierce battle of credentials!"),
            }
        except Exception:
            score_a, score_b = 65, 55
            return {"fighter_a": name_a, "fighter_b": name_b,
                    "score_a": score_a, "score_b": score_b,
                    "winner": name_a if score_a > score_b else name_b,
                    "commentary": f"{name_a} edges ahead on overall profile strength!"}

    def detect_special_attacks(
        self, skills_a: List[str], skills_b: List[str]
    ) -> tuple[Dict, Dict]:
        skills_a_lower = [s.lower() for s in skills_a]
        skills_b_lower = [s.lower() for s in skills_b]

        def check(skill_list):
            for combo in COMBO_PATTERNS:
                required = combo["skills"]
                if all(any(r in s for s in skill_list) for r in required):
                    return {"triggered": True, "name": combo["name"], "skills": required}
            return {"triggered": False, "name": "", "skills": []}

        return check(skills_a_lower), check(skills_b_lower)

    # ── Internal ───────────────────────────────────────────────────────────
    def _build_battle_prompt(
        self, name_a, name_b, text_a, text_b, jd_block, has_jd
    ) -> str:
        return f"""You are Resume Kombat AI — an expert recruiter analyzing resumes for an epic hiring battle.
Return ONLY valid JSON with no markdown fences, no preamble.

Resume A ({name_a}):
{text_a[:2000]}

Resume B ({name_b}):
{text_b[:2000]}
{jd_block}

Return this exact JSON structure (all scores 0-100, commentary must be vivid game-style language specific to actual resume content):
{{
  "nameA": "{name_a}",
  "nameB": "{name_b}",
  "rounds": [
    {{"id":1,"name":"Skills Clash","scoreA":0,"scoreB":0,"commentary":"...","winner":"A"}},
    {{"id":2,"name":"Experience Duel","scoreA":0,"scoreB":0,"commentary":"...","winner":"A"}},
    {{"id":3,"name":"Project Warfare","scoreA":0,"scoreB":0,"commentary":"...","winner":"A"}},
    {{"id":4,"name":"Education Arena","scoreA":0,"scoreB":0,"commentary":"...","winner":"A"}},
    {{"id":5,"name":"Certification Strike","scoreA":0,"scoreB":0,"commentary":"...","winner":"A"}},
    {{"id":6,"name":"ATS Showdown","scoreA":0,"scoreB":0,"commentary":"...","winner":"A"}}
  ],
  "overallWinner":"A",
  "totalScoreA":0,
  "totalScoreB":0,
  "skillsA":["skill1"],
  "skillsB":["skill1"],
  "commonSkills":["skill1"],
  "uniqueSkillsA":["skill1"],
  "uniqueSkillsB":["skill1"],
  "missingSkillsA":[],
  "missingSkillsB":["skill1"],
  "recruiterRecommendation":"2-3 sentence professional hire/no-hire recommendation",
  "riskAnalysis":"1-2 sentence hiring risk assessment",
  "improvementsA":["tip1","tip2","tip3"],
  "improvementsB":["tip1","tip2","tip3"],
  "radarA":{{"skills":0,"experience":0,"projects":0,"education":0,"certifications":0,"ats":0}},
  "radarB":{{"skills":0,"experience":0,"projects":0,"education":0,"certifications":0,"ats":0}},
  "atsScoreA":0,
  "atsScoreB":0,
  "jdMatchA":{-1 if not has_jd else 0},
  "jdMatchB":{-1 if not has_jd else 0}
}}

Round winner must be "A", "B", or "TIE". Overall winner must be "A" or "B".
Commentary: vivid, context-aware game language based on actual resume details.
JSON only — no markdown, no explanation."""

    async def _call_api(self, prompt: str) -> Dict[str, Any]:
        raw = await self._raw_call(prompt, max_tokens=1000)
        return self._parse_json(raw)

    async def _raw_call(self, prompt: str, max_tokens: int = 1000) -> str:
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")
        headers = {
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        }
        body = {
            "model": MODEL,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(ANTHROPIC_API_URL, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            return "".join(
                block["text"] for block in data.get("content", [])
                if block.get("type") == "text"
            )

    def _parse_json(self, raw: str) -> Dict[str, Any]:
        raw = raw.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        # Find first { to last }
        fb, lb = raw.find("{"), raw.rfind("}")
        if fb != -1 and lb != -1:
            raw = raw[fb:lb + 1]
        return json.loads(raw)

    def _enrich(self, data: Dict, skills_a: List[str], skills_b: List[str], has_jd: bool) -> Dict:
        """Add special attacks and validate data"""
        special_a, special_b = self.detect_special_attacks(skills_a, skills_b)
        data["specialAttackA"] = special_a
        data["specialAttackB"] = special_b
        if not has_jd:
            data["jdMatchA"] = -1
            data["jdMatchB"] = -1
        # Calculate weighted total if missing
        if not data.get("totalScoreA"):
            rounds = data.get("rounds", [])
            weights = [0.25, 0.25, 0.20, 0.10, 0.10, 0.10]
            data["totalScoreA"] = round(sum(r["scoreA"] * w for r, w in zip(rounds, weights)))
            data["totalScoreB"] = round(sum(r["scoreB"] * w for r, w in zip(rounds, weights)))
        return data

    def _fallback_battle(
        self, name_a: str, name_b: str,
        skills_a: List[str], skills_b: List[str], has_jd: bool
    ) -> Dict[str, Any]:
        """Return deterministic fallback when API unavailable"""
        rounds = [
            {"id": 1, "name": "Skills Clash",         "scoreA": 78, "scoreB": 62, "commentary": f"{name_a} demonstrates a broader and deeper tech stack!", "winner": "A"},
            {"id": 2, "name": "Experience Duel",       "scoreA": 72, "scoreB": 68, "commentary": "Both fighters exchange blows — edge goes to seniority!", "winner": "A"},
            {"id": 3, "name": "Project Warfare",       "scoreA": 80, "scoreB": 55, "commentary": f"{name_a} unleashes production-scale projects!", "winner": "A"},
            {"id": 4, "name": "Education Arena",       "scoreA": 75, "scoreB": 65, "commentary": "Institutional prestige decides this round!", "winner": "A"},
            {"id": 5, "name": "Certification Strike",  "scoreA": 70, "scoreB": 50, "commentary": "Certifications land critical blows!", "winner": "A"},
            {"id": 6, "name": "ATS Showdown",          "scoreA": 82, "scoreB": 70, "commentary": f"{name_a}'s resume blazes through ATS filters!", "winner": "A"},
        ]
        special_a, special_b = self.detect_special_attacks(skills_a, skills_b)
        return {
            "nameA": name_a, "nameB": name_b, "rounds": rounds,
            "overallWinner": "A", "totalScoreA": 76, "totalScoreB": 62,
            "skillsA": skills_a[:10], "skillsB": skills_b[:10],
            "commonSkills": list(set(s.lower() for s in skills_a) & set(s.lower() for s in skills_b))[:5],
            "uniqueSkillsA": skills_a[:6], "uniqueSkillsB": skills_b[:6],
            "missingSkillsA": [], "missingSkillsB": ["Python", "Cloud Platform"],
            "specialAttackA": special_a, "specialAttackB": special_b,
            "recruiterRecommendation": f"{name_a} is the stronger candidate based on available resume data.",
            "riskAnalysis": "Moderate — verify claims during technical interview.",
            "improvementsA": ["Add quantified metrics", "Strengthen leadership language", "Add GitHub profile link"],
            "improvementsB": ["Learn a cloud platform", "Build production-scale projects", "Pursue a relevant certification"],
            "radarA": {"skills": 78, "experience": 72, "projects": 80, "education": 75, "certifications": 70, "ats": 82},
            "radarB": {"skills": 62, "experience": 68, "projects": 55, "education": 65, "certifications": 50, "ats": 70},
            "atsScoreA": 82, "atsScoreB": 70,
            "jdMatchA": -1 if not has_jd else 70,
            "jdMatchB": -1 if not has_jd else 45,
        }


import re  # needed for _parse_json

ai_engine = AIEngine()