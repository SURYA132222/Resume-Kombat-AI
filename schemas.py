"""
Resume Kombat AI — Pydantic Models / Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


# ── Enums ─────────────────────────────────────────────────────────────────────
class BattleWinner(str, Enum):
    A = "A"
    B = "B"
    TIE = "TIE"


class BattleMode(str, Enum):
    STANDARD = "standard"
    JD_MATCHING = "jd_matching"
    GITHUB = "github"


class TournamentSize(int, Enum):
    FOUR = 4
    EIGHT = 8
    SIXTEEN = 16


# ── Resume Schemas ─────────────────────────────────────────────────────────────
class ResumeUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    parsed: ParsedResume
    ats_score: int
    created_at: datetime


class ParsedResume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    summary: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    total_years_experience: float = 0.0
    seniority_level: str = "junior"


class ExperienceItem(BaseModel):
    company: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    duration_months: int = 0
    bullets: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class ProjectItem(BaseModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)
    url: str = ""
    github_url: str = ""
    stars: int = 0


# ── Battle Schemas ─────────────────────────────────────────────────────────────
class BattleCreateRequest(BaseModel):
    resume_a_id: uuid.UUID
    resume_b_id: uuid.UUID
    jd_id: Optional[uuid.UUID] = None
    mode: BattleMode = BattleMode.STANDARD

    class Config:
        use_enum_values = True


class RoundResult(BaseModel):
    round_id: int
    round_name: str
    score_a: int = Field(ge=0, le=100)
    score_b: int = Field(ge=0, le=100)
    winner: BattleWinner
    commentary: str
    weight: float


class SpecialAttack(BaseModel):
    triggered: bool
    name: str = ""
    skills: List[str] = Field(default_factory=list)
    candidate: str = ""


class RadarData(BaseModel):
    skills: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    projects: int = Field(ge=0, le=100)
    education: int = Field(ge=0, le=100)
    certifications: int = Field(ge=0, le=100)
    ats: int = Field(ge=0, le=100)


class BattleResult(BaseModel):
    id: uuid.UUID
    name_a: str
    name_b: str
    rounds: List[RoundResult]
    overall_winner: BattleWinner
    total_score_a: int
    total_score_b: int
    skills_a: List[str] = Field(default_factory=list)
    skills_b: List[str] = Field(default_factory=list)
    common_skills: List[str] = Field(default_factory=list)
    unique_skills_a: List[str] = Field(default_factory=list)
    unique_skills_b: List[str] = Field(default_factory=list)
    missing_skills_a: List[str] = Field(default_factory=list)
    missing_skills_b: List[str] = Field(default_factory=list)
    special_attack_a: SpecialAttack
    special_attack_b: SpecialAttack
    recruiter_recommendation: str
    risk_analysis: str
    improvements_a: List[str] = Field(default_factory=list)
    improvements_b: List[str] = Field(default_factory=list)
    radar_a: RadarData
    radar_b: RadarData
    ats_score_a: int = Field(ge=0, le=100)
    ats_score_b: int = Field(ge=0, le=100)
    jd_match_a: int = Field(default=-1, ge=-1, le=100)
    jd_match_b: int = Field(default=-1, ge=-1, le=100)
    mode: BattleMode
    created_at: datetime


# ── Job Description Schemas ────────────────────────────────────────────────────
class JobDescriptionCreate(BaseModel):
    title: str = ""
    raw_text: str

    @validator("raw_text")
    def validate_text(cls, v):
        if len(v.strip()) < 20:
            raise ValueError("Job description must be at least 20 characters")
        return v.strip()


class JobDescriptionResponse(BaseModel):
    id: uuid.UUID
    title: str
    raw_text: str
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    required_experience_years: Optional[int] = None
    created_at: datetime


# ── Tournament Schemas ─────────────────────────────────────────────────────────
class TournamentCreateRequest(BaseModel):
    resume_ids: List[uuid.UUID]
    jd_id: Optional[uuid.UUID] = None

    @validator("resume_ids")
    def validate_size(cls, v):
        if len(v) not in (4, 8, 16):
            raise ValueError("Tournament requires exactly 4, 8, or 16 resumes")
        return v


class BracketMatch(BaseModel):
    match_id: int
    fighter_a: str
    fighter_b: str
    score_a: int
    score_b: int
    winner: str
    commentary: str


class BracketRound(BaseModel):
    round_name: str
    matches: List[BracketMatch]


class TournamentResult(BaseModel):
    id: uuid.UUID
    size: int
    rounds: List[BracketRound]
    champion: str
    champion_score: int
    champion_reason: str
    created_at: datetime


# ── Analytics Schemas ──────────────────────────────────────────────────────────
class AnalyticsResponse(BaseModel):
    battle_id: uuid.UUID
    category_comparison: Dict[str, Any] = Field(default_factory=dict)
    skill_overlap: Dict[str, Any] = Field(default_factory=dict)
    ats_breakdown: Dict[str, Any] = Field(default_factory=dict)
    keyword_density: Dict[str, Any] = Field(default_factory=dict)
    timeline: Dict[str, Any] = Field(default_factory=dict)
    jd_match: Optional[Dict[str, Any]] = None


# ── Error Schemas ──────────────────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None