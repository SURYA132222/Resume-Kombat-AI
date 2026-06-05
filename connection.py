"""
Resume Kombat AI — Database Connection
Async PostgreSQL via asyncpg + connection pooling
"""

import logging
import os
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://rk_user:rk_password@localhost:5432/resume_kombat"
)


async def init_db() -> None:
    global _pool
    try:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
        logger.info("✅ Database pool created")
        await _run_migrations()
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("Running without database — results won't be persisted")


async def close_db() -> None:
    global _pool
    if _pool:
        await _pool.close()
        logger.info("Database pool closed")


async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database not initialized")
    return _pool


async def _run_migrations() -> None:
    """Run schema migrations on startup"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(SCHEMA_SQL)
    logger.info("✅ Migrations applied")


# ── Schema SQL ─────────────────────────────────────────────────────────────────
SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS resumes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename    TEXT,
    raw_text    TEXT NOT NULL,
    parsed_data JSONB,
    skills      TEXT[],
    ats_score   INT DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_descriptions (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title                    TEXT DEFAULT '',
    raw_text                 TEXT NOT NULL,
    required_skills          TEXT[],
    nice_to_have_skills      TEXT[],
    required_experience_years INT,
    created_at               TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS battles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_a_id     UUID REFERENCES resumes(id) ON DELETE SET NULL,
    resume_b_id     UUID REFERENCES resumes(id) ON DELETE SET NULL,
    jd_id           UUID REFERENCES job_descriptions(id) ON DELETE SET NULL,
    winner          CHAR(1) CHECK (winner IN ('A','B','T')),
    total_score_a   INT,
    total_score_b   INT,
    mode            TEXT DEFAULT 'standard',
    battle_data     JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scores (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    battle_id   UUID REFERENCES battles(id) ON DELETE CASCADE,
    round_id    INT NOT NULL,
    round_name  TEXT NOT NULL,
    score_a     INT NOT NULL,
    score_b     INT NOT NULL,
    winner      CHAR(1),
    commentary  TEXT,
    weight      NUMERIC(4,2) DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS tournaments (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    size           INT NOT NULL CHECK (size IN (4,8,16)),
    bracket_data   JSONB,
    champion       TEXT,
    champion_score INT,
    champion_reason TEXT,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS battle_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  TEXT,
    battle_id   UUID REFERENCES battles(id) ON DELETE CASCADE,
    viewed_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analytics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    battle_id       UUID REFERENCES battles(id) ON DELETE CASCADE UNIQUE,
    skill_overlap   JSONB,
    ats_breakdown   JSONB,
    keyword_density JSONB,
    radar_data      JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_battles_created   ON battles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scores_battle     ON scores(battle_id);
CREATE INDEX IF NOT EXISTS idx_resumes_created   ON resumes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_battle  ON analytics(battle_id);
"""