"""
Resume Kombat AI — API Routers (combined)
battles · resumes · tournaments · analytics · health
"""

# ─────────────────────────────────────────────────────────────────────────────
# health.py
# ─────────────────────────────────────────────────────────────────────────────
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import uuid, time, json
from datetime import datetime
from typing import List, Optional

router_health = APIRouter()

@router_health.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat(), "service": "resume-kombat-api"}

@router_health.get("/ping")
async def ping():
    return {"pong": True}

# Export as health module
import types
health = types.ModuleType("health")
health.router = router_health


# ─────────────────────────────────────────────────────────────────────────────
# resumes.py  –  POST /api/v1/resumes/upload
# ─────────────────────────────────────────────────────────────────────────────
router_resumes = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt"}
MAX_FILE_SIZE_MB = 5

@router_resumes.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse a resume. Returns structured JSON + ATS score."""
    # Validate extension
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: .{ext}. Use PDF, DOCX, or TXT.")

    # Read content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(413, f"File too large. Max size: {MAX_FILE_SIZE_MB}MB")

    # Parse
    from services.parser import parser
    try:
        parsed = parser.parse_bytes(content, file.filename or "resume.txt")
        ats_score = parser.calc_ats_score(parsed, content.decode("utf-8", errors="replace"))
    except Exception as e:
        raise HTTPException(500, f"Parsing failed: {str(e)}")

    resume_id = uuid.uuid4()

    # Persist to DB (optional — skip if DB unavailable)
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO resumes (id, filename, raw_text, parsed_data, skills, ats_score)
                   VALUES ($1, $2, $3, $4, $5, $6)""",
                resume_id,
                file.filename,
                content.decode("utf-8", errors="replace")[:50000],
                json.dumps(parsed),
                parsed.get("skills", []),
                ats_score,
            )
    except Exception:
        pass  # Run without DB in dev mode

    return {
        "id": str(resume_id),
        "filename": file.filename,
        "parsed": parsed,
        "ats_score": ats_score,
        "created_at": datetime.utcnow().isoformat(),
    }


@router_resumes.get("/{resume_id}")
async def get_resume(resume_id: uuid.UUID):
    """Fetch a previously uploaded resume by ID."""
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM resumes WHERE id=$1", resume_id)
            if not row:
                raise HTTPException(404, "Resume not found")
            return dict(row)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "Database unavailable")

resumes = types.ModuleType("resumes")
resumes.router = router_resumes


# ─────────────────────────────────────────────────────────────────────────────
# battles.py  –  POST /api/v1/battles
# ─────────────────────────────────────────────────────────────────────────────
router_battles = APIRouter()

@router_battles.post("")
async def create_battle(
    resume_a_id: str,
    resume_b_id: str,
    jd_text: Optional[str] = None,
    mode: str = "standard",
):
    """
    Create a new battle from two previously uploaded resume IDs.
    Runs AI analysis and returns full battle result.
    """
    # Fetch resumes
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            row_a = await conn.fetchrow("SELECT * FROM resumes WHERE id=$1", uuid.UUID(resume_a_id))
            row_b = await conn.fetchrow("SELECT * FROM resumes WHERE id=$1", uuid.UUID(resume_b_id))
        if not row_a or not row_b:
            raise HTTPException(404, "One or both resume IDs not found")
        parsed_a = json.loads(row_a["parsed_data"])
        parsed_b = json.loads(row_b["parsed_data"])
        name_a = parsed_a.get("name") or f"Candidate A"
        name_b = parsed_b.get("name") or f"Candidate B"
        text_a = row_a["raw_text"]
        text_b = row_b["raw_text"]
        skills_a = row_a["skills"] or []
        skills_b = row_b["skills"] or []
    except HTTPException:
        raise
    except Exception as e:
        # Dev mode fallback: use placeholder text
        name_a, name_b = "Candidate A", "Candidate B"
        text_a = text_b = ""
        skills_a = skills_b = []

    # Run AI analysis
    from services.ai_engine import ai_engine
    battle_data = await ai_engine.run_battle(
        name_a, name_b, text_a, text_b, skills_a, skills_b, jd_text
    )

    battle_id = uuid.uuid4()

    # Persist
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO battles (id, resume_a_id, resume_b_id, winner, total_score_a, total_score_b, mode, battle_data)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""",
                battle_id,
                uuid.UUID(resume_a_id),
                uuid.UUID(resume_b_id),
                battle_data.get("overallWinner", "A"),
                battle_data.get("totalScoreA", 0),
                battle_data.get("totalScoreB", 0),
                mode,
                json.dumps(battle_data),
            )
            # Insert individual scores
            for r in battle_data.get("rounds", []):
                await conn.execute(
                    """INSERT INTO scores (battle_id, round_id, round_name, score_a, score_b, winner, commentary)
                       VALUES ($1,$2,$3,$4,$5,$6,$7)""",
                    battle_id, r["id"], r["name"],
                    r["scoreA"], r["scoreB"], r["winner"], r["commentary"],
                )
    except Exception:
        pass

    return {"id": str(battle_id), "created_at": datetime.utcnow().isoformat(), **battle_data}


@router_battles.get("/{battle_id}")
async def get_battle(battle_id: uuid.UUID):
    """Fetch a battle result by ID."""
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM battles WHERE id=$1", battle_id)
            if not row:
                raise HTTPException(404, "Battle not found")
            data = dict(row)
            data["battle_data"] = json.loads(data["battle_data"])
            return data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "Database unavailable")


@router_battles.get("")
async def list_battles(limit: int = Query(20, le=100), offset: int = 0):
    """List recent battles."""
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, winner, total_score_a, total_score_b, mode, created_at FROM battles ORDER BY created_at DESC LIMIT $1 OFFSET $2",
                limit, offset,
            )
            return [dict(r) for r in rows]
    except Exception:
        return []


@router_battles.post("/quick")
async def quick_battle(
    text_a: str,
    text_b: str,
    name_a: str = "Candidate A",
    name_b: str = "Candidate B",
    jd_text: Optional[str] = None,
):
    """Quick battle: pass resume text directly without prior upload."""
    from services.parser import parser
    from services.ai_engine import ai_engine
    parsed_a = parser.parse_text(text_a)
    parsed_b = parser.parse_text(text_b)
    result = await ai_engine.run_battle(
        parsed_a.get("name") or name_a,
        parsed_b.get("name") or name_b,
        text_a, text_b,
        parsed_a.get("skills", []),
        parsed_b.get("skills", []),
        jd_text,
    )
    return {"id": str(uuid.uuid4()), "created_at": datetime.utcnow().isoformat(), **result}

battles = types.ModuleType("battles")
battles.router = router_battles


# ─────────────────────────────────────────────────────────────────────────────
# tournaments.py
# ─────────────────────────────────────────────────────────────────────────────
router_tournaments = APIRouter()

@router_tournaments.post("")
async def create_tournament(resume_ids: List[str], jd_text: Optional[str] = None):
    """Run a knockout tournament for 4/8/16 resumes."""
    n = len(resume_ids)
    if n not in (4, 8, 16):
        raise HTTPException(400, "Tournament requires exactly 4, 8, or 16 resume IDs")

    # Fetch or use fallback
    fighters = []
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            for rid in resume_ids:
                row = await conn.fetchrow("SELECT raw_text, parsed_data FROM resumes WHERE id=$1", uuid.UUID(rid))
                if row:
                    parsed = json.loads(row["parsed_data"])
                    fighters.append({"name": parsed.get("name") or f"Fighter {len(fighters)+1}", "text": row["raw_text"]})
                else:
                    fighters.append({"name": f"Fighter {len(fighters)+1}", "text": ""})
    except Exception:
        fighters = [{"name": f"Fighter {i+1}", "text": ""} for i in range(n)]

    from services.ai_engine import ai_engine

    # Run bracket
    current_round = fighters[:]
    all_rounds = []
    round_names = ["Quarterfinals", "Round of 8", "Semifinals", "Final"]
    round_idx = 0

    while len(current_round) > 1:
        matches = []
        next_round = []
        for i in range(0, len(current_round), 2):
            fa = current_round[i]
            fb = current_round[i + 1] if i + 1 < len(current_round) else current_round[0]
            match = await ai_engine.run_tournament_match(fa["name"], fa["text"], fb["name"], fb["text"])
            matches.append(match)
            winner_name = match["winner"]
            winner_fighter = fa if winner_name == fa["name"] else fb
            next_round.append(winner_fighter)
        name = round_names[round_idx] if round_idx < len(round_names) else f"Round {round_idx+1}"
        all_rounds.append({"round_name": name, "matches": matches})
        current_round = next_round
        round_idx += 1

    champion = current_round[0]["name"] if current_round else "Unknown"
    tourney_id = uuid.uuid4()

    result = {
        "id": str(tourney_id),
        "size": n,
        "rounds": all_rounds,
        "champion": champion,
        "champion_score": 89,
        "champion_reason": f"{champion} demonstrated the strongest combination of technical skills and experience throughout all rounds.",
        "created_at": datetime.utcnow().isoformat(),
    }

    # Persist
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO tournaments (id, size, bracket_data, champion, champion_score, champion_reason) VALUES ($1,$2,$3,$4,$5,$6)",
                tourney_id, n, json.dumps(all_rounds), champion, 89, result["champion_reason"],
            )
    except Exception:
        pass

    return result


@router_tournaments.get("/{tournament_id}")
async def get_tournament(tournament_id: uuid.UUID):
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tournaments WHERE id=$1", tournament_id)
            if not row:
                raise HTTPException(404, "Tournament not found")
            data = dict(row)
            data["bracket_data"] = json.loads(data["bracket_data"])
            return data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "Database unavailable")

tournaments = types.ModuleType("tournaments")
tournaments.router = router_tournaments


# ─────────────────────────────────────────────────────────────────────────────
# analytics.py
# ─────────────────────────────────────────────────────────────────────────────
router_analytics = APIRouter()

@router_analytics.get("/{battle_id}")
async def get_analytics(battle_id: uuid.UUID):
    """Return deep analytics for a completed battle."""
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            battle = await conn.fetchrow("SELECT battle_data FROM battles WHERE id=$1", battle_id)
            if not battle:
                raise HTTPException(404, "Battle not found")
            data = json.loads(battle["battle_data"])

            # Build analytics payload
            analytics = {
                "battle_id": str(battle_id),
                "category_comparison": {
                    r["name"]: {"a": r["scoreA"], "b": r["scoreB"], "winner": r["winner"]}
                    for r in data.get("rounds", [])
                },
                "skill_overlap": {
                    "skills_a": data.get("skillsA", []),
                    "skills_b": data.get("skillsB", []),
                    "common": data.get("commonSkills", []),
                    "unique_a": data.get("uniqueSkillsA", []),
                    "unique_b": data.get("uniqueSkillsB", []),
                    "missing_a": data.get("missingSkillsA", []),
                    "missing_b": data.get("missingSkillsB", []),
                },
                "ats_breakdown": {
                    "score_a": data.get("atsScoreA", 0),
                    "score_b": data.get("atsScoreB", 0),
                },
                "radar": {
                    "a": data.get("radarA", {}),
                    "b": data.get("radarB", {}),
                },
                "jd_match": {
                    "a": data.get("jdMatchA", -1),
                    "b": data.get("jdMatchB", -1),
                } if data.get("jdMatchA", -1) >= 0 else None,
            }
            return analytics
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "Database unavailable")


@router_analytics.get("")
async def analytics_summary(limit: int = 10):
    """Aggregate analytics across recent battles."""
    try:
        from db.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT winner, total_score_a, total_score_b, created_at FROM battles ORDER BY created_at DESC LIMIT $1",
                limit,
            )
            battles = [dict(r) for r in rows]
            a_wins = sum(1 for b in battles if b["winner"] == "A")
            avg_a = sum(b["total_score_a"] or 0 for b in battles) / max(len(battles), 1)
            avg_b = sum(b["total_score_b"] or 0 for b in battles) / max(len(battles), 1)
            return {
                "total_battles": len(battles),
                "a_wins": a_wins,
                "b_wins": len(battles) - a_wins,
                "avg_score_a": round(avg_a, 1),
                "avg_score_b": round(avg_b, 1),
            }
    except Exception:
        return {"total_battles": 0, "a_wins": 0, "b_wins": 0, "avg_score_a": 0, "avg_score_b": 0}

analytics = types.ModuleType("analytics")
analytics.router = router_analytics