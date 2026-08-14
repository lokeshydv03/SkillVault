import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.deps import get_llm_provider
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import SkillVaultException
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.database import AsyncSessionLocal, engine
from app.db.repositories.skill_repository import SkillRepository
from app.services.embedding_service import EmbeddingService
from app.services.skill_service import SkillService

setup_logging()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Try enabling pgvector extension in isolated connection
    try:
        async with engine.connect() as conn:
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                await conn.commit()
            except Exception:
                pass
    except Exception:
        pass

    # Column auto-migration for existing SQLite/PostgreSQL instances
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE skills ADD COLUMN quality_score FLOAT DEFAULT 0.0;"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE skills ADD COLUMN quality_components JSON DEFAULT '{}';"))
        except Exception:
            pass

    # Initialize DB schema in fresh transaction block
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed built-in skills idempotently with the active LLM Provider
    async with AsyncSessionLocal() as session:
        skill_repo = SkillRepository(session)
        llm_provider = get_llm_provider()
        emb_service = EmbeddingService(llm_provider)
        skill_service = SkillService(skill_repo, emb_service)
        await skill_service.seed_builtin_skills()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SkillVaultException)
async def skillvault_exception_handler(request, exc: SkillVaultException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_code": exc.__class__.__name__},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_code": exc.__class__.__name__},
    )


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "version": settings.VERSION,
    }
