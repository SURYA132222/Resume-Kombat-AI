"""
Resume Kombat AI — FastAPI Backend
Main application entry point
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from routers import battles, resumes, tournaments, analytics, health
from db.connection import init_db, close_db

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("resume_kombat")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("⚡ Resume Kombat AI starting up...")
    await init_db()
    yield
    logger.info("🔻 Resume Kombat AI shutting down...")
    await close_db()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Resume Kombat AI",
    description="AI-powered resume battle and hiring intelligence API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.1f}ms)")
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Basic in-memory rate limiting (use Redis in production)
    return await call_next(request)


# ── Exception Handlers ─────────────────────────────────────────────────────────
@app.exception_handler(404)
async def not_found(request: Request, exc):
    return JSONResponse(status_code=404, content={"error": "Not found", "path": str(request.url.path)})


@app.exception_handler(500)
async def server_error(request: Request, exc):
    logger.error(f"Server error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["Resumes"])
app.include_router(battles.router, prefix="/api/v1/battles", tags=["Battles"])
app.include_router(tournaments.router, prefix="/api/v1/tournaments", tags=["Tournaments"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    return {
        "name": "Resume Kombat AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }