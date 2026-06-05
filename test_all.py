"""
Resume Kombat AI — Test Suite
"""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


# ── Parser Tests ──────────────────────────────────────────────────────────────
class TestResumeParser:
    def setup_method(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from services.parser import ResumeParser
        self.parser = ResumeParser()

    def test_extract_email(self):
        text = "John Doe\njohn.doe@example.com\n+1 555-1234"
        result = self.parser.parse_text(text)
        assert result["email"] == "john.doe@example.com"

    def test_extract_phone(self):
        text = "Jane Smith\njane@test.com\n(555) 123-4567"
        result = self.parser.parse_text(text)
        assert "555" in result["phone"]

    def test_extract_skills_python(self):
        text = "Skills: Python, React, PostgreSQL, Docker, Kubernetes"
        result = self.parser.parse_text(text)
        skill_lower = [s.lower() for s in result["skills"]]
        assert "python" in skill_lower

    def test_extract_linkedin(self):
        text = "linkedin.com/in/johndoe Profile"
        result = self.parser.parse_text(text)
        assert "linkedin" in result["linkedin"].lower()

    def test_ats_score_range(self):
        text = "Alice Chen\nalice@email.com\n+1-555-0000\nSkills: Python AWS Docker\nExperience:\n• Led migration improving performance 40%\nEducation: MIT CS 2019"
        parsed = self.parser.parse_text(text)
        score = self.parser.calc_ats_score(parsed, text)
        assert 0 <= score <= 100

    def test_empty_text(self):
        result = self.parser.parse_text("")
        assert result["name"] == ""
        assert result["skills"] == []

    def test_seniority_detection(self):
        text = "Senior Software Engineer at Google\n8 years experience"
        result = self.parser.parse_text(text)
        assert result["seniority_level"] in ("senior", "mid", "lead")

    def test_skills_dedup(self):
        text = "Python python PYTHON React react"
        result = self.parser.parse_text(text)
        lower_skills = [s.lower() for s in result["skills"]]
        assert lower_skills.count("python") <= 1


# ── AI Engine Tests ────────────────────────────────────────────────────────────
class TestAIEngine:
    def setup_method(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from services.ai_engine import AIEngine
        self.engine = AIEngine()

    def test_detect_cloud_strike(self):
        skills_a = ["AWS", "Kubernetes", "Terraform", "Python"]
        skills_b = ["React", "Node.js"]
        special_a, special_b = self.engine.detect_special_attacks(skills_a, skills_b)
        assert special_a["triggered"] is True
        assert special_a["name"] == "Cloud Strike"
        assert special_b["triggered"] is False

    def test_detect_fullstack_fury(self):
        skills = ["React", "Node.js", "MongoDB", "Express"]
        special, _ = self.engine.detect_special_attacks(skills, [])
        assert special["triggered"] is True
        assert "Full Stack" in special["name"]

    def test_detect_ai_combo(self):
        skills = ["Python", "TensorFlow", "PyTorch"]
        special, _ = self.engine.detect_special_attacks(skills, [])
        assert special["triggered"] is True

    def test_no_special_attack(self):
        skills = ["HTML", "CSS", "jQuery"]
        special, _ = self.engine.detect_special_attacks(skills, [])
        assert special["triggered"] is False

    def test_fallback_battle(self):
        result = self.engine._fallback_battle("A", "B", ["Python"], ["JS"], False)
        assert "rounds" in result
        assert len(result["rounds"]) == 6
        assert result["overallWinner"] in ("A", "B")
        assert 0 <= result["totalScoreA"] <= 100

    def test_parse_json_strips_fences(self):
        raw = '```json\n{"key": "value"}\n```'
        result = self.engine._parse_json(raw)
        assert result["key"] == "value"

    def test_parse_json_finds_braces(self):
        raw = 'Some text before {"key": 42} and after'
        result = self.engine._parse_json(raw)
        assert result["key"] == 42

    @pytest.mark.asyncio
    async def test_run_battle_fallback_no_api(self):
        """Should return fallback result when API key not set"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}):
            result = await self.engine.run_battle("Alice", "Bob", "text a", "text b", ["Python"], ["JS"])
        assert "rounds" in result
        assert len(result["rounds"]) == 6


# ── Router Tests ───────────────────────────────────────────────────────────────
class TestRouters:
    def setup_method(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        from routers import health
        response = await health.router.routes[0].endpoint()
        assert response["status"] == "ok"

    @pytest.mark.asyncio
    async def test_quick_battle_endpoint(self):
        from routers import battles
        with patch("services.ai_engine.ai_engine.run_battle") as mock_battle:
            mock_battle.return_value = {
                "nameA": "Alice", "nameB": "Bob",
                "rounds": [{"id":1,"name":"Skills Clash","scoreA":80,"scoreB":60,"commentary":"...","winner":"A"}]*6,
                "overallWinner": "A", "totalScoreA": 78, "totalScoreB": 60,
                "skillsA": [], "skillsB": [], "commonSkills": [],
                "uniqueSkillsA": [], "uniqueSkillsB": [],
                "missingSkillsA": [], "missingSkillsB": [],
                "specialAttackA": {"triggered": False, "name": "", "skills": []},
                "specialAttackB": {"triggered": False, "name": "", "skills": []},
                "recruiterRecommendation": "Hire Alice.",
                "riskAnalysis": "Low risk.",
                "improvementsA": [], "improvementsB": [],
                "radarA": {"skills":80,"experience":78,"projects":80,"education":75,"certifications":70,"ats":82},
                "radarB": {"skills":60,"experience":65,"projects":55,"education":60,"certifications":50,"ats":70},
                "atsScoreA": 82, "atsScoreB": 70, "jdMatchA": -1, "jdMatchB": -1,
            }
            # Find the quick battle endpoint
            endpoint = next(r for r in battles.router.routes if "quick" in str(r.path))
            assert endpoint is not None


# ── Integration Tests ──────────────────────────────────────────────────────────
class TestIntegration:

    def test_full_parse_and_score(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from services.parser import ResumeParser
        p = ResumeParser()

        resume = """Alice Chen
alice@email.com
+1-555-0000
linkedin.com/in/alicechen
github.com/alicechen

SKILLS
Python, TypeScript, React, AWS, Docker, Kubernetes, PostgreSQL, TensorFlow

EXPERIENCE
Senior Engineer — TechCorp (2021–2024)
• Led migration to microservices, 40% latency reduction
• Built ML pipeline processing 5M events/day

Engineer — CloudStartup (2019–2021)
• Designed GraphQL API serving 2M DAU

EDUCATION
B.S. Computer Science — MIT, 2019, GPA 3.9

PROJECTS
ML Library — github.com/alicechen/ml-lib — 1,200 stars
Kubernetes operator for auto-scaling

CERTIFICATIONS
AWS Solutions Architect Professional
Google Cloud Professional Data Engineer"""

        parsed = p.parse_text(resume)
        ats = p.calc_ats_score(parsed, resume)

        assert parsed["email"] == "alice@email.com"
        assert len(parsed["skills"]) >= 3
        assert ats >= 40
        assert parsed["seniority_level"] in ("senior", "mid", "lead")

    @pytest.mark.asyncio
    async def test_ai_engine_special_detection_integration(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from services.ai_engine import AIEngine
        engine = AIEngine()

        skills_cloud = ["AWS", "Kubernetes", "Terraform", "Python", "Go"]
        skills_basic = ["HTML", "CSS", "JavaScript"]

        sa, sb = engine.detect_special_attacks(skills_cloud, skills_basic)
        assert sa["triggered"]
        assert not sb["triggered"]
        assert sa["name"] == "Cloud Strike"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])