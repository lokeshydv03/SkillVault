import asyncio
import json
import os
import sys

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.api.deps import get_llm_provider
from app.db.base import Base
from app.db.repositories.execution_repository import ExecutionRepository
from app.db.repositories.skill_repository import SkillRepository
from app.db.repositories.task_repository import TaskRepository
from app.services.embedding_service import EmbeddingService
from app.services.execution_service import ExecutionService
from app.services.generation_service import GenerationService
from app.services.retrieval_service import RetrievalService
from app.services.skill_metrics_service import SkillMetricsService
from app.services.skill_service import SkillService
from app.services.task_service import TaskService
from app.skills.executor import LocalSkillExecutor
from app.core.config import settings


async def run_demo():
    print("=" * 80)
    print("      SKILLVAULT PHASE 1 — DYNAMIC SKILL GENERATION ENGINE DEMO           ")
    print("=" * 80)

    demo_db_file = "skillvault_demo.db"
    demo_db_url = settings.DATABASE_URL
    if demo_db_url.startswith("postgresql://"):
        demo_db_url = demo_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    try:
        engine = create_async_engine(demo_db_url, echo=False)
        async with engine.connect() as conn:
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                await conn.commit()
            except Exception:
                pass
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Notice: PostgreSQL unavailable ({e}). Using isolated SQLite demo database.")
        demo_db_url = "sqlite+aiosqlite:///skillvault_demo.db"
        engine = create_async_engine(demo_db_url, echo=False, connect_args={"timeout": 30})
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    DemoSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with DemoSessionLocal() as session:
            llm = get_llm_provider()

            task_repo = TaskRepository(session)
            skill_repo = SkillRepository(session)
            exec_repo = ExecutionRepository(session)

            emb_service = EmbeddingService(llm)
            gen_service = GenerationService(llm)
            ret_service = RetrievalService(skill_repo, emb_service)
            skill_service = SkillService(skill_repo, emb_service)
            metrics_service = SkillMetricsService(skill_repo)
            exec_service = ExecutionService(exec_repo, metrics_service, LocalSkillExecutor())

            task_service = TaskService(
                task_repo=task_repo,
                execution_repo=exec_repo,
                generation_service=gen_service,
                retrieval_service=ret_service,
                skill_service=skill_service,
                execution_service=exec_service,
            )

            # Seed initial capabilities
            await skill_service.seed_builtin_skills()
            print("[Step 1] Initialized Vault with Built-in Skills.")

            # --- PART 1: REUSE DECISION ---
            print("\n" + "-" * 80)
            print("PART 1: SUBMIT TASK MATCHING EXISTING SKILL")
            print("Task: 'Analyze employees.csv and calculate average salary.'")
            print("-" * 80)
            res1 = await task_service.create_and_execute_task(
                "Analyze employees.csv and calculate average salary."
            )
            print(f"-> Strategy: {res1.strategy.upper()}")
            print(f"-> Selected Skill: {res1.skill.get('name') if res1.skill else 'None'}")
            print(f"-> Execution Status: {res1.status.upper()}")

            # --- PART 2: GENERATE DECISION ---
            print("\n" + "-" * 80)
            print("PART 2: SUBMIT TASK WITH MISSING CAPABILITY")
            print("Task: 'Generate interactive 3D SVG rendering chart from financial matrix.'")
            print("-" * 80)
            res2 = await task_service.create_and_execute_task(
                "Generate interactive 3D SVG rendering chart from financial matrix."
            )
            print(f"-> Strategy: {res2.strategy.upper()}")
            print(f"-> Generated Skill Name: {res2.skill.get('name') if res2.skill else 'None'}")
            print(f"-> Skill Status in DB: {res2.skill.get('status') if res2.skill else 'None'}")
            print(f"-> Source Type: {res2.skill.get('source_type') if res2.skill else 'None'}")
            
            # Retrieve DB skill record to demonstrate full persistence
            if res2.skill and res2.skill.get("skill_id"):
                db_skill = await skill_service.get_skill(res2.skill["skill_id"])
                print(f"-> DB Verification: ID={db_skill.id}, Slug={db_skill.slug}, Risk={db_skill.risk_level}")
                print(f"-> Generated Input Schema: {json.dumps(db_skill.input_schema)}")
                print(f"-> Generated Dependencies: {db_skill.dependencies}")

            print("\n" + "-" * 80)
            print("PART 3: SECURITY BOUNDARY & EXECUTION CHECK")
            print("-" * 80)
            print("Code execution:")
            print("SKIPPED — sandbox not implemented yet")
            print(f"Task Execution Result Status: {res2.execution.get('status') if res2.execution else 'NOT_EXECUTED'}")
            print(f"Notice: {res2.result.get('notice') if res2.result else ''}")

            print("\n" + "=" * 80)
            print("             SKILL GENERATION ENGINE DEMO COMPLETED              ")
            print("=" * 80)

    finally:
        await engine.dispose()
        if os.path.exists(demo_db_file):
            try:
                os.remove(demo_db_file)
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(run_demo())
